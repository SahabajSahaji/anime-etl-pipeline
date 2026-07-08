# Anime ETL Pipeline

A restartable ETL pipeline that extracts anime metadata from the Jikan API,
normalizes it into CSV, validates data quality, loads an indexed SQLite database,
and serves analytics through Streamlit.

## Architecture

```text
Jikan API -> data/raw/*.json -> data/processed/anime_clean.csv
          -> data quality reports -> data/database/anime.db -> dashboard
```

Raw pages are the immutable source layer. Transform and load stages rebuild their
outputs atomically, making repeated runs deterministic and safe.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

Rebuild from the existing raw snapshot without network access:

```bash
python main.py
```

Resume API extraction after the highest saved page, then rebuild all outputs:

```bash
python main.py --extract
```

Bounded extraction is useful for controlled jobs and testing:

```bash
python main.py --extract --start-page 1 --max-pages 5
```

Fail a scheduled run if fewer than a chosen percentage of records have no
quality issues:

```bash
python main.py --quality-threshold 20
```

Launch the dashboard from the repository root:

```bash
streamlit run dashboard/app.py
```

## Configuration

The following environment variables are supported:

| Variable | Default | Purpose |
|---|---:|---|
| `JIKAN_API_URL` | Jikan v4 anime endpoint | API endpoint |
| `ANIME_ETL_REQUEST_TIMEOUT` | `30` | HTTP timeout in seconds |
| `ANIME_ETL_REQUEST_DELAY` | `1` | Delay between successful pages |
| `ANIME_ETL_MAX_RETRIES` | `5` | Attempts per failed page |

Pipeline logs rotate under `logs/pipeline.log`. A failed stage exits with a
non-zero status, suitable for schedulers and CI.

## Data quality

`reports/data_quality_report.txt` summarizes completeness and validity.
`reports/invalid_records.csv` lists every issue. The quality score is the
percentage of records with no detected issues; it therefore remains between
0% and 100% even when one record has several issues.

## Test

```bash
python -m unittest discover -s tests -v
```
