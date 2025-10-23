import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time
from io import BytesIO
import requests # 新增：用於呼叫 Gemini API
from PIL import Image, ImageDraw, ImageFont 

# ================= LLM API 設定 (已轉換為 Gemini) =================
GEMINI_MODEL = "gemini-2.5-flash" # 已更新為正式版本
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# 嘗試讀取 GEMINI API 金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ 錯誤：請在 Streamlit Secrets 中設定 **GEMINI_API_KEY**！")
    API_KEY = ""

# 4 個網站的 RSS
RSS_FEEDS = {
    "妞新聞": "https://www.niusnews.com/feed",
    "Women's Health TW": "https://www.womenshealthmag.com/tw/rss/all.xml",
    "BEAUTY美人圈": "https://www.beauty321.com/feed_pin",
    "A Day Magazine": "https://www.adaymag.com/feed"
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

def get_font(size, bold=False):
    """
    嘗試載入 CJK 字體以正確顯示中文 (如微軟正黑體或 Noto Sans CJK)。
    Note: 由於運行環境無法確定字型路徑，這是一個最佳嘗試。
    """
    # 根據 Streamlit 運行環境，嘗試載入常見的 CJK 字型名稱。
    # 如果您將微軟正黑體 (.ttc) 上傳到應用目錄，可以直接指定路徑。
    cjk_font_paths = [
        "msjh.ttc",            # 微軟正黑體
        "NotoSansCJK-Regular.ttc", # Noto CJK (Regular)
        "NotoSansCJK-Bold.ttc",    # Noto CJK (Bold)
        "simhei.ttf"               # 簡體環境下的黑體
    ]
    
    font_files = [
        "msjhbd.ttc" if bold else "msjh.ttc", # 微軟正黑體 (Bold/Regular)
        "NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc", # Noto CJK (Bold/Regular)
    ]
    
    # 嘗試載入 CJK 字體
    for path in font_files + cjk_font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
            
    # 最終備援：使用預設字體 (中文顯示效果可能不佳)
    return ImageFont.load_default()

def generate_visual_content(title, ratio='1:1', uploaded_file=None):
    """
    使用 Pillow 函式庫，在伺服器端生成帶有文章標題的圖片模板。
    新增底部黑色半透明遮罩，並優化字型載入以解決中文排版問題。
    """
    # 定義尺寸 (1000px max dimension)
    MAX_DIM = 1000
    if ratio == '4:3': # 依據要求，4:3 改為 3:4 直式版型 (750x1000)
        WIDTH = int(MAX_DIM * 3 / 4) # 750
        HEIGHT = MAX_DIM # 1000
    else: # 1:1 (1000x1000)
        WIDTH = MAX_DIM # 1000
        HEIGHT = MAX_DIM # 1000
    
    # 1. 載入背景圖或建立基礎圖
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            # 使用 LANCZOS 演算法進行高品質縮放
            img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        except Exception:
            img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')
    else:
        img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')


    # --- 2. 新增底部半透明黑色遮罩 (Overlay) ---
    # 遮罩高度約佔圖片底部的 25% (從 75% 高度開始)
    OVERLAY_START_Y = int(HEIGHT * 0.75) 
    
    # 建立一個新的 RGBA 圖片用於遮罩
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # 繪製半透明的黑色矩形 (Alpha=150/255，約 60% 透明度)
    opacity = 150 
    overlay_draw.rectangle([0, OVERLAY_START_Y, WIDTH, HEIGHT], fill=(0, 0, 0, opacity))
    
    # 將遮罩疊加到主圖上
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img) # 重新獲取 Draw 物件

    # --- 3. 繪製頂部模板標題 ---
    title_size = int(WIDTH / 35)
    title_font = get_font(title_size, bold=True)
    draw.text((WIDTH / 2, HEIGHT * 0.08), 
              "【社群內容加速器】視覺模板", 
              fill="#ffffff", 
              font=title_font, 
              anchor="mm")
    
    # --- 4. 繪製文章標題 (置中靠下，在遮罩上) ---
    
    article_to_display = title or "請輸入文章標題以跟風熱點..."
    
    # 設置字型 (40pt 約等於 70px)
    ARTICLE_FONT_SIZE = 70 
    
    # 根據比例設定字型屬性：兩個比例都使用 bold 模擬微軟正黑體粗體字型風格
    article_font = get_font(ARTICLE_FONT_SIZE, bold=True)
    
    # 實現多行自動換行
    # 針對中文標題，調整字元限制 (750px 寬度較窄，1:1 較寬)
    CHAR_LIMIT = 15 if WIDTH < 1000 else 20 
    
    lines = []
    current_line = ""
    for char in article_to_display:
        # 在遇到空格或符號時也嘗試斷行，讓中文排版更自然
        if len(current_line) < CHAR_LIMIT and char not in '，。、！？：；':
            current_line += char
        else:
            # 確保標點符號不單獨成行 (簡單處理)
            if char in '，。、！？：；' and len(lines) > 0:
                 lines[-1] += char
                 continue
            lines.append(current_line)
            current_line = char
    lines.append(current_line)
    lines = [line.strip() for line in lines if line.strip()]

    # 定位：置中靠下 (底部錨點在圖片高度 90% 處)
    line_height = ARTICLE_FONT_SIZE * 1.5 # 增加行距，讓文字更寬鬆
    total_text_height = len(lines) * line_height

    # 將文字塊的底部邊緣對齊到 HEIGHT * 0.90
    Y_BOTTOM_ANCHOR = HEIGHT * 0.90 
    
    # 計算第一行的起始Y座標 
    y_start = Y_BOTTOM_ANCHOR - total_text_height 

    # 繪製
    for i, line in enumerate(lines):
        draw.text((WIDTH / 2, y_start + i * line_height), 
                  line, 
                  fill="#ffffff", 
                  font=article_font, 
                  anchor="mt", # 使用 'mt' (middle-top) 錨點進行置中對齊
                  stroke_width=2, # 添加描邊來模擬粗體和清晰度
                  stroke_fill="#000000") 

    return img

