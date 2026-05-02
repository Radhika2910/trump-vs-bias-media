import json
import re
import time
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

OUTPUT_PATH = Path(__file__).parent.parent / 'output' / 'records_raw.jsonl'
HEADERS = {'User-Agent': 'Mozilla/5.0 (educational research project)'}

FEEDS = {
    'PolitiFact':    'https://www.politifact.com/rss/factchecks/',
    'FactCheck.org': 'https://www.factcheck.org/feed/',
    'Snopes':        'https://www.snopes.com/fact-check/feed/',
}

# alt text slugs on the ruling images
POLITIFACT_ALT_MAP = {
    'pants-fire':  'Pants on Fire',
    'barely-true': 'Mostly True',
    'half-true':   'Half True',
    'mostly-true': 'Mostly True',
    'mostly-false':'Mostly False',
    'false':       'False',
    'true':        'True',
}

# sorted longest-first so 'mostly false' matches before 'false'
VERDICT_TERMS = sorted([
    'pants on fire', 'four pinocchios',
    'mostly false', 'mostly true', 'half true',
    'false', 'true', 'mixture', 'mixed', 'unproven',
], key=len, reverse=True)


def strip_html(text):
    return re.sub(r'<[^>]+>', ' ', str(text)).strip()


def scrape_politifact_verdict(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for img in soup.select('.c-image__original'):
            alt = img.get('alt', '').lower().strip()
            if not alt:
                continue
            if alt in POLITIFACT_ALT_MAP:
                return POLITIFACT_ALT_MAP[alt]
            normalized = alt.replace('-', ' ')
            for v in VERDICT_TERMS:
                if v in normalized:
                    return v.title()
    except Exception:
        pass
    return ''


def scrape_snopes_verdict(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        el = soup.select_one('.rating_title_wrap')
        if el:
            # snopes appends "About this rating" to the element text
            text = el.get_text(separator=' ').replace('About this rating', '').strip()
            return text
    except Exception:
        pass
    return ''


def scrape_factcheck_verdict(url):
    # no structured element, just scan the page body
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.select('nav, footer, aside, script, style'):
            tag.decompose()
        page_text = soup.get_text(' ').lower()
        for v in VERDICT_TERMS:
            if v in page_text:
                return v.title()
    except Exception:
        pass
    return ''


SCRAPERS = {
    'PolitiFact':    scrape_politifact_verdict,
    'FactCheck.org': scrape_factcheck_verdict,
    'Snopes':        scrape_snopes_verdict,
}


def collect():
    records = []

    for source_name, feed_url in FEEDS.items():
        scrape_fn = SCRAPERS[source_name]
        try:
            feed = feedparser.parse(feed_url)
            print(f'  {source_name}: {len(feed.entries)} entries — scraping verdicts...')
            found = 0
            for entry in feed.entries:
                link = entry.get('link', '')
                verdict = ''
                if link:
                    verdict = scrape_fn(link)
                    time.sleep(0.5)
                if verdict:
                    found += 1
                summary = strip_html(entry.get('summary', ''))
                records.append({
                    'source_type': 'fact_check',
                    'source_name': source_name,
                    'text': summary or entry.get('title', ''),
                    'published_at': entry.get('published', ''),
                    'engagement': 0,
                    'claim': entry.get('title', ''),
                    'verdict': verdict,
                })
            print(f'    {found}/{len(feed.entries)} verdicts extracted')
        except Exception as e:
            print(f'  Error on {source_name}: {e}')

    return records


def main():
    print('Collecting fact-checks (includes per-article scraping — takes ~1 min)...')
    records = collect()
    if records:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, 'a') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        print(f'Saved {len(records)} fact-check records → {OUTPUT_PATH}')
    else:
        print('No fact-check records collected.')


if __name__ == '__main__':
    main()
