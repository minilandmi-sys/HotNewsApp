import streamlit as st
import random

# --- 1. 小編邏輯區 (這就是優化後的部分) ---
def generate_editor_intro(input_text):
    """
    根據人設隨機組合語句，讓靜態版本看起來不那麼死板。
    """
    if not input_text:
        return ""

    # 開場白：模擬 ETtoday 的抓重點與親切感
    openings = [
        f"大家有發現嗎？✨ 關於「{input_text[:10]}...」這件事，",
        f"小編今天滑到「{input_text[:10]}...」，心裡真的很有感，",
        f"最近大家都在討論這個：{input_text[:10]}... 其實，",
        f"敲碗很久的「{input_text[:10]}...」終於來了！"
    ]
    
    # 內文：模擬 Vogue 的質感與無距離感
    bodies = [
        "生活有時候不需要太多客套話，懂的人自然懂。就像這則內容給我的感覺一樣，簡單卻很有力量。",
        "比起那些官腔的報導，我更喜歡這種貼近大家的真實感。這不就是我們要的品牌個性嗎？",
        "質感藏在細節裡，不管是想要時髦還是想要親切，找到那個記憶點才是最重要的。",
        "其實我們追求的不只是新聞，而是一種生活態度。不需要過多贅字，這就是最真實的樣子。"
    ]
    
    # 結尾：強化社群互動
    closings = [
        "下方留言告訴小編你的看法吧！👇",
        "你們也會這樣覺得嗎？在下面分享你的記憶點吧！✨",
        "如果你也喜歡這種質感生活，別忘了分享給朋友喔！"
    ]
    
    # 隨機組合
    result = f"【小編引言預覽】\n\n{random.choice(openings)}\n\n{random.choice(bodies)}\n\n{random.choice(closings)}\n\n#小編碎碎念 #質感生活 #拒絕官腔"
    return result

# --- 2. 頁面配置 ---
st.set_page_config(page_title="個性化小編 - Social Media Editor", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.caption("輸入一段文字，透過「無距離感小編」人設為你撰寫引言。")

# --- 3. 介面設計 ---
with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📢 原始內容輸入")
        user_input = st.text_area(
            "請貼上新聞標題、文章段落或想分享的話：",
            placeholder="例如：最新的保養趨勢或是時裝週消息...",
            height=300
        )
        
        generate_btn = st.button("✨ 產生小編引言", type="primary", use_container_width=True)

    with col2:
        st.subheader("📄 生成結果")
        if generate_btn:
            if user_input:
                with st.spinner("小編正在構思中..."):
                    # 執行產生邏輯
                    result = generate_editor_intro(user_input)
                    st.success("引言已模擬生成！")
                    st.text_area("複製到社群平台：", value=result, height=300)
                    
                    if st.button("清除重來"):
                        st.rerun()
            else:
                st.warning("⚠️ 請先輸入一些文字內容喔！")

# --- 4. 側邊欄：完整人設檔案 ---
with st.sidebar:
    st.header("👤 小編人設檔案")
    st.info(
        """
        **核心個性：**
        擅長透過貼近粉絲、了解群眾，以無距離感的口吻創造品牌個性。

        **風格參考：**
        - **ETtoday：** 親切、日常語調。
        - **Vogue：** 時髦質感、生活化。

        **禁忌：**
        - 拒絕官腔、不重複贅字。
        """
    )
    st.write("---")
    st.caption("當前狀態：**靜態演示版**")
