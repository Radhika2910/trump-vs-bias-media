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
