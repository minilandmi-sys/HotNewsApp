import streamlit as st
import streamlit.components.v1 as components  # 必須補上這一行，否則會出現 NameError

# 1. 確保 article_title 變數存在 (初始化)
if 'article_title' not in st.session_state:
    st.session_state['article_title'] = "請輸入或選擇文章標題"

# ================= 新增：JavaScript Canvas 高級圖卡產生器 =================
st.markdown("---")
st.header("✨ 高級圖卡產生器 (Canvas 版)")
st.info("這是使用瀏覽器硬體加速繪製的高級模板，支援半透明遮罩效果。")

# 這裡提供一個輸入框，讓你在測試頁面也能手動輸入內容
article_title = st.text_input("輸入要顯示在圖卡上的標題：", value=st.session_state['article_title'])

def render_canvas_generator(title):
    # 將標題中的換行符號轉義，並處理引號避免 JavaScript 語法錯誤
    clean_title = title.replace('\n', ' ').replace('"', '\\"').replace("'", "\\'")
    
    canvas_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 15px;">
        <canvas id="newsCanvas" width="800" height="450" style="border:1px solid #d3d3d3; border-radius: 10px; max-width: 100%; box-shadow: 0 8px 16px rgba(0,0,0,0.1);"></canvas>
        <p style="color: #888; font-size: 13px; margin-top: 15px;">💡 提示：按右鍵可直接「另存圖片」</p>
    </div>

    <script>
        const canvas = document.getElementById('newsCanvas');
        const ctx = canvas.getContext('2d');

        // 1. 繪製背景圖片
        const img = new Image();
        img.crossOrigin = "anonymous"; 
        img.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=800'; 
        
        img.onload = () => {{
            // 繪製背景
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // 2. 繪製頂部半透明遮罩
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, 350);

            // 3. 設定文字樣式並繪製
            ctx.textAlign = 'center';
            ctx.fillStyle = 'white';
            
            // 設定字型 (優先使用系統中文字型)
            ctx.font = 'bold 45px "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif';
            
            const titleText = "{clean_title}";
            // 簡單的斷行邏輯
            if (titleText.length > 15) {{
                ctx.fillText(titleText.
