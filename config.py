"""Central paths and runtime settings for the anime ETL pipeline."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
REPORT_DIR = BASE_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"

PROCESSED_FILE = PROCESSED_DIR / "anime_clean.csv"
DATABASE_FILE = DATABASE_DIR / "anime.db"
QUALITY_REPORT_FILE = REPORT_DIR / "data_quality_report.txt"
INVALID_RECORDS_FILE = REPORT_DIR / "invalid_records.csv"

JIKAN_API_URL = os.getenv("JIKAN_API_URL", "https://api.jikan.moe/v4/anime")
REQUEST_TIMEOUT = float(os.getenv("ANIME_ETL_REQUEST_TIMEOUT", "30"))
REQUEST_DELAY = float(os.getenv("ANIME_ETL_REQUEST_DELAY", "1"))
MAX_RETRIES = int(os.getenv("ANIME_ETL_MAX_RETRIES", "5"))


def ensure_directories() -> None:
    for directory in (RAW_DIR, PROCESSED_DIR, DATABASE_DIR, REPORT_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
