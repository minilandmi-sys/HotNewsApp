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

# ================= 模組 2 & 3：視覺內容生成 (Pillow 實現) =================

def get_font(size, bold=False):
    """嘗試載入常見字體，若失敗則回傳預設字體"""
    try:
        # 模擬 Impact 或 Arial Bold 作為梗圖字體
        # Note: 在實際部署環境中，您可能需要提供 'Impact.ttf' 或 CJK 字體檔案
        font_name = "arial.ttf" if not bold else "arialbd.ttf"
        return ImageFont.truetype(font_name, size)
    except IOError:
        # 若找不到特定字體，使用預設字體
        return ImageFont.load_default()

def generate_visual_content(title, meme_text, ratio='1:1', uploaded_file=None): # 新增 uploaded_file 參數
    """
    使用 Pillow 函式庫，在伺服器端生成帶有梗圖文字的圖片。
    """
    # 定義尺寸
    WIDTH = 1000
    HEIGHT = 1778 if ratio == '9:16' else 1000
    
    if uploaded_file is not None:
        # 載入上傳的圖片並縮放至模板尺寸
        try:
            img = Image.open(uploaded_file).convert("RGB")
            # 使用 LANCZOS 演算法進行高品質縮放
            img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        except Exception as e:
            # 圖片載入失敗，使用藍色預設模板作為備援
            st.warning(f"⚠️ 圖片載入失敗，使用藍色預設模板。錯誤: {e}")
            img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')
    else:
        # 建立基礎圖片 (藍色背景作為模板)
        img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')

    draw = ImageDraw.Draw(img)

    # --- 繪製模板標題與文章標題 ---
    title_size = int(WIDTH / 35)
    article_size = int(WIDTH / 50)
    
    title_font = get_font(title_size, bold=True)
    article_font = get_font(article_size, bold=False)

    # 模板標題 (保持單行置中)
    draw.text((WIDTH / 2, HEIGHT * 0.08), 
              "【社群內容加速器】視覺模板", 
              fill="#ffffff", 
              font=title_font, 
              anchor="mm")
    
    # 文章標題 - 實現多行自動換行 (使用簡易字元限制)
    article_to_display = title or "請輸入文章標題以跟風熱點..."
    
    # 針對中文標題，每行限制大約 30 個字元 (粗略估計 80% 寬度)
    CHAR_LIMIT = 30 
    lines = []
    current_line = ""
    
    # 處理標題換行
    for char in article_to_display:
        # 這裡使用 len() 模擬字元數限制，而非精準的像素計算
        if len(current_line) < CHAR_LIMIT:
            current_line += char
        else:
            lines.append(current_line)
            current_line = char
    lines.append(current_line) # Add the last line

    lines = [line.strip() for line in lines if line.strip()] # 清理空白行

    y_start = HEIGHT * 0.15 # 換行文字起始 Y 座標
    line_height = article_size * 1.5 # 行距

    # 繪製 wrapped 文章標題
    for i, line in enumerate(lines):
        draw.text((WIDTH / 2, y_start + i * line_height), 
                  line, 
                  fill="#ffffff", 
                  font=article_font, 
                  anchor="mt") # 使用 'mt' 錨點進行頂部置中對齊

    # --- 繪製梗圖文字 (白字黑邊效果) ---
    if meme_text:
        meme_size = int(WIDTH / 12)
        y_pos = HEIGHT * 0.85
        meme_font = get_font(meme_size, bold=True)
        
        # 模擬黑邊效果
        outline_width = 3 
        outline_color = "black"
        
        # 繪製黑邊
        for x_offset in range(-outline_width, outline_width + 1):
            for y_offset in range(-outline_width, outline_width + 1):
                if x_offset != 0 or y_offset != 0:
                    draw.text((WIDTH / 2 + x_offset, y_pos + y_offset), 
                              meme_text.upper(), 
                              font=meme_font, 
                              fill=outline_color, 
                              anchor="ms")
        
        # 繪製白色主體
        draw.text((WIDTH / 2, y_pos), 
                  meme_text.upper(), 
                  font=meme_font, 
                  fill="white", 
                  anchor="ms")

    return img

# ================= 模組 3：AI 文案優化邏輯 (使用 Gemini API) =================

