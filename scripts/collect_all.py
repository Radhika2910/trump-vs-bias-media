"""
Run all collectors in sequence and append results to output/records_raw.jsonl.

Steps:
  1. Tweets      — X API v2        (needs app attached to a Project in dev portal)
  2. Reddit      — Reddit API      (free; needs REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET)
  3. News        — NewsAPI / GNews / Mediastack
  4. Fact-checks — PolitiFact / FactCheck.org / Snopes (RSS + per-article scraping)

Records are APPENDED on each run — safe to run daily to build up a multi-day dataset.
Re-run the notebook after collecting to refresh the analysis.

Usage (from project root):
    python scripts/collect_all.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from collect_tweets     import main as collect_tweets
from collect_reddit     import main as collect_reddit
from collect_news       import main as collect_news
from collect_factchecks import main as collect_factchecks


if __name__ == '__main__':
    steps = [
        ('Tweets (X API)',                       collect_tweets),
        ('Reddit posts',                          collect_reddit),
        ('News articles (NewsAPI/GNews/Mediastack)', collect_news),
        ('Fact-checks (RSS + page scraping)',     collect_factchecks),
    ]

    for label, fn in steps:
        print('=' * 58)
        print(f'  {label}')
        print('=' * 58)
        fn()
        print()

    output = Path(__file__).parent.parent / 'output' / 'records_raw.jsonl'
    if output.exists():
        with open(output) as f:
            n = sum(1 for line in f if line.strip())
        print(f'Done. {n} total records in {output}')
    print('Re-run the notebook to refresh the analysis.')
