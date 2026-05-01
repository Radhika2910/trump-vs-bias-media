import requests
import pandas as pd
from datetime import datetime, timedelta
import re
import time

# === CONFIG ===
bearer_token = r"AAAAAAAAAAAAAAAAAAAAAPX9xwEAAAAA3iGryA0rLnhhQhIA9%2FdEKUautMc%3DNnCHdblmUD74wweEP02czkBanuFOGZAy1u1wlsNtSeYIsDoqqQ"  # Replace this with your actual token
queries = ["operation sindoor"]
countries = ['in', 'us', 'gb', 'pk', 'tr', 'au', 'cn', 'bd', 'lk']

end_dt = datetime.utcnow() - timedelta(seconds=20)
start_dt = end_dt - timedelta(days=6)
start_date = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
end_date = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

headers = {"Authorization": f"Bearer {bearer_token}"} if bearer_token else None

def sanitize_filename(query):
    return re.sub(r'\s+', '_', query.strip().lower())

def wait_until(reset_timestamp):
    wait_seconds = max(reset_timestamp - time.time(), 0)
    print(f"Rate limit hit. Sleeping for {int(wait_seconds)} seconds until reset...")
    time.sleep(wait_seconds + 1)  # sleep a bit extra

def fetch_from_twitter_raw(query):
    if not headers:
        print("[Twitter] Bearer token not provided. Exiting.")
        return []

    print(f"[Twitter API] Fetching tweets for query: {query}")
    data = []
    base_url = "https://api.twitter.com/2/tweets/search/recent"

    # Request these fields to get place info
    tweet_fields = "created_at,lang,public_metrics,geo"
    expansions = "geo.place_id"
    place_fields = "country,country_code,full_name"

    params = {
        "query": query,
        "max_results": 100,
        "start_time": start_date,
        "end_time": end_date,
        "tweet.fields": tweet_fields,
        "expansions": expansions,
        "place.fields": place_fields
    }

    count = 0
    next_token = None

    while count < 1000:
        if next_token:
            params["next_token"] = next_token

        try:
            response = requests.get(base_url, headers=headers, params=params)
            if response.status_code == 429:
                reset = response.headers.get("x-rate-limit-reset")
                if reset:
                    wait_until(float(reset))
                    continue
                else:
                    print("Rate limited but no reset header, sleeping 60 seconds...")
                    time.sleep(60)
                    continue
            elif response.status_code != 200:
                raise Exception(f"{response.status_code} - {response.text}")

            result = response.json()

            tweets = result.get("data", [])
            includes = result.get("includes", {})
            places_list = includes.get("places", [])
            meta = result.get("meta", {})

            # Map place_id to place info
            places = {place["id"]: place for place in places_list}

            for tweet in tweets:
                geo = tweet.get("geo", {})
                place_id = geo.get("place_id")
                country = None
                if place_id and place_id in places:
                    place = places[place_id]
                    country = place.get("country_code") or place.get("country")

                data.append({
                    "source": "Twitter",
                    "query": query,
                    "country": country,
                    "date": tweet.get("created_at"),
                    "text": tweet.get("text"),
                    "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                    "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0)
                })

            count += len(tweets)
            next_token = meta.get("next_token")
            if not next_token:
                break

            time.sleep(1)

        except Exception as e:
            print(f"Error fetching for {query}: {e}")
            break

    return data


if __name__ == "__main__":
    for q in queries:
        twitter_data = fetch_from_twitter_raw(q)
        if twitter_data:
            twitter_df = pd.DataFrame(twitter_data)
            filename = "twitter_" + sanitize_filename(q) + ".csv"
            twitter_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Saved Twitter data to {filename}")
        else:
            print(f"[Twitter] No data fetched for query '{q}'")
