import json
import os
from datetime import datetime, timezone
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID     = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
MAX_ITEMS            = int(os.getenv('MAX_ITEMS_PER_SOURCE', 100))
OUTPUT_PATH          = Path(__file__).parent.parent / 'output' / 'records_raw.jsonl'

# Mix of subreddits across the political spectrum for balanced coverage
SUBREDDITS = [
    'politics',             # large, leans left — lots of mainstream media discussion
    'conservative',         # right-leaning — pro-Trump perspective
    'news',                 # relatively neutral news aggregation
    'PoliticalDiscussion',  # moderated, sourced debate
    'NeutralPolitics',      # strictly neutral, citations required
]

QUERIES = [
    'Trump media bias',
    'Trump fake news',
    'Trump mainstream media',
    'Trump media coverage',
]


def collect():
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print('  REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not set in .env — skipping Reddit.')
        print('  → See instructions at the top of this file to get free credentials.')
        return []

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent='trump-media-bias-study/1.0 (educational project)',
    )

    records = []
    for sub_name in SUBREDDITS:
        sub_count = 0
        try:
            sub = reddit.subreddit(sub_name)
            for query in QUERIES:
                results = sub.search(
                    query,
                    limit=min(25, MAX_ITEMS),
                    sort='relevance',
                    time_filter='month',
                )
                for post in results:
                    text = post.title
                    if post.selftext and post.selftext != '[removed]':
                        text += ' ' + post.selftext[:300]
                    records.append({
                        'source_type': 'tweet',          # kept as 'tweet' for notebook compatibility
                        'source_name': f'Reddit/r/{sub_name}',
                        'text': text,
                        'published_at': datetime.fromtimestamp(
                            post.created_utc, tz=timezone.utc
                        ).isoformat(),
                        'engagement': post.score + post.num_comments,
                        'claim': '',
                        'verdict': '',
                    })
                    sub_count += 1
        except Exception as e:
            print(f'  Error on r/{sub_name}: {e}')
        if sub_count:
            print(f'  r/{sub_name}: {sub_count} posts')

    return records


def main():
    print('Collecting Reddit posts...')
    records = collect()
    if records:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, 'a') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        print(f'Saved {len(records)} Reddit records → {OUTPUT_PATH}')
    else:
        print('No Reddit records collected.')


if __name__ == '__main__':
    main()
