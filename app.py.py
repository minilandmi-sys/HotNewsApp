import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time
from io import BytesIO

# 4 個網站的 RSS
RSS_FEEDS = {
    "妞新聞": "https://www.niusnews.com/feed",
    "Women's Health TW": "https://www.womenshealthmag.com/tw/rss/all.xml",
    "BEAUTY美人圈": "https://www.beauty321.com/feed_pin",
    "A Day Magazine": "https://www.adaymag.com/feed"
}

def parse_entries(entries):
    parsed_list = []
    for entry in entries:
        published_time = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_time = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published_time = datetime(*entry.updated_parsed[:6])
        if not published_time:
            published_time = datetime.now()

        parsed_list.append({
            "標題": entry.title if "title" in entry else "(無標題)",
            "連結": entry.link if "link" in entry else "",
            "發佈時間": published_time.strftime("%Y-%m-%d %H:%M"),
            "來源": ""
        })
    return parsed_list

def fetch_top5_each_site():
    all_entries = []
    for site, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries:
            continue

        entries = parse_entries(feed.entries)
        entries_sorted = entries[:5]
        for item in entries_sorted:
            item["來源"] = site
        all_entries.extend(entries_sorted)

        time.sleep(1)

    all_entries.sort(key=lambda x: x["發佈時間"], reverse=True)
    return pd.DataFrame(all_entries)

# ================= Streamlit UI =================
st.title("📰 熱門新聞報表工具 (RSS)")

if st.button("📊 產生最新報表"):
    df = fetch_top5_each_site()
    if df.empty:
        st.warning("⚠️ 沒有抓到任何文章。")
    else:
        st.success("✅ 報表已產生！")
        st.dataframe(df)

        # 轉換為 Excel 並下載
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()

        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}_HotNews.xlsx"

        st.download_button(
            label="⬇️ 下載 Excel 報表",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
