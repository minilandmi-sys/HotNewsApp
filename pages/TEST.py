# ================= 新增：JavaScript Canvas 高級圖卡產生器 =================
st.markdown("---")
st.header("✨ 高級圖卡產生器 (Canvas 版)")
st.info("這是使用瀏覽器硬體加速繪製的高級模板，支援半透明遮罩效果。")

def render_canvas_generator(title):
    # 將標題中的換行符號轉義，避免 JavaScript 報錯
    clean_title = title.replace('\n', ' ')
    
    canvas_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 15px;">
        <canvas id="newsCanvas" width="800" height="450" style="border:1px solid #d3d3d3; border-radius: 10px; max-width: 100%; box-shadow: 0 8px 16px rgba(0,0,0,0.1);"></canvas>
        <p style="color: #888; font-size: 13px; margin-top: 15px;">按右鍵可直接「另存圖片」</p>
    </div>

    <script>
        const canvas = document.getElementById('newsCanvas');
        const ctx = canvas.getContext('2d');

        // 1. 繪製背景圖片
        const img = new Image();
        img.crossOrigin = "anonymous"; 
        // 這裡可以更換你想要的背景圖 URL
        img.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=800'; 
        
        img.onload = () => {{
            // 繪製並裁切背景
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // 2. 繪製頂部半透明遮罩
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, 350);

            // 3. 設定文字樣式並繪製
            ctx.textAlign = 'center';
            ctx.fillStyle = 'white';
            
            // 主標題 (自動帶入選定的文章標題)
            ctx.font = 'bold 45px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            
            // 處理長標題自動斷行 (簡易版)
            const titleText = "{clean_title}";
            if (titleText.length > 15) {{
                ctx.fillText(titleText.substring(0, 15), canvas.width / 2, 130);
                ctx.fillText(titleText.substring(15, 30), canvas.width / 2, 210);
            }} else {{
                ctx.fillText(titleText, canvas.width / 2, 160);
            }}

            // 副標題 (黃色)
            ctx.fillStyle = '#FFD700';
            ctx.font = '500 30px "Noto Sans TC", "Microsoft JhengHei", sans-serif';
            ctx.fillText('今日熱點新聞追蹤報告', canvas.width / 2, 300);
        }};
    </script>
    """
    components.html(canvas_html, height=550)

# 呼叫 Canvas 產生器，帶入當前選定的標題
render_canvas_generator(article_title)
