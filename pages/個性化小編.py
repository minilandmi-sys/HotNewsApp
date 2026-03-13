import streamlit as st

def generate_editor_intro(input_text):
    """
    這裡預留串接 LLM (如 Gemini 或 OpenAI) 的位置。
    目前先以邏輯示範小編的人設回覆風格。
    """
    # 這裡的 prompt 設定完全依照你的需求
    system_prompt = """
    你是一個社群小編，擅長透過貼近粉絲、了解群眾、運用平台特性，以無距離感的口吻創造品牌個性。
    風格參考：
    - 《ETtoday新聞雲》：親切、抓重點、日常語調。
    - 《Vogue》：時髦、生活化、有質感但不官腔。
    規則：簡要說明，不重複太多字，拒絕官腔，找到共同記憶點。
    """
    
    # 模擬生成結果 (實際使用時請在此串接 API)
    # response = llm.generate(system_prompt + input_text)
    return f"【小編引言預覽】\n\n「大家也有過這種感覺嗎？✨ {input_text[:20]}... 其實生活就是這樣，不一定要很嚴肅，但一定要很有態度。快在下面跟小編分享你的看法吧！👇」"

# --- 頁面配置 ---
st.set_page_config(page_title="個性化小編 - Social Media Editor", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.caption("輸入一段文字，讓具備 ETtoday 與 Vogue 風格的小編為你撰寫引言。")

# --- 介面設計 ---
with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("輸入原始內容")
        user_input = st.text_area(
            "請貼上新聞標題、文章段落或想分享的話：",
            placeholder="例如：今天天氣變冷了，大家記得加件衣服...",
            height=200
        )
        
        generate_btn = st.button("產生小編引言", type="primary")

    with col2:
        st.subheader("生成結果")
        if generate_btn:
            if user_input:
                with st.spinner("小編正在構思中..."):
                    # 執行產生邏輯
                    result = generate_editor_intro(user_input)
                    st.success("引言已生成！")
                    st.text_area("複製到社群平台：", value=result, height=200)
                    st.button("清除重來")
            else:
                st.warning("請先輸入一些文字內容喔！")

# --- 側邊欄說明 ---
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **小編人設說明：**
    - **口吻：** 無距離感、拒絕官腔。
    - **目標：** 創造品牌個性，尋找粉絲記憶點。
    - **核心：** 簡要、不囉唆。
    """
)
