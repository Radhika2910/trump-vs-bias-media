"""
Collect tweets about Trump and media bias using the X API v2.
Appends records to output/records_raw.jsonl.

--- IMPORTANT: Fix required before this script will work ---
The bearer token must come from a Twitter Developer App that is
attached to a Project in the developer portal. To fix:
  1. Go to https://developer.twitter.com/en/portal/dashboard
  2. Create a new Project (Projects → New Project)
  3. Move your existing App under that Project
  4. The same X_BEARER_TOKEN in .env will then work
This is free and takes about 2 minutes.

If you'd rather skip Twitter entirely, use collect_reddit.py instead
— Reddit's API is free and covers the same social media signal.

Usage:
    python scripts/collect_tweets.py
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN    = os.getenv('X_BEARER_TOKEN')
MAX_RESULTS     = min(int(os.getenv('MAX_ITEMS_PER_SOURCE', 100)), 100)
COLLECTION_DAYS = int(os.getenv('COLLECTION_DAYS', 3))
OUTPUT_PATH     = Path(__file__).parent.parent / 'output' / 'records_raw.jsonl'

QUERIES = [
    'Trump media bias -is:retweet lang:en',
    'Trump "fake news" -is:retweet lang:en',
    'Trump mainstream media -is:retweet lang:en',
    'Trump media coverage -is:retweet lang:en',
]


def collect():
    if not BEARER_TOKEN:
        print('  X_BEARER_TOKEN not set in .env — skipping.')
        return []

    client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)
    start_time = datetime.now(timezone.utc) - timedelta(days=COLLECTION_DAYS)
    records = []

    for query in QUERIES:
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=max(10, MAX_RESULTS),   # API minimum is 10
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
            )
            if not response.data:
                print(f'  No results: {query[:60]}')
                continue
            for tweet in response.data:
                m = tweet.public_metrics or {}
                records.append({
                    'source_type': 'tweet',
                    'source_name': 'X',
                    'text': tweet.text,
                    'published_at': tweet.created_at.isoformat() if tweet.created_at else '',
                    'engagement': m.get('like_count', 0) + m.get('reply_count', 0) + m.get('retweet_count', 0),
                    'claim': '',
                    'verdict': '',
                })
            print(f'  {len(response.data)} tweets — {query[:60]}')

        except tweepy.errors.Forbidden as e:
            print(f'  403 Forbidden — app not attached to a Project.')
            print(f'  Fix: https://developer.twitter.com/en/portal/dashboard')
            print(f'  Or use collect_reddit.py as a free alternative.')
            break   # same error will repeat for all queries
        except tweepy.errors.Unauthorized:
            print(f'  401 Unauthorized — check X_BEARER_TOKEN in .env')
            break
        except tweepy.TweepyException as e:
            print(f'  Tweepy error on "{query[:50]}": {e}')

    return records


def main():
    print(f'Collecting tweets (last {COLLECTION_DAYS} days)...')
    records = collect()
    if records:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, 'a') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        print(f'Saved {len(records)} tweet records → {OUTPUT_PATH}')
    else:
        print('No tweet records saved.')


if __name__ == '__main__':
    main()
