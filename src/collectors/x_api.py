from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from src.schema import PROJECT_QUERIES, Record
from src.settings import settings


SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


def collect_x_posts(queries: list[str] | None = None) -> list[Record]:
    if not settings.x_bearer_token:
        print("Skipping X collection: X_BEARER_TOKEN is not set.")
        return []

    queries = queries or PROJECT_QUERIES
    start_time = datetime.now(timezone.utc) - timedelta(days=settings.collection_days)
    headers = {"Authorization": f"Bearer {settings.x_bearer_token}"}
    records: list[Record] = []

    for query in queries:
        params = {
            "query": f"({query}) lang:en -is:retweet",
            "max_results": min(settings.max_items_per_source, 100),
            "start_time": start_time.isoformat().replace("+00:00", "Z"),
            "tweet.fields": "created_at,author_id,public_metrics,lang",
        }
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            print(f"X API error for {query}: {response.status_code} {response.text[:200]}")
            continue

        for tweet in response.json().get("data", []):
            metrics = tweet.get("public_metrics", {})
            records.append(
                Record(
                    source_type="tweet",
                    source_name="X",
                    author=str(tweet.get("author_id", "")),
                    title=tweet.get("text", "")[:120],
                    text=tweet.get("text", ""),
                    url=f"https://x.com/i/web/status/{tweet.get('id', '')}",
                    published_at=tweet.get("created_at", ""),
                    query=query,
                    engagement=float(metrics.get("like_count", 0) + metrics.get("reply_count", 0) + metrics.get("retweet_count", 0)),
                    metadata=metrics,
                )
            )

    return records

