import streamlit as st
import streamlit.components.v1 as components

# 確保基礎變數存在，避免後續 NameError
if 'article_title' not in st.session_state:
    st.session_state['article_title'] = "預設熱點標題"

st.title("✨ 視覺產生器測試")

# 提供輸入介面
user_input = st.text_input("編輯標題內容：", value=st.session_state['article_title'])

def render_canvas_generator(title):
    # 轉義特殊字元，避免 JS 崩潰
    clean_title = title.replace('\n', ' ').replace('"', '\\"').replace("'", "\\'")
    
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
            ctx.font = 'bold 45px sans-serif';
            const text = "{clean_title}";
            if (text.length > 15) {{
                ctx.fillText(text.substring(0, 15), canvas.width / 2, 130);
                ctx.fillText(text.substring(15, 30), canvas.width / 2, 210);
            }} else {{
                ctx.fillText(text, canvas.width / 2, 160);
            }}
            ctx.fillStyle = '#FFD700';
            ctx.font = '30px sans-serif';
            ctx.fillText('今日熱點新聞追蹤報告', canvas.width / 2, 300);
        }};
    </script>
    """
    components.html(canvas_html, height=550)

# 執行渲染
render_canvas_generator(user_input)
