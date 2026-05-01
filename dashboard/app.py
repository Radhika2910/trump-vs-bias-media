from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.settings import PROCESSED_DIR, SAMPLE_DIR  # noqa: E402
from src.storage.database import load_dataframe  # noqa: E402
from src.utils import read_jsonl  # noqa: E402
from src.nlp.analysis import analyze_records  # noqa: E402


st.set_page_config(page_title="Trump vs Media Bias", layout="wide")
st.title("Trump vs Media Bias Analysis")


@st.cache_data
def load_data() -> pd.DataFrame:
    db_df = load_dataframe()
    if not db_df.empty:
        return db_df

    processed = PROCESSED_DIR / "analysis_records.csv"
    if processed.exists():
        return pd.read_csv(processed)

    sample_rows = read_jsonl(SAMPLE_DIR / "sample_records.jsonl")
    return analyze_records(sample_rows)


df = load_data()

if df.empty:
    st.warning("No data found. Run the pipeline or use the included sample dataset.")
    st.stop()

source_types = st.sidebar.multiselect("Source type", sorted(df["source_type"].dropna().unique()), default=sorted(df["source_type"].dropna().unique()))
biases = st.sidebar.multiselect("Media bias", sorted(df["media_bias"].dropna().unique()), default=sorted(df["media_bias"].dropna().unique()))

filtered = df[df["source_type"].isin(source_types) & df["media_bias"].isin(biases)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Records", len(filtered))
col2.metric("News/Tweets", int(filtered["source_type"].isin(["news", "tweet"]).sum()))
col3.metric("Fact Checks", int((filtered["source_type"] == "fact_check").sum()))
col4.metric("Known Bias Sources", int((filtered["media_bias"] != "unknown").sum()))

left, right = st.columns(2)
with left:
    sentiment_counts = filtered.groupby(["source_type", "sentiment"]).size().reset_index(name="count")
    st.plotly_chart(px.bar(sentiment_counts, x="sentiment", y="count", color="source_type", barmode="group", title="Sentiment by Source Type"), use_container_width=True)

with right:
    bias_counts = filtered["media_bias"].value_counts().reset_index()
    bias_counts.columns = ["media_bias", "count"]
    st.plotly_chart(px.pie(bias_counts, names="media_bias", values="count", title="Media Bias Distribution"), use_container_width=True)

trend_df = filtered.dropna(subset=["published_date"])
if not trend_df.empty:
    trend = trend_df.groupby(["published_date", "sentiment"]).size().reset_index(name="count")
    st.plotly_chart(px.line(trend, x="published_date", y="count", color="sentiment", markers=True, title="Sentiment Trends"), use_container_width=True)

fact_df = filtered[filtered["source_type"] == "fact_check"]
if not fact_df.empty:
    truth = fact_df["truth_bucket"].value_counts().reset_index()
    truth.columns = ["truth_bucket", "count"]
    st.plotly_chart(px.bar(truth, x="truth_bucket", y="count", title="Truth vs False Claim Ratio"), use_container_width=True)

st.subheader("Records")
st.dataframe(filtered[["source_type", "source_name", "title", "sentiment", "media_bias", "verdict", "url"]], use_container_width=True)

