import streamlit as st
import streamlit.components.v1 as components

# 確保基礎變數存在，避免後續 NameError
if 'article_title' not in st.session_state:
    st.session_state['article_title'] = "台灣國產「全新7人座MPV」挑戰百萬內！"

st.title("✨ 高級圖卡產生器 (Canvas 版)")

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
        
        // 1. 設置背景圖片
        img.crossOrigin = "anonymous"; 
        img.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=800'; 
        
        img.onload = () => {{
            // 繪製背景
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // 2. 繪製底部半透明遮罩 (0.5 透明度黑色)
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, 350);

            // 3. 設定文字樣式
            ctx.textAlign = 'center';
            
            // 主標題顏色與字型
            ctx.fillStyle = 'white';
            ctx.font = 'bold 65px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            
            const titleText = "{clean_title}";
            
            // 自動斷行處理 (以 12 個字為基準斷行，因字體變大)
            if (titleText.length > 12) {{
                ctx.fillText(titleText.substring(0, 12), canvas.width / 2, 120);
                ctx.fillText(titleText.substring(12, 24), canvas.width / 2, 210);
            }} else {{
                ctx.fillText(titleText, canvas.width / 2, 160);
            }}

            // 4. 副標題 (黃色)
            ctx.fillStyle = '#FFD700';
            ctx.font = '500 45px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            ctx.fillText('今日熱點新聞追蹤報告', canvas.width / 2, 310);
        }};
    </script>
    """
    components.html(canvas_html, height=550)

# 執行渲染
if user_input:
    render_canvas_generator(user_input)