# ================= 模組 3：AI 文案優化邏輯 (使用 Gemini API) =================

def generate_ai_copy(article_title): # 已移除 meme_text
    """
    使用 Gemini API 生成 3 份針對社群貼文優化的標題，僅依賴文章標題。
    NOTE: 若出現 400 錯誤，請檢查您的 GEMINI_API_KEY 是否有效且具有足夠權限。
    """
    if not API_KEY:
        return "API 金鑰未設定，無法呼叫 Gemini API。"
        
    if not article_title: # 僅檢查 article_title
        return None

    # 系統指令：設定為機智的台灣社群編輯 (已修改為生成標題)
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
        response.raise_for_status() # 對 HTTP 錯誤碼拋出異常

        result = response.json()
        
        # 檢查並提取生成的文本
        if result and 'candidates' in result and len(result['candidates']) > 0 and 'parts' in result['candidates'][0]['content']:
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text.strip()
        else:
            st.error("⚠️ Gemini API 回傳格式錯誤或無內容。")
            return "API 回應解析失敗。"

    except requests.exceptions.RequestException as e:
        # 由於 400 錯誤常與金鑰/權限相關，此處保留錯誤顯示以利使用者排查
        st.error(f"⚠️ Gemini API 呼叫失敗: {e}")
        st.write(f"API 回應狀態碼: {response.status_code if 'response' in locals() else 'N/A'}")
        return "API 呼叫失敗。"
    except Exception as e:
        st.error(f"⚠️ 發生未知錯誤：{e}")
        return "未知錯誤。"


# ================= Streamlit UI (主程式) =================

st.title("📰 熱門新聞報表工具 (RSS)")

# 報表產生區 (維持原有邏輯)
if st.button("📊 產生最新報表"):
    df = fetch_top5_each_site()
    st.session_state.df = df # 將 DataFrame 存入 session_state
    
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
    # 確保 session_state.df 在第一次執行時存在
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()


# ================= 社群內容加速器 (新增模組) =================
st.markdown("---")
st.header("🚀 社群內容加速器")
st.markdown("使用熱點文章標題，快速製作圖片視覺與優化標題！") 

# --- 文章標題狀態管理回呼函式 ---
def update_editable_title():
    """當下拉選單變動時，更新可編輯標題的狀態。"""
    selected = st.session_state.title_select
    # 如果選擇的不是預設選項，則更新可編輯標題
    if selected != "--- 請選擇熱點文章 ---":
        st.session_state.editable_article_title = selected

