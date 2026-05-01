from __future__ import annotations

import pandas as pd
from textblob import TextBlob

from src.nlp.preprocess import clean_text


BIAS_LOOKUP = {
    "abc news": "leans left",
    "associated press": "center",
    "ap news": "center",
    "bbc news": "center",
    "breitbart": "right",
    "cnn": "left",
    "fox news": "right",
    "msnbc": "left",
    "new york post": "right",
    "new york times": "leans left",
    "politico": "leans left",
    "reuters": "center",
    "the guardian": "left",
    "the hill": "center",
    "the wall street journal": "leans right",
    "usa today": "leans left",
    "washington post": "leans left",
}


FALSE_VERDICTS = {"false", "mostly false", "pants on fire", "four pinocchios"}
TRUE_VERDICTS = {"true", "mostly true", "half true"}


def sentiment_label(polarity: float) -> str:
    if polarity > 0.05:
        return "positive"
    if polarity < -0.05:
        return "negative"
    return "neutral"


def source_bias(source_name: str) -> str:
    source = str(source_name).lower()
    for known_source, bias in BIAS_LOOKUP.items():
        if known_source in source:
            return bias
    return "unknown"


def truth_bucket(verdict: str) -> str:
    normalized = str(verdict).strip().lower()
    if normalized in FALSE_VERDICTS:
        return "false_or_mostly_false"
    if normalized in TRUE_VERDICTS:
        return "true_or_partly_true"
    if normalized in {"mixture", "mixed", "unproven", "unknown"}:
        return normalized
    return "unknown"


def analyze_records(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["clean_text"] = df["text"].fillna("").apply(clean_text)
    df["sentiment_score"] = df["clean_text"].apply(lambda text: TextBlob(text).sentiment.polarity)
    df["sentiment"] = df["sentiment_score"].apply(sentiment_label)
    df["media_bias"] = df["source_name"].apply(source_bias)
    df["truth_bucket"] = df["verdict"].apply(truth_bucket)
    df["published_date"] = pd.to_datetime(df["published_at"], errors="coerce").dt.date.astype("string")
    return df

