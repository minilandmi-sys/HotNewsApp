import streamlit as st
import random

# --- 1. 模擬 AI 邏輯區 (根據關鍵字自動變換語氣) ---
def simulate_smart_editor(input_text):
    if not input_text:
        return ""

    # 定義關鍵字庫 (大寫比較，增加準確度)
    text_upper = input_text.upper()
    fashion_keywords = ["LV", "LOUIS VUITTON", "精品", "包包", "運動鞋", "穿搭", "時尚", "美妝", "寶石"]
    news_keywords = ["新聞", "報導", "政府", "快訊", "發生", "天氣", "交通", "公告"]

    # 判斷輸入內容屬於哪一類
    is_fashion = any(k in text_upper for k in fashion_keywords)
    is_news = any(k in text_upper for k in news_keywords)

    if is_fashion:
        # 模擬妳提供的「姐妹們/閃瞎」風格
        openings = ["OMG！姐妹們妳們聽說了嗎？✨", "這絕對是編編今年看過最燒的！🔥", "妳們的荷包準備好了嗎？🛍️", "編編的眼睛快被閃瞎了！💎"]
        bodies = [
            f"這次的「{input_text[:8]}...」真的美到讓人眼睛張不開！根本是專為愛獨特的妳打造的夢幻逸品。💖",
            f"走在路上回頭率絕對破表！那種自帶光芒的感覺，光是想像就覺得值得了。🤩",
            f"這根本是為我們這些愛閃亮、愛女孩們量身打造的吧！編編的心已經被徹底擊中了！💘"
        ]
        closings = ["妳們也被燒到了嗎？快留言跟我一起流口水！😍", "快 tag 妳那個愛閃亮的朋友一起看！✨", "編編已經決定要入手了，妳們呢？🔥"]
    
    elif is_news:
        # 模擬 ETtoday 抓重點風格
        openings = ["小編幫大家抓好重點了！🔎", "這件事最近討論度超高，大家有注意到嗎？", "最新消息快報！📢", "這件事大家一定要留意！🚩"]
        bodies = [
            f"關於「{input_text[:10]}...」，其實重點就在這裡。不說官腔話，直接帶大家看關鍵。📝",
            "生活忙碌，小編懂大家沒時間看長篇大論，所以幫大家把這則資訊整理好了。🌿",
            "這種事真的發生在我們日常生活中，找到共同記憶點才是最重要的。"
        ]
        closings = ["大家覺得這件事該怎麼看？下方留言交流！👇", "如果是你，你會怎麼處理呢？告訴小編吧！", "別忘了分享給身邊的人知道最新狀況！"]
    
    else:
        # 預設：日常親切風格
        openings = ["大家今天好嗎？✨", "小編剛才滑到這個，覺得超有感...", "關於這件事，其實我有個小秘密想分享..."]
        bodies = [
            f"雖然「{input_text[:8]}...」看起來很平常，但生活不就是這些細節組成的嗎？",
            "比起那些嚴肅的內容，我更喜歡這種貼近大家的真實感。🌿",
            "有時候不需要多華麗的文字，簡單的共鳴才是最有溫度的。"
        ]
        closings = ["留言告訴我你的看法吧！💬", "大家今天也有遇到有趣的事嗎？來跟我聊聊！", "按讚分享，讓我知道你也喜歡這種風格。"]

    # 隨機組合生成結果
    result = f"{random.choice(openings)}\n\n{random.choice(bodies)}\n\n{random.choice(closings)}"
    return result

# --- 2. Streamlit 介面 ---
st.set_page_config(page_title="個性化小編", layout="wide")

st.title("✍️ 個性化小編引言產生器")
st.caption("無須 API，根據內容自動切換《ETtoday》或《Vogue》語氣。")

# 建立左右兩欄
col1, col2 = st.columns(2)

with col1:
    st.subheader("📢 原始內容輸入")
    user_input = st.text_area("請輸入內容 (例如：LV新出的鑲鑽運動鞋)：", height=300)
    generate_btn = st.button("✨ 產生小編引言", type="primary", use_container_width=True)

with col2:
    st.subheader("📄 生成結果")
    if generate_btn:
        if user_input:
            with st.spinner("小編正在構思中..."):
                final_result = simulate_smart_editor(user_input)
                st.success("引言已生成！")
                st.text_area("預覽與複製：", value=final_result, height=300)
        else:
            st.warning("⚠️ 請先輸入內容喔！")

# --- 側邊欄 ---
with st.sidebar:
    st.header("👤 小編人設檔案")
    st.markdown("""
    - **人設核心**：無距離感、貼近粉絲。
    - **風格參考**：ETtoday (親切)、Vogue (質感)。
    - **規則**：簡要、不重複、拒絕官腔。
    """)
    st.write("---")
    st.caption("Status: Running smoothly (Local Mode)")
