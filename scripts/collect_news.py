import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

NEWSAPI_KEY    = os.getenv('NEWSAPI_KEY')
GNEWS_KEY      = os.getenv('GNEWS_KEY')
MEDIASTACK_KEY = os.getenv('MEDIASTACK_KEY')
MAX_ITEMS      = int(os.getenv('MAX_ITEMS_PER_SOURCE', 100))
OUTPUT_PATH    = Path(__file__).parent.parent / 'output' / 'records_raw.jsonl'

QUERIES = [
    'Trump media bias',
    'Trump fake news',
    'Trump mainstream media',
    'Trump media coverage',
]


def collect_from_newsapi():
    if not NEWSAPI_KEY:
        print('  NEWSAPI_KEY not set — skipping NewsAPI.')
        return []

    client = NewsApiClient(api_key=NEWSAPI_KEY)
    records = []

    for query in QUERIES:
        try:
            resp = client.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=min(MAX_ITEMS, 100),
            )
            articles = resp.get('articles', [])
            for article in articles:
                text = (article.get('content') or article.get('description')
                        or article.get('title') or '')
                records.append({
                    'source_type': 'news',
                    'source_name': (article.get('source') or {}).get('name') or 'NewsAPI',
                    'text': text,
                    'published_at': article.get('publishedAt') or '',
                    'engagement': 0,
                    'claim': '',
                    'verdict': '',
                })
            print(f'  NewsAPI: {len(articles)} articles — {query}')
        except Exception as e:
            print(f'  NewsAPI error on "{query}": {e}')

    return records


def collect_from_gnews():
    if not GNEWS_KEY:
        print('  GNEWS_KEY not set — skipping GNews.')
        return []

    records = []

    for query in QUERIES:
        try:
            resp = requests.get(
                'https://gnews.io/api/v4/search',
                params={'q': query, 'token': GNEWS_KEY, 'lang': 'en', 'country': 'us', 'max': 10},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = data.get('articles', [])
            for article in articles:
                text = (article.get('content') or article.get('description')
                        or article.get('title') or '')
                records.append({
                    'source_type': 'news',
                    'source_name': (article.get('source') or {}).get('name') or 'GNews',
                    'text': text,
                    'published_at': article.get('publishedAt') or '',
                    'engagement': 0,
                    'claim': '',
                    'verdict': '',
                })
            print(f'  GNews: {len(articles)} articles — {query}')
        except Exception as e:
            print(f'  GNews error on "{query}": {e}')

    return records


def collect_from_mediastack():
    if not MEDIASTACK_KEY:
        print('  MEDIASTACK_KEY not set — skipping Mediastack.')
        return []

    records = []

    for query in QUERIES:
        try:
            resp = requests.get(
                'http://api.mediastack.com/v1/news',
                params={
                    'access_key': MEDIASTACK_KEY,
                    'keywords': query,
                    'languages': 'en',
                    'countries': 'us',
                    'limit': min(MAX_ITEMS, 25),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = data.get('data', [])
            for article in articles:
                text = article.get('description') or article.get('title') or ''
                records.append({
                    'source_type': 'news',
                    'source_name': article.get('source') or 'Mediastack',
                    'text': text,
                    'published_at': article.get('published_at') or '',
                    'engagement': 0,
                    'claim': '',
                    'verdict': '',
                })
            print(f'  Mediastack: {len(articles)} articles — {query}')
        except Exception as e:
            print(f'  Mediastack error on "{query}": {e}')

    return records


def collect():
    return collect_from_newsapi() + collect_from_gnews() + collect_from_mediastack()


def main():
    print('Collecting news articles...')
    records = collect()
    if records:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, 'a') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        print(f'Saved {len(records)} news records → {OUTPUT_PATH}')
    else:
        print('No news records collected.')


if __name__ == '__main__':
    main()
