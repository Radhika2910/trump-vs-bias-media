from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from src.settings import DATA_DIR, settings


TABLE_NAME = "analysis_records"


def _sqlite_path() -> Path:
    return DATA_DIR / "project.db"


def save_dataframe(df: pd.DataFrame) -> None:
    if df.empty:
        print("No records to store.")
        return
    df = df.copy()
    for column in df.columns:
        if df[column].map(lambda value: isinstance(value, (dict, list))).any():
            df[column] = df[column].apply(lambda value: json.dumps(value) if isinstance(value, (dict, list)) else value)

    if settings.database_url.startswith("mongodb"):
        from pymongo import MongoClient

        client = MongoClient(settings.database_url)
        db = client.get_default_database() or client["trump_media_bias"]
        db[TABLE_NAME].delete_many({})
        db[TABLE_NAME].insert_many(json.loads(df.to_json(orient="records")))
        return

    if settings.database_url.startswith("sqlite"):
        path = _sqlite_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        return

    from sqlalchemy import create_engine
    engine = create_engine(settings.database_url)
    df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)


def load_dataframe() -> pd.DataFrame:
    if settings.database_url.startswith("mongodb"):
        from pymongo import MongoClient

        client = MongoClient(settings.database_url)
        db = client.get_default_database() or client["trump_media_bias"]
        rows = list(db[TABLE_NAME].find({}, {"_id": 0}))
        return pd.DataFrame(rows)

    path = _sqlite_path()
    if not path.exists():
        return pd.DataFrame()
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