# --- 初始化可編輯標題的狀態 ---
if 'editable_article_title' not in st.session_state:
    st.session_state.editable_article_title = ""


# --- 模組 1: 文章輸入與比例選擇 ---
# 將上傳圖片功能與比例選擇放在同一欄
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        # 模組 1: 文章標題輸入 (從報表選擇或手動輸入)
        if not st.session_state.df.empty:
            
            # 準備標題列表，並新增預設選項
            titles = ["--- 請選擇熱點文章 ---"] + st.session_state.df["標題"].tolist()
            
            # 嘗試保持當前編輯中的標題在選單中被選中
            try:
                default_index = titles.index(st.session_state.editable_article_title) if st.session_state.editable_article_title in titles else 0
            except ValueError:
                default_index = 0
            
            # 下拉選單：選擇標題，變動時呼叫回呼函式
            st.selectbox(
                "選擇熱點文章標題：", 
                titles, 
                index=default_index,
                key="title_select",
                on_change=update_editable_title
            )
            
            # 可編輯文字輸入框：用於顯示和修改選中的標題
            st.text_input(
                "編輯或輸入文章標題:", 
                value=st.session_state.editable_article_title, # 從 session_state 讀取初始值
                key="editable_article_title" # <--- 直接使用 canonical key
            )
            

        else:
            # Fallback if no report is generated
            st.text_input(
                "手動輸入文章標題 (請先產生報表):", 
                value=st.session_state.editable_article_title, 
                key="editable_article_title" # <--- 直接使用 canonical key
            )

    # <--- 在容器外定義 article_title，確保使用最新的 editable_article_title 狀態
    article_title = st.session_state.editable_article_title
        
    with col2:
        # 模組 2: 比例選擇
        st.markdown("##### 貼文比例選擇")
        ratio = st.radio(
            "選擇圖片比例：",
            ('1:1', '4:3'), 
            key='ratio_select',
            horizontal=True
        )
        
        # 新增圖片上傳功能
        uploaded_file = st.file_uploader("🖼️ 上傳背景圖片 (可選)", type=["jpg", "jpeg", "png"])

# --- 模組 2: 視覺模板預覽 ---
st.markdown("#### 🖼️ 視覺模板預覽")
visual_img = generate_visual_content(article_title, ratio, uploaded_file)
st.image(visual_img, caption="視覺內容預覽 (已加入底部遮罩並優化中文排版)", use_column_width='auto')

# --- 下載按鈕 (只留 JPG) ---
# 只保留 JPG 下載按鈕
img_byte_arr_jpg = BytesIO()
visual_img.save(img_byte_arr_jpg, format='JPEG', quality=95) # quality=95 以確保較高品質的 JPG

st.download_button(
    label="⬇️ 下載成品 (JPG)",
    data=img_byte_arr_jpg.getvalue(),
    file_name=f"{article_title[:10].replace('/', '_')}_image.jpg",
    mime="image/jpeg"
)

# --- 模組 3: AI 文案優化 ---
st.markdown("---")
st.subheader("🤖 AI 社群標題優化 (生成 3 份標題)") # 修正文案為標題

if st.button("✨ 生成優化社群標題", key="generate_new_copy_btn"): # 修正文案為標題
    if not article_title: # 僅檢查文章標題
        st.error("⚠️ 請確認已輸入**文章標題**。")
    else:
        with st.spinner("AI 正在根據您的輸入撰寫 3 份優化標題中..."): # 修正文案為標題
            try:
                # 呼叫函式時已移除 meme_text
                ai_text = generate_ai_copy(article_title)
                if ai_text:
                    st.session_state.accelerator_copy = ai_text # 儲存新標題
            except Exception as e:
                # 錯誤處理已在 generate_ai_copy 內部完成
                pass

# 顯示 AI 生成結果
if 'accelerator_copy' in st.session_state and st.session_state.accelerator_copy:
    st.success("✅ 3 份優化標題生成完成！") # 修正文案為標題
    # 將 Markdown 格式的結果 (如 *) 渲染出來
    st.markdown(st.session_state.accelerator_copy)
