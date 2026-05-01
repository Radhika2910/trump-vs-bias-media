import pandas as pd
from datetime import datetime
from GoogleNews import GoogleNews
import re
import time

# === CONFIG ===
queries = ["pahalgam attack", "operation sindoor"]
countries = ['in', 'us', 'gb', 'pk', 'tr', 'au', 'cn', 'bd', 'lk']

def sanitize_filename(query):
    return re.sub(r'\s+', '_', query.strip().lower())

def fetch_from_google_news(query, pages=5, max_retries=3):
    print(f"[GoogleNews] Fetching news for query: {query}")
    googlenews = GoogleNews(start='04/22/2025', end=datetime.now().strftime('%m/%d/%Y'))
    googlenews.set_lang('en')
    data = []

    for country in countries:
        retries = 0
        while retries <= max_retries:
            try:
                googlenews.clear()
                googlenews.search(f"{query} site:{country}")
                for page in range(1, pages + 1):
                    googlenews.get_page(page)
                    results = googlenews.result()
                    for res in results:
                        data.append({
                            "source": "GoogleNews",
                            "query": query,
                            "country": country,
                            "date": res.get("date", ""),
                            "text": res.get("title", "") + " - " + res.get("desc", ""),
                            "likes": "",
                            "retweets": ""
                        })
                    time.sleep(1)
                break  # success, exit retry loop
            except Exception as e:
                retries += 1
                wait_time = 2 ** retries
                print(f"Error fetching GoogleNews for {query} in {country}: {e}")
                if retries <= max_retries:
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached, skipping.")
                    break

    return data

if __name__ == "__main__":
    for q in queries:
        google_data = fetch_from_google_news(q, pages=5)
        if google_data:
            google_df = pd.DataFrame(google_data)
            filename = "google_news_" + sanitize_filename(q) + "_headlines.csv"
            google_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\u2705 Saved Google News data to {filename}")
        else:
            print(f"[GoogleNews] No data fetched for query '{q}'")
