# --- 1. 原有的下載按鈕 (確保括號正確關閉) ---
img_byte_arr_png = BytesIO()
visual_img_selected.save(img_byte_arr_png, format='PNG') 
img_byte_arr_png.seek(0)

st.download_button(
    label="⬇️ 下載成品 (PNG) - 無損畫質",
    data=img_byte_arr_png.getvalue(),
    file_name="social_image.png",
    mime="image/png"
)

# --- 2. 插入區隔線 ---
st.write("---")

# --- 3. JavaScript Canvas 高級圖卡產生器 ---
# 確保這裡有 import
import streamlit.components.v1 as components

st.header("✨ 高級圖卡產生器 (Canvas 版)")
st.info("這是使用瀏覽器硬體加速繪製的高級模板。")

def render_canvas_generator(title_text):
    # 預防性處理：確保傳入的是字串且處理換行
    clean_title = str(title_text).replace('\n', ' ')
    
    canvas_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 15px;">
        <canvas id="newsCanvas" width="800" height="450" style="border:1px solid #d3d3d3; border-radius: 10px; max-width: 100%; box-shadow: 0 8px 16px rgba(0,0,0,0.1);"></canvas>
        <p style="color: #888; font-size: 13px; margin-top: 15px;">💡 提示：按右鍵可直接「另存圖片」</p>
    </div>

    <script>
        const canvas = document.getElementById('newsCanvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = "anonymous"; 
        img.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=800'; 
        
        img.onload = () => {{
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, 350);
            ctx.textAlign = 'center';
            ctx.fillStyle = 'white';
            ctx.font = 'bold 45px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            
            const text = "{clean_title}";
            if (text.length > 15) {{
                ctx.fillText(text.substring(0, 15), canvas.width / 2, 130);
                ctx.fillText(text.substring(15, 30), canvas.width / 2, 210);
            }} else {{
                ctx.fillText(text, canvas.width / 2, 160);
            }}

            ctx.fillStyle = '#FFD700';
            ctx.font = '500 30px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            ctx.fillText('今日熱點新聞追蹤報告', canvas.width / 2, 300);
        }};
    </script>
    """
    components.html(canvas_html, height=550)

# --- 4. 執行函式 ---
# 這裡檢查 article_title 變數是否存在，若不存在則給予預設值
current_title = article_title if 'article_title' in locals() else "請先產生報表"
render_canvas_generator(current_title)
