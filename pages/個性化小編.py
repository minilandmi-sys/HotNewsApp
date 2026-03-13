import streamlit as st
import random

def generate_editor_intro(input_text):
    """
    優化後的模擬邏輯：
    根據不同的人設風格準備了幾套模板，讓生成的文字不再一模一樣。
    """
    # 這裡我們模擬小編會說的話，分成開場、內文、結尾
    # 參考 ETtoday 的親切與 Vogue 的質感
    
    options = [
        # 模板 1：親切日常風格 (ETtoday 感)
        f"大家也有過這種感覺嗎？✨ 剛看到「{input_text[:15]}...」真的很有共鳴。生活不需要太嚴肅，但一定要有態度。快在下面跟小編分享你的看法吧！👇",
        
        # 模板 2：時髦質感風格 (Vogue 感)
        f"質感藏在細節裡。🖤 關於「{input_text[:15]}...」，其實我們追求的不只是新聞，而是一種生活風格。拒絕官腔，讓我們一起找到那個記憶點。妳們覺得呢？",
        
        # 模板 3：快速抓重點風格 (簡潔感)
        f"重點幫大家抓好了！🔎「{input_text[:15]}...」這件事其實沒那麼複雜。簡單、直接、無距離，這就是小編想分享給你們的品牌個性。歡迎留言聊聊！",
        
        # 模板 4：感性共鳴風格
        f"有時候，最動人的就是這種無距離的日常。🍂 看到「{input_text[:15]}...」，忍不住想跟你們分享這份心情。不重複贅字，只說真心話。✨"
    ]
    
    # 隨機挑選一個模板回傳
    return random.choice(options)

# --- 頁面配置 ---
st.set_page_config(page_title="個性化小編 - Social Media Editor", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.caption("輸入一段文字，隨機產生具備 ETtoday 與 Vogue 風格的小編引言。")

# --- 介面設計 ---
with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("輸入原始內容")
        user_input = st.text_area(
            "請貼上新聞標題、文章段落或想分享的話：",
            placeholder="例如：今天天氣變冷了，大家記得加件衣服...",
            height=250
        )
        
        generate_btn = st.button("✨ 產生小編引言", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate_btn:
            if user_input:
                with st.spinner("小編正在構思中..."):
                    # 執行產生邏輯
                    result = generate_editor_intro(user_input)
                    st.success("引言已模擬生成！")
                    st.text_area("複製到社群平台：", value=result, height=250)
                    
                    if st.button("清除重來"):
                        st.rerun()
            else:
                st.warning("請先輸入一些文字內容喔！")

# --- 側邊欄說明 ---
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **小編人設說明：**
    - **口吻：** 無距離感、拒絕內容官腔。
    - **目標：** 創造品牌個性，尋找記憶點。
    - **核心：** 簡要、不囉唆。
    """
)
