from __future__ import annotations

from src.nlp.analysis import analyze_records
from src.settings import PROCESSED_DIR, RAW_DIR, ensure_data_dirs
from src.storage.database import save_dataframe
from src.utils import save_jsonl


def main(use_sample: bool = False) -> None:
    ensure_data_dirs()

    if use_sample:
        from src.pipeline.sample_loader import load_sample_records

        records = load_sample_records()
    else:
        from src.collectors.fact_checks import collect_fact_checks
        from src.collectors.news_apis import collect_all_news
        from src.collectors.x_api import collect_x_posts

        records = collect_x_posts() + collect_all_news() + collect_fact_checks()

    rows = [record.to_dict() if hasattr(record, "to_dict") else record for record in records]
    save_jsonl(RAW_DIR / "collected_records.jsonl", rows)

    analyzed = analyze_records(rows)
    analyzed.to_csv(PROCESSED_DIR / "analysis_records.csv", index=False)
    save_dataframe(analyzed)

    print(f"Saved {len(analyzed)} analyzed records.")
    print(f"CSV: {PROCESSED_DIR / 'analysis_records.csv'}")


if __name__ == "__main__":
    main()
