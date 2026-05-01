from __future__ import annotations

import feedparser
import requests
from bs4 import BeautifulSoup

from src.schema import Record
from src.settings import settings


FACT_CHECK_FEEDS = {
    "PolitiFact": "https://www.politifact.com/rss/factchecks/",
    "FactCheck.org": "https://www.factcheck.org/feed/",
    "Snopes": "https://www.snopes.com/feed/",
}


def _label_from_text(text: str) -> str:
    lowered = text.lower()
    verdicts = ["pants on fire", "false", "mostly false", "half true", "mostly true", "true", "mixture", "unproven"]
    for verdict in verdicts:
        if verdict in lowered:
            return verdict.title()
    return "unknown"


def collect_fact_checks() -> list[Record]:
    records: list[Record] = []
    for source_name, feed_url in FACT_CHECK_FEEDS.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[: settings.max_items_per_source]:
            title = entry.get("title", "")
            summary = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ", strip=True)
            combined = f"{title} {summary}"
            if "trump" not in combined.lower():
                continue
            records.append(
                Record(
                    source_type="fact_check",
                    source_name=source_name,
                    title=title,
                    text=combined,
                    url=entry.get("link", ""),
                    published_at=entry.get("published", ""),
                    claim=title,
                    verdict=_label_from_text(combined),
                    metadata={"provider": "rss"},
                )
            )

    # Simple fallback: FactCheck.org search page can help when its feed is sparse.
    if not records:
        try:
            response = requests.get("https://www.factcheck.org/search/?fwp_search=Trump", timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select("article")[: settings.max_items_per_source]:
                title_el = item.select_one("h3, h2")
                link_el = item.select_one("a")
                title = title_el.get_text(" ", strip=True) if title_el else ""
                records.append(
                    Record(
                        source_type="fact_check",
                        source_name="FactCheck.org",
                        title=title,
                        text=item.get_text(" ", strip=True),
                        url=link_el.get("href", "") if link_el else "",
                        claim=title,
                        verdict=_label_from_text(item.get_text(" ", strip=True)),
                        metadata={"provider": "html_search"},
                    )
                )
        except requests.RequestException as exc:
            print(f"Fact-check fallback failed: {exc}")

    return records

