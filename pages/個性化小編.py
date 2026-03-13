import streamlit as st
import random

# --- 1. 模擬 AI 邏輯區 (根據關鍵字自動變換語氣) ---
def simulate_smart_editor(input_text):
    if not input_text:
        return ""

    # 定義關鍵字庫
    fashion_keywords = ["LV", "香奈兒", "精品", "包包", "運動鞋", "穿搭", "時尚", "美妝"]
    news_keywords = ["新聞", "報導", "政府", "快訊", "發生", "天氣", "交通"]

    # 判斷輸入內容屬於哪一類 (預設為日常風格)
    is_fashion = any(k in input_text.upper() for k in fashion_keywords)
    is_news = any(k in input_text.upper() for k in news_keywords)

    if is_fashion:
        # 模擬 Vogue/小紅書 風格
        openings = ["OMG！姐妹們妳們聽說了嗎？✨", "這絕對是編編今年看過最燒的！🔥", "妳們的荷包準備好了嗎？🛍️"]
        bodies = [
            f"這次的「{input_text[:8]}...」真的美到讓人眼睛張不開！💎 根本是專為愛獨特的妳打造的夢幻逸品。",
            f"走在路上回頭率絕對破表！那種自帶光芒的感覺，光是想像就覺得值得了。💖",
            f"雖然編編的心也在滴血，但這設計真的太擊中人心了，完全是必收清單！"
        ]
        closings = ["妳們也被燒到了嗎？留言分享妳的夢幻清單！😍", "快 tag 妳那個愛閃亮的朋友一起流口水吧！", "編編已經決定要入手了，妳們呢？✨"]
    
    elif is_news:
        # 模擬 ETtoday 抓重點風格
        openings = ["小編幫大家抓好重點了！🔎", "這件事最近討論度超高，大家有注意到嗎？",
