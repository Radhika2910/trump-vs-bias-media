from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Allows the sample pipeline to run before optional deps are installed.
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DIR = DATA_DIR / "sample"


load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    x_bearer_token: str = os.getenv("X_BEARER_TOKEN", "")
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    gnews_key: str = os.getenv("GNEWS_KEY", "")
    mediastack_key: str = os.getenv("MEDIASTACK_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'project.db'}")
    collection_days: int = int(os.getenv("COLLECTION_DAYS", "3"))
    max_items_per_source: int = int(os.getenv("MAX_ITEMS_PER_SOURCE", "100"))

    @property
    def using_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


settings = Settings()


def ensure_data_dirs() -> None:
    for directory in (RAW_DIR, PROCESSED_DIR, SAMPLE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
