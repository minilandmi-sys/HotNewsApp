import streamlit as st
import google.generativeai as genai
import os

# --- 1. 配置 Gemini API ---
# 提醒：在 Streamlit Cloud 部署時，請在 Settings > Secrets 設定 GOOGLE_API_KEY
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_ai_intro(content):
    """
    呼叫 Gemini 產生符合特定人設的引言
    """
    prompt = f"""
    你是一個社群小編，擅長透過貼近粉絲、了解群眾、運用平台特性，以無距離感的口吻創造品牌個性。
    風格參考：
    - 《ETtoday新聞雲》：親切、抓重點、日常語調。
    - 《Vogue》：時髦、生活化、有質感但不官腔。
    規則：簡要說明，不重複太多字，拒絕官腔，找到共同記憶點。

    請針對以下內容撰寫一段吸引人的社群引言：
    ---
    {content}
    ---
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"產生失敗，錯誤訊息：{e}"

# --- 2. 頁面介面 ---
st.set_page_config(page_title="個性化小編", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📢 原始內容輸入")
    user_input = st.text_area(
        "請輸入新聞內容或想要轉換的文字：",
        placeholder="把你想發布的內容貼在這裡...",
        height=300
    )
    
    # 增加一個風格微調選項（選填）
    tone_option = st.radio("偏好風格：", ["綜合風格", "偏向 ETtoday (親切)", "偏向 Vogue (質感)"], horizontal=True)
    
    generate_btn = st.button("✨ 產生小編引言", type="primary", use_container_width=True)

with col2:
    st.subheader("📄 AI 建議引言")
    if generate_btn:
        if user_input:
            with st.spinner("AI 小編正在思考如何與粉絲對話..."):
                # 如果有選特定風格，可以在這裡微調 prompt（選配）
                final_result = generate_ai_intro(user_input)
                
                st.markdown("---")
                st.success("生成成功！")
                st.write(final_result)
                st.button("📋 複製文字 (請手動選取)")
        else:
            st.warning("小編需要一點內容才能發揮喔！")

# --- 3. 側邊欄：人設預覽 ---
with st.sidebar:
    st.header("小編人設檔案")
    st.info("""
    **核心個性：** 無距離感、創造品牌個性。
    **參考對象：** ETtoday, Vogue。
    **禁忌：** 拒絕官腔、重複贅字。
    """)
