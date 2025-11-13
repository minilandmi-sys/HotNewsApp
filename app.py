import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time
from io import BytesIO
import requests 
from PIL import Image, ImageDraw, ImageFont 

# ================= LLM API 設定 (已轉換為 Gemini) =================
GEMINI_MODEL = "gemini-2.5-flash" 
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# 嘗試讀取 GEMINI API 金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ 錯誤：請在 Streamlit Secrets 中設定 **GEMINI_API_KEY**！")
    API_KEY = ""

# 5 個網站的 RSS (已加入 The Femin)
RSS_FEEDS = {
    "妞新聞": "https://www.niusnews.com/feed",
    "Women's Health TW": "https://www.womenshealthmag.com/tw/rss/all.xml",
    "BEAUTY美人圈": "https://www.beauty321.com/feed_pin",
    "A Day Magazine": "https://www.adaymag.com/feed",
    "The Femin": "https://thefemin.com/category/editorial/issue/feed" # 新增的 RSS 來源
}

# ================= 輔助函式 (原有的 RSS 處理) =================

def parse_entries(entries):
    parsed_list = []
    for entry in entries:
        published_time = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_time = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published_time = datetime(*entry.updated_parsed[:6])
        if not published_time:
            published_time = datetime.now()

        parsed_list.append({
            "標題": entry.title if "title" in entry else "(無標題)",
            "連結": entry.link if "link" in entry else "",
            "發佈時間": published_time.strftime("%Y-%m-%d %H:%M"),
            "來源": ""
        })
    return parsed_list

def fetch_top5_each_site():
    all_entries = []
    for site, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries:
            continue

        entries = parse_entries(feed.entries)
        entries_sorted = entries[:5]
        for item in entries_sorted:
            item["來源"] = site
        all_entries.extend(entries_sorted)

        time.sleep(1)

    all_entries.sort(key=lambda x: x["發佈時間"], reverse=True)
    return pd.DataFrame(all_entries)

# ================= 模組 2：視覺內容生成 (Pillow 實現) =================

# 根據您的檔案結構截圖，路徑修正為 ".devcontainer/NotoSansTC-Bold.ttf"
FONT_FILE_PATH = ".devcontainer/NotoSansTC-Bold.ttf" 

def get_font(size, bold=False):
    """
    嘗試載入明確指定的 CJK 字型檔案。
    """
    try:
        # 強制使用上傳的字型檔路徑
        return ImageFont.truetype(FONT_FILE_PATH, size)
    except IOError:
        # 如果找不到指定檔案，則退回預設字型並發出警告
        st.warning(f"⚠️ 嚴重警告：找不到字型檔案 '{FONT_FILE_PATH}'。請確認檔案已上傳至應用程式根目錄。")
        return ImageFont.load_default()

