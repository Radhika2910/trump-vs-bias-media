# Trump vs Media Bias Analysis

This project analyzes Donald Trump's claim that media coverage about him is false or biased.
It collects live data from X, news APIs, and fact-checking websites, then performs sentiment,
media-bias, and truth-ratio analysis.

The project is intentionally simple for beginners. The main analysis interface is now a
JupyterLab notebook, so the EDA and transformation steps are visible and easy to modify.

## Folder Structure

```text
trump-vs-bias-media/
├── config/
│   └── media_bias_sources.csv
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│       └── sample_records.jsonl
├── notebooks/
│   └── trump_media_bias_analysis.ipynb
├── scripts/
├── src/
│   ├── collectors/
│   │   ├── fact_checks.py
│   │   ├── news_apis.py
│   │   └── x_api.py
│   ├── nlp/
│   │   ├── analysis.py
│   │   └── preprocess.py
│   ├── pipeline/
│   │   ├── run_collection.py
│   │   └── sample_loader.py
│   ├── storage/
│   │   └── database.py
│   ├── schema.py
│   ├── settings.py
│   └── utils.py
├── .env.example
├── requirements.txt
└── run_pipeline.py
```

## What It Collects

- X posts about Trump and media bias
- News articles from NewsAPI, GNews, and Mediastack
- Fact-check entries from PolitiFact, Snopes, and FactCheck.org RSS/search pages

Default queries are defined in `src/schema.py`.

## What It Analyzes

- Sentiment of tweets and news articles using TextBlob
- Media-bias category using a starter AllSides/AdFontes-style lookup in `config/media_bias_sources.csv`
- Truth ratio from fact-check verdicts such as `False`, `Mostly False`, `True`, and `Mixture`

The bias lookup is a starter dataset. For a real paper or presentation, cite and manually verify
ratings from AllSides and Ad Fontes Media before making conclusions.

## Setup

```bash
cd /home/radhika/workspace/trump-vs-bias-media
python -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Then add your API keys in `.env`:

```text
X_BEARER_TOKEN=...
NEWSAPI_KEY=...
GNEWS_KEY=...
MEDIASTACK_KEY=...
```

The database defaults to local SQLite at `data/project.db`. You can also use MongoDB by setting:

```text
DATABASE_URL=mongodb://localhost:27017/trump_media_bias
```

## Run With Sample Data

Use this first. It does not require API keys.

```bash
python3 run_pipeline.py --sample
jupyter lab notebooks/trump_media_bias_analysis.ipynb
```

## Run With Live Data

Collect for the configured 2-3 day window:

```bash
python3 run_pipeline.py
jupyter lab notebooks/trump_media_bias_analysis.ipynb
```

Outputs:

- Raw JSONL: `data/raw/collected_records.jsonl`
- Processed CSV: `data/processed/analysis_records.csv`
- Database: `data/project.db` by default

## Beginner Workflow

1. Run the sample pipeline.
2. Open `notebooks/trump_media_bias_analysis.ipynb` in JupyterLab.
3. Add API keys.
4. Run live collection once per day for 2-3 days.
5. Re-run the notebook cells to refresh EDA, transformations, and charts.
6. Export charts and CSVs for your report.

## Notebook Contents

The main notebook includes:

- data loading from processed, raw, or sample records
- reusable data transformation with `analyze_records()`
- missing-value and source-count EDA
- sentiment distribution and sentiment-over-time charts
- media-bias distribution and sentiment-by-bias charts
- fact-check truth-vs-false ratio
- evidence table for inspecting source records
- conclusion template for a beginner research write-up

## Optional Model Tools

The old notebook template includes XGBoost experiments. Install optional packages only if you
want to run those notebooks:

```bash
python3 -m pip install -r requirements-optional.txt
```

## Research Caution

This project can show patterns in sentiment, source distribution, and fact-check outcomes.
It cannot prove all media coverage is biased or unbiased by itself. Treat the result as evidence
for a focused dataset and time window, then explain limitations clearly.
