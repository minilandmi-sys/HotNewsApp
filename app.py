import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components # 必須引入此模組

# ================= 1. 基礎設定 =================

RSS_FEEDS = {
    "妞新聞": "https://www.niusnews.com/feed",
    "Women's Health TW": "https://www.womenshealthmag.com/tw/rss/all.xml",
    "BEAUTY美人圈": "https://www.beauty321.com/feed_pin",
    "A Day Magazine": "https://www.adaymag.com/feed",
    "The Femin": "https://thefemin.com/category/editorial/issue/feed"
}

FONT_FILE_PATH = ".devcontainer/NotoSansTC-Bold.ttf" 

# ================= 2. 輔助函式 =================

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
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            entries = parse_entries(feed.entries)
            entries_sorted = entries[:5]
            for item in entries_sorted:
                item["來源"] = site
            all_entries.extend(entries_sorted)
            time.sleep(0.5)
        except Exception as e:
            st.error(f"抓取 {site} 失敗: {e}")
    
    if not all_entries:
        return pd.DataFrame()
    all_entries.sort(key=lambda x: x["發佈時間"], reverse=True)
    return pd.DataFrame(all_entries)

def get_font(size):
    try:
        return ImageFont.truetype(FONT_FILE_PATH, size)
    except IOError:
        return ImageFont.load_default()

def generate_visual_content(title, ratio='1:1', uploaded_file=None, font_size=40, font_color="#ffffff"):
    MAX_DIM = 1000
    WIDTH, HEIGHT = (MAX_DIM, MAX_DIM) if ratio == '1:1' else (750, 1000)
    
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            img_width, img_height = img.size
            target_ratio = WIDTH / HEIGHT
            if img_width / img_height > target_ratio:
                new_height = HEIGHT
                new_width = int(img_width * (HEIGHT / img_height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - WIDTH) / 2
                img = img.crop((int(left), 0, int(left + WIDTH), HEIGHT))
            else:
                new_width = WIDTH
                new_height = int(img_height * (WIDTH / img_width))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                top = (new_height - HEIGHT) / 2
                img = img.crop((0, int(top), WIDTH, int(top + HEIGHT)))
        except:
            img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')
    else:
        img = Image.new('RGB', (WIDTH, HEIGHT), color='#1e3a8a')

    # 遮罩
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    rect_y = int(HEIGHT * 0.75)
    draw_ov.rectangle([0, rect_y, WIDTH, int(HEIGHT * 0.9)], fill=(0, 0, 0, 180))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 畫字
    draw = ImageDraw.Draw(img)
    font = get_font(font_size)
    display_text = title if title else "請選擇標題"
    draw.text((WIDTH / 2, rect_y + 20), display_text, fill=font_color, font=font, anchor="mt")
    return img

# ================= 3. Streamlit UI =================

st.title("📰 熱門新聞報表工具 (RSS)")

if st.button("📊 產生最新報表"):
    df = fetch_top5_each_site()
    st.session_state.df = df
    if not df.empty:
        st.success("✅ 報表已產生！")
        st.dataframe(df)

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

st.markdown("---")
st.header("🚀 社群內容加速器")

# 標題選擇
if not st.session_state.df.empty:
    titles = ["--- 請選擇熱點文章 ---"] + st.session_state.df["標題"].tolist()
    selected_title = st.selectbox("選擇文章標題：", titles)
    article_title = st.text_area("編輯標題:", value="" if selected_title == "--- 請選擇熱點文章 ---" else selected_title)
else:
    article_title = st.text_area("手動輸入標題 (或先產生報表):")

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    ratio = st.radio("圖片比例：", ('1:1', '4:3'), horizontal=True)
    custom_font_size = st.slider("字型大小", 20, 100, 40)
with col_opt2:
    uploaded_file = st.file_uploader("🖼️ 上傳背景", type=["jpg", "png"])
    custom_font_color = st.color_picker("字型顏色", "#ffffff")

# 預覽與下載
if article_title:
    img = generate_visual_content(article_title, ratio, uploaded_file, custom_font_size, custom_font_color)
    st.image(img, caption="預覽畫面", use_column_width=True)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("⬇️ 下載成品圖片", buf.getvalue(), "social_image.png", "image/png")

# ================= 4. Canvas 進階版 =================
st.write("---")
st.header("✨ 高級圖卡產生器 (Canvas 版)")

def render_canvas(title):
    clean_title = str(title).replace('\n', ' ')
    html_code = f"""
    <div style="text-align:center;">
        <canvas id="cv" width="800" height="450" style="border-radius:10px; width:100%;"></canvas>
        <script>
            const c = document.getElementById('cv');
            const ctx = c.getContext('2d');
            const i = new Image();
            i.crossOrigin = "anonymous";
            i.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800';
            i.onload = () => {{
                ctx.drawImage(i, 0, 0, 800, 450);
                ctx.fillStyle = 'rgba(0,0,0,0.6)';
                ctx.fillRect(0, 300, 800, 100);
                ctx.fillStyle = 'white';
                ctx.textAlign = 'center';
                ctx.font = 'bold 35px sans-serif';
                ctx.fillText("{clean_title}", 400, 360);
            }};
        </script>
    </div>
    """
    components.html(html_code, height=500)

render_canvas(article_title if article_title else "等待輸入中...")
