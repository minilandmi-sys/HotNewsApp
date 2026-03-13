import streamlit as st

def generate_editor_intro(input_text):
    """
    這是一個模擬生成函式。
    目前不會呼叫 AI API，僅根據你提供的人設邏輯展示固定回覆格式。
    """
    # 這是你指定的人設設定，已放入邏輯中
    # 規則：簡要說明，不重複太多字，拒絕官腔
    
    intro_template = f"""【小編精選引言】✨

大家最近有注意到嗎？關於「{input_text[:15]}...」

其實生活就是這樣，不需要太多官腔，只要一點點共鳴就能很有溫度。
不管是像 ETtoday 的親切感，還是帶點 Vogue 的時髦質感，我們都要活出自己的品牌個性！

#日常 #品牌個性 #不官腔"""

    return intro_template

# --- 頁面配置 ---
st.set_page_config(page_title="個性化小編 - Social Media Editor", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.caption("輸入一段文字，透過「無距離感小編」人設為你撰寫引言。")

# --- 介面設計 ---
with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📢 原始內容輸入")
        user_input = st.text_area(
            "請貼上新聞標題、文章段落或想分享的話：",
            placeholder="例如：最新的保養趨勢或是時裝週消息...",
            height=250
        )
        
        generate_btn = st.button("✨ 產生小編引言", type="primary", use_container_width=True)

    with col2:
        st.subheader("📄 生成結果")
        if generate_btn:
            if user_input:
                with st.spinner("小編正在構思中..."):
                    # 呼叫模擬邏輯
                    result = generate_editor_intro(user_input)
                    st.success("引言已模擬生成成功！")
                    st.text_area("預覽內容 (可手動修改)：", value=result, height=250)
                    
                    # 貼心小功能：清空按鈕
                    if st.button("清除結果"):
                        st.rerun()
            else:
                st.warning("⚠️ 請先輸入一些文字內容，小編才好發揮喔！")

# --- 側邊欄：完整人設說明 ---
st.sidebar.markdown("### 👤 小編人設檔案")
st.sidebar.info(
    """
    **核心個性：**
    你是一個社群小編，擅長透過貼近粉絲、了解群眾、運用平台特性，以無距離感的口吻創造品牌個性。

    **風格參考：**
    - **ETtoday新聞雲：** 親切、抓重點、日常語調。
    - **Vogue：** 時髦、生活化、有質感但不官腔。

    **寫作規則：**
    - 簡要說明，不重複太多字。
    - 拒絕官腔。
    - 找到粉絲的共同記憶點。
    """
)

st.sidebar.write("---")
st.sidebar.caption("目前的版本為：**靜態演示版**（無須 API KEY）")
