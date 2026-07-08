"""Atomic SQLite loader for the processed anime dataset."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

import pandas as pd

from config import DATABASE_FILE, PROCESSED_FILE, ensure_directories

LOGGER = logging.getLogger(__name__)


def load_to_sqlite(
    csv_file: Path = PROCESSED_FILE, database_file: Path = DATABASE_FILE
) -> int:
    """Create a new indexed database and atomically replace the prior version."""
    ensure_directories()
    frame = pd.read_csv(csv_file)
    if frame.empty:
        raise ValueError("Refusing to load an empty dataset")
    if frame["mal_id"].isna().any() or frame["mal_id"].duplicated().any():
        raise ValueError("mal_id must be non-null and unique before loading")

    temporary = database_file.with_suffix(".db.tmp")
    temporary.unlink(missing_ok=True)
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(temporary)
        try:
            frame.to_sql("anime", connection, if_exists="fail", index=False, chunksize=1000)
            connection.executescript(
                """
                CREATE UNIQUE INDEX ux_anime_mal_id ON anime(mal_id);
                CREATE INDEX ix_anime_score ON anime(score);
                CREATE INDEX ix_anime_popularity ON anime(popularity);
                CREATE INDEX ix_anime_year ON anime(year);
                """
            )
            connection.execute("PRAGMA optimize")
            connection.commit()
        finally:
            connection.close()
            connection = None
        os.replace(temporary, database_file)
    except Exception:
        if connection is not None:
            connection.close()
        temporary.unlink(missing_ok=True)
        raise
    LOGGER.info("Loaded %s rows into %s", len(frame), database_file)
    return len(frame)


if __name__ == "__main__":
    from pipeline_logging import configure_logging
    configure_logging()
    load_to_sqlite()