def generate_visual_content(title, ratio='1:1', uploaded_file=None):
    """
    使用 Pillow 函式庫，在伺服器端生成帶有文章標題的圖片模板。
    Args:
        title (str): 文章標題。
        ratio (str): 圖片比例 ('1:1' 或 '4:3')。
        uploaded_file (Optional): 上傳的背景圖片檔案。
    """
    # 定義尺寸 (1000px max dimension)
    MAX_DIM = 1000
    if ratio == '4:3': # 3:4 直式版型 (750x1000)
        WIDTH = int(MAX_DIM * 3 / 4) # 750
        HEIGHT = MAX_DIM # 1000
    else: # 1:1 (1000x1000)
        WIDTH = MAX_DIM # 1000
        HEIGHT = MAX_DIM # 1000
    
    # 1. 載入背景圖或建立基礎圖
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            
            # --- START: 新增圖片置中裁剪邏輯以保持比例 ---
            # 獲取上傳圖片的長寬
            img_width, img_height = img.size
            # 計算目標模板的長寬比 (Target Aspect Ratio)
            target_ratio = WIDTH / HEIGHT
            
            # 判斷是寬度過度還是高度過度
            if img_width / img_height > target_ratio:
                # 圖片太寬，按高度縮放，寬度裁剪
                new_height = HEIGHT
                new_width = int(img_width * (HEIGHT / img_height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 置中裁剪
                left = (new_width - WIDTH) / 2
                top = 0
                right = left + WIDTH
                bottom = HEIGHT
            else:
                # 圖片太高，按寬度縮放，高度裁剪
                new_width = WIDTH
                new_height = int(img_height * (WIDTH / img_width))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 置中裁剪
                left = 0
                top = (new_height - HEIGHT) / 2
                right = WIDTH
                bottom = top + HEIGHT
            
            img = img.crop((int(left), int(top), int(right), int(bottom)))
            # --- END: 新增圖片置中裁剪邏輯以保持比例 ---
            
        except Exception:
            img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')
    else:
        img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')


    # --- 2. 新增底部半透明黑色遮罩 (Overlay) ---
    # 調整：黑底總高度為 15%，但整個區塊上移，使底部留出 10% 的空白。
    OVERLAY_HEIGHT_RATIO = 0.15 # 黑底高度為 15%
    BOTTOM_GAP_RATIO = 0.10 # 底部留白 10%
    
    # 遮罩結束 Y 座標：距離底部 10%
    OVERLAY_END_Y = int(HEIGHT * (1.0 - BOTTOM_GAP_RATIO)) # 90%
    # 遮罩起始 Y 座標：從結束點向上減去 15% 的高度
    OVERLAY_START_Y = int(HEIGHT * (1.0 - BOTTOM_GAP_RATIO - OVERLAY_HEIGHT_RATIO)) # 90% - 15% = 75%
    
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    opacity = 180 
    # 使用新的起始和結束 Y 座標繪製遮罩
    overlay_draw.rectangle([0, OVERLAY_START_Y, WIDTH, OVERLAY_END_Y], fill=(0, 0, 0, opacity))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img) 

    # --- 3. 繪製文章標題 (置中靠下，在遮罩上) ---
    
    article_to_display = title or "請輸入文章標題以跟風熱點..."
    
    # 字型大小為 40
    ARTICLE_FONT_SIZE = 40 
    
    article_font = get_font(ARTICLE_FONT_SIZE, bold=True) 
    
    # 實現多行自動換行
    CHAR_LIMIT = 24 if WIDTH < 1000 else 36 
    
    # --- 支援 st.text_area 輸入的換行符號 ---
    final_lines = []
    user_defined_lines = article_to_display.split('\n')
    
    for user_line in user_defined_lines:
        current_line = ""
        
        # 對每一行應用自動換行邏輯 (防止單行過長)
        for char in user_line:
            if len(current_line) < CHAR_LIMIT:
                current_line += char
            else:
                # 達到 CHAR_LIMIT，強制換行
                final_lines.append(current_line)
                current_line = char
        
        # 確保行尾的剩餘文字被加入
        if current_line:
            final_lines.append(current_line)

    # 移除空行並清理
    lines = [line.strip() for line in final_lines if line.strip()] 
    # --- 結束修正 ---

    # 定位：將文字區塊垂直置中於新的遮罩區塊內
    # 調整行距，使文字更寬鬆一點 (1.3 倍)
    line_height = ARTICLE_FONT_SIZE * 1.3 
    total_text_height = len(lines) * line_height

    # 計算新遮罩區塊的垂直中心點 (75% to 90%)
    Y_OVERLAY_CENTER = (OVERLAY_START_Y + OVERLAY_END_Y) / 2
    
    # 計算文字區塊的起始 Y 座標，使其中心點對齊遮罩中心點
    # y_start 是整個文字區塊的頂部
    y_start = Y_OVERLAY_CENTER - (total_text_height / 2) 

    # 繪製
    for i, line in enumerate(lines):
        draw.text((WIDTH / 2, y_start + i * line_height), 
                  line, 
                  fill="#ffffff", # 硬編碼為白色 (原預設值)
                  font=article_font, 
                  anchor="mt") # anchor="mt" ensures horizontal center alignment

    # 底部版權標示部分已依照原碼註解/移除，保持不變
    
    return img

# ================= 模組 3：AI 文案優化邏輯 (使用 Gemini API) =================
# 此處邏輯與功能正常，保持不變

def generate_ai_copy(article_title): 
    """
    使用 Gemini API 生成 3 份針對社群貼文優化的標題，僅依賴文章標題。
    """
    if not API_KEY:
        return "API 金鑰未設定，無法呼叫 Gemini API。"
        
    if not article_title: 
        return None

    # 系統指令：設定為機智的台灣社群編輯
    system_prompt = "Act as a witty Taiwanese social media editor (社群小編). Your output must be in Traditional Chinese. Based on the article title provided by the user, generate 3 different, highly engaging, and clickable article titles/headlines ( suitable for a blog or social media post). Each title should be concise and separated by a single line break. Format your response using Markdown bullet points (*), NOT numbered lists."
            
    # 查詢內容：僅使用文章標題
    user_query = f"請根據以下資訊生成 3 份優化的社群標題:\n\n文章標題 (核心資訊): {article_title}"

    headers = {
        "Content-Type": "application/json",
    }
    
    # 構建 Gemini API 的 Payload
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "config": {
            "maxOutputTokens": 500,
            "temperature": 0.7
        }
    }

    try:
        # 發起 API 呼叫
        response = requests.post(
            f"{GEMINI_API_URL}?key={API_KEY}", 
            headers=headers, 
            json=payload
        )
        response.raise_for_status() 

        result = response.json()
        
        # 檢查並提取生成的文本
        if result and 'candidates' in result and len(result['candidates']) > 0 and 'parts' in result['candidates'][0]['content']:
            text = result['candidates'][0]['content']['parts'][0].text
            return text.strip()
        else:
            st.error("⚠️ Gemini API 回傳格式錯誤或無內容。")
            return "API 回應解析失敗。"

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Gemini API 呼叫失敗: {e}")
        st.write(f"API 回應狀態碼: {response.status_code if 'response' in locals() else 'N/A'}")
        return "API 呼叫失敗。"
    except Exception as e:
        st.error(f"⚠️ 發生未知錯誤：{e}")
        return "未知錯誤。"


