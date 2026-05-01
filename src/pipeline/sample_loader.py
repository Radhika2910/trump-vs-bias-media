from __future__ import annotations

from src.settings import SAMPLE_DIR
from src.utils import read_jsonl


def load_sample_records() -> list[dict]:
    return read_jsonl(SAMPLE_DIR / "sample_records.jsonl")

