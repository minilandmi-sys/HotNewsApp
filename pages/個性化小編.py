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
            "這種