# ================= Streamlit UI (主程式) =================

st.title("📰 熱門新聞報表工具 (RSS)")

# 報表產生區
if st.button("📊 產生最新報表"):
    df = fetch_top5_each_site()
    st.session_state.df = df 
    
    if df.empty:
        st.warning("⚠️ 沒有抓到任何文章。")
    else:
        st.success("✅ 報表已產生！")
        st.dataframe(df)

        # 轉換為 Excel 並下載
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()

        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}_HotNews.xlsx"

        st.download_button(
            label="⬇️ 下載 Excel 報表",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()


# ================= 社群內容加速器 (新增模組) =================
st.markdown("---")
st.header("🚀 社群內容加速器")
st.markdown("使用熱點文章標題，快速製作圖片視覺與優化標題！") 

# --- 文章標題狀態管理回呼函式 ---
def update_editable_title():
    selected = st.session_state.title_select
    if selected != "--- 請選擇熱點文章 ---":
        st.session_state.editable_article_title = selected

# --- 初始化可編輯標題的狀態 ---
if 'editable_article_title' not in st.session_state:
    st.session_state.editable_article_title = ""


# --- 模組 1: 文章輸入與比例選擇 ---
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        if not st.session_state.df.empty:
            titles = ["--- 請選擇熱點文章 ---"] + st.session_state.df["標題"].tolist()
            
            try:
                default_index = titles.index(st.session_state.editable_article_title) if st.session_state.editable_article_title in titles else 0
            except ValueError:
                default_index = 0
            
            st.selectbox(
                "選擇熱點文章標題：", 
                titles, 
                index=default_index,
                key="title_select",
                on_change=update_editable_title
            )
            
            st.text_area( # <-- 更改為 st.text_area
                "編輯或輸入文章標題:", 
                value=st.session_state.editable_article_title, 
                key="editable_article_title"
            )
            
        else:
            st.text_area( # <-- 更改為 st.text_area
                "手動輸入文章標題 (請先產生報表):", 
                value=st.session_state.editable_article_title, 
                key="editable_article_title"
            )

    article_title = st.session_state.editable_article_title
        
    with col2:
        st.markdown("##### 貼文比例選擇")
        ratio = st.radio(
            "選擇圖片比例：",
            ('1:1', '4:3'), 
            key='ratio_select',
            horizontal=True
        )
        
        uploaded_file = st.file_uploader("🖼️ 上傳背景圖片 (可選)", type=["jpg", "jpeg", "png"])

# --- 模組 2: 視覺模板預覽 ---
st.markdown("#### 🖼️ 視覺模板預覽")

# 1. 根據選定的比例生成圖片 (用於下載)
visual_img_selected = generate_visual_content(
    article_title, 
    ratio, # '1:1' or '4:3'
    uploaded_file
)

# 2. 生成另一個比例的圖片 (用於對照預覽)
other_ratio = '4:3' if ratio == '1:1' else '1:1'
visual_img_other = generate_visual_content(
    article_title, 
    other_ratio, 
    uploaded_file
)

# 3. 顯示兩個預覽
col_1_1, col_4_3 = st.columns(2)

with col_1_1:
    st.markdown("**1:1 比例預覽**")
    st.image(visual_img_selected if ratio == '1:1' else visual_img_other, 
             caption=f"1:1 預覽 (字型檔: {FONT_FILE_PATH})", 
             use_column_width='always')

with col_4_3:
    st.markdown("**4:3 比例預覽**")
    st.image(visual_img_selected if ratio == '4:3' else visual_img_other, 
             caption=f"4:3 預覽 (字型檔: {FONT_FILE_PATH})", 
             use_column_width='always')

# --- 下載按鈕 (改為 PNG 以避免 JPEG 壓縮失真) ---
img_byte_arr_png = BytesIO()
visual_img_selected.save(img_byte_arr_png, format='PNG') 
img_byte_arr_png.seek(0)

st.download_button(
    label="⬇️ 下載成品 (PNG) - 無損畫質",
    data=img_byte_arr_png.getvalue(),
    file_name=f"{article_title[:10].replace('/', '_')}_image_{ratio}.png", 
    mime="image/png"
)

# --- 模組 3: AI 文案優化 ---
st.markdown("---")
st.subheader("🤖 AI 社群標題優化 (生成 3 份標題)") 

if st.button("✨ 生成優化社群標題", key="generate_new_copy_btn"): 
    if not article_title: 
        st.error("⚠️ 請確認已輸入**文章標題**。")
    else:
        with st.spinner("AI 正在根據您的輸入撰寫 3 份優化標題中..."): 
            try:
                ai_text = generate_ai_copy(article_title)
                if ai_text:
                    st.session_state.accelerator_copy = ai_text 
            except Exception as e:
                pass

# 顯示 AI 生成結果
if 'accelerator_copy' in st.session_state and st.session_state.accelerator_copy:
    st.success("✅ 3 份優化標題生成完成！") 
    st.markdown(st.session_state.accelerator_copy)
