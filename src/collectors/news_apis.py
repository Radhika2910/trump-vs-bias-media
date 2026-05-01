from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from src.schema import PROJECT_QUERIES, Record
from src.settings import settings


def collect_newsapi(queries: list[str] | None = None) -> list[Record]:
    if not settings.newsapi_key:
        print("Skipping NewsAPI collection: NEWSAPI_KEY is not set.")
        return []

    records: list[Record] = []
    from_date = (datetime.now(timezone.utc) - timedelta(days=settings.collection_days)).date().isoformat()
    for query in queries or PROJECT_QUERIES:
        params = {
            "q": query,
            "language": "en",
            "from": from_date,
            "sortBy": "publishedAt",
            "pageSize": min(settings.max_items_per_source, 100),
            "apiKey": settings.newsapi_key,
        }
        response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=30)
        if response.status_code != 200:
            print(f"NewsAPI error for {query}: {response.status_code} {response.text[:200]}")
            continue
        for article in response.json().get("articles", []):
            records.append(
                Record(
                    source_type="news",
                    source_name=article.get("source", {}).get("name", "NewsAPI"),
                    author=article.get("author") or "",
                    title=article.get("title") or "",
                    text=" ".join(filter(None, [article.get("title"), article.get("description"), article.get("content")])),
                    url=article.get("url") or "",
                    published_at=article.get("publishedAt") or "",
                    query=query,
                    metadata={"provider": "newsapi"},
                )
            )
    return records


def collect_gnews(queries: list[str] | None = None) -> list[Record]:
    if not settings.gnews_key:
        print("Skipping GNews collection: GNEWS_KEY is not set.")
        return []

    records: list[Record] = []
    from_date = (datetime.now(timezone.utc) - timedelta(days=settings.collection_days)).isoformat()
    for query in queries or PROJECT_QUERIES:
        params = {
            "q": query,
            "lang": "en",
            "country": "us",
            "from": from_date,
            "max": min(settings.max_items_per_source, 100),
            "token": settings.gnews_key,
        }
        response = requests.get("https://gnews.io/api/v4/search", params=params, timeout=30)
        if response.status_code != 200:
            print(f"GNews error for {query}: {response.status_code} {response.text[:200]}")
            continue
        for article in response.json().get("articles", []):
            records.append(
                Record(
                    source_type="news",
                    source_name=article.get("source", {}).get("name", "GNews"),
                    title=article.get("title") or "",
                    text=" ".join(filter(None, [article.get("title"), article.get("description"), article.get("content")])),
                    url=article.get("url") or "",
                    published_at=article.get("publishedAt") or "",
                    query=query,
                    metadata={"provider": "gnews"},
                )
            )
    return records


def collect_mediastack(queries: list[str] | None = None) -> list[Record]:
    if not settings.mediastack_key:
        print("Skipping Mediastack collection: MEDIASTACK_KEY is not set.")
        return []

    records: list[Record] = []
    from_date = (datetime.now(timezone.utc) - timedelta(days=settings.collection_days)).date().isoformat()
    for query in queries or PROJECT_QUERIES:
        params = {
            "access_key": settings.mediastack_key,
            "keywords": query,
            "languages": "en",
            "countries": "us",
            "date": from_date,
            "limit": min(settings.max_items_per_source, 100),
        }
        response = requests.get("http://api.mediastack.com/v1/news", params=params, timeout=30)
        if response.status_code != 200:
            print(f"Mediastack error for {query}: {response.status_code} {response.text[:200]}")
            continue
        for article in response.json().get("data", []):
            records.append(
                Record(
                    source_type="news",
                    source_name=article.get("source") or "Mediastack",
                    author=article.get("author") or "",
                    title=article.get("title") or "",
                    text=" ".join(filter(None, [article.get("title"), article.get("description")])),
                    url=article.get("url") or "",
                    published_at=article.get("published_at") or "",
                    query=query,
                    metadata={"provider": "mediastack"},
                )
            )
    return records


def collect_all_news(queries: list[str] | None = None) -> list[Record]:
    return collect_newsapi(queries) + collect_gnews(queries) + collect_mediastack(queries)