def generate_ai_copy(article_title, meme_text):
    """
    使用 Gemini API 生成 3 份針對社群貼文優化的標題。
    NOTE: 若出現 400 錯誤，請檢查您的 GEMINI_API_KEY 是否有效且具有足夠權限。
    """
    if not API_KEY:
        return "API 金鑰未設定，無法呼叫 Gemini API。"
        
    if not article_title or not meme_text:
        return None

    # 系統指令：設定為機智的台灣社群編輯 (已修改為生成標題)
    system_prompt = "Act as a witty Taiwanese social media editor (社群小編). Your output must be in Traditional Chinese. Based on the article title and the visual meme text provided by the user, generate 3 different, highly engaging, and clickable article titles/headlines ( suitable for a blog or social media post). Each title should be concise and separated by a single line break. Format your response using Markdown bullet points (*), NOT numbered lists."
            
    user_query = f"請根據以下資訊生成 3 份優化的社群標題:\n\n文章標題 (核心資訊): {article_title}\n視覺文案 (梗圖文字): {meme_text}"

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
st.markdown("使用熱點文章標題，快速製作梗圖視覺與優化標題！") # 修正文案為標題

# --- 模組 1: 文章輸入與比例選擇 ---
# 將上傳圖片功能與比例選擇放在同一欄
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        # 模組 1: 文章標題輸入 (從報表選擇或手動輸入)
        if not st.session_state.df.empty:
            titles = ["--- 手動輸入 ---"] + st.session_state.df["標題"].tolist()
            selected_title_option = st.selectbox(
                "選擇或輸入熱點文章標題：", 
                titles, 
                key="title_select"
            )
            
            if selected_title_option == "--- 手動輸入 ---":
                article_title = st.text_input("或手動輸入文章標題:", value="", key="title_manual")
            else:
                article_title = selected_title_option
        else:
            article_title = st.text_input("手動輸入文章標題 (請先產生報表):", value="", key="title_manual_only")
        
        # 模組 3: 視覺化文案輸入
        meme_text = st.text_area("視覺化文案 (梗圖文字):", 
                                  value="", 
                                  height=100,
                                  placeholder="輸入要疊加在圖片上的標語或梗圖文字，例如：好險有跟到這波熱點！")
    
    with col2:
        # 模組 2: 比例選擇
        st.markdown("##### 貼文比例選擇")
        ratio = st.radio(
            "選擇圖片比例：",
            ('1:1', '9:16'),
            key='ratio_select',
            horizontal=True
        )
        
        # 新增圖片上傳功能
        uploaded_file = st.file_uploader("🖼️ 上傳背景圖片 (可選)", type=["jpg", "jpeg", "png"])

# --- 模組 2: 視覺模板預覽 ---
st.markdown("#### 🖼️ 視覺模板預覽")
# 呼叫函式時傳入上傳的檔案
visual_img = generate_visual_content(article_title, meme_text, ratio, uploaded_file)
st.image(visual_img, caption="視覺內容預覽 (由 Pillow 模擬 Canvas 繪製，已支援長標題換行與自訂背景)", use_column_width='auto')

# --- 下載按鈕 (只留 JPG) ---
# 只保留 JPG 下載按鈕
img_byte_arr_jpg = BytesIO()
visual_img.save(img_byte_arr_jpg, format='JPEG', quality=95) # quality=95 以確保較高品質的 JPG

st.download_button(
    label="⬇️ 下載成品 (JPG)",
    data=img_byte_arr_jpg.getvalue(),
    file_name=f"{article_title[:10].replace('/', '_')}_meme.jpg",
    mime="image/jpeg"
)

# --- 模組 3: AI 文案優化 ---
st.markdown("---")
st.subheader("🤖 AI 社群標題優化 (生成 3 份標題)") # 修正文案為標題

if st.button("✨ 生成優化社群標題", key="generate_new_copy_btn"): # 修正文案為標題
    if not article_title or not meme_text:
        st.error("⚠️ 請確認已輸入**文章標題**和**梗圖文字**。")
    else:
        with st.spinner("AI 正在根據您的輸入撰寫 3 份優化標題中..."): # 修正文案為標題
            try:
                ai_text = generate_ai_copy(article_title, meme_text)
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
