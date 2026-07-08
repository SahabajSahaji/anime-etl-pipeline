"""Transform raw Jikan pages into one deterministic, deduplicated CSV."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from config import PROCESSED_FILE, RAW_DIR, ensure_directories

LOGGER = logging.getLogger(__name__)

COLUMNS = [
    "mal_id", "title", "episodes", "status", "aired", "duration", "rating",
    "score", "scored_by", "MyAnimeList_Rank", "popularity", "members",
    "favorites", "year", "season", "studios", "genres",
]


def _page_number(path: Path) -> int:
    try:
        return int(path.stem.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0


def _names(values: Iterable[dict[str, Any]] | None) -> str:
    return ", ".join(
        str(item["name"]) for item in (values or []) if item.get("name")
    )


def _record(anime: dict[str, Any]) -> dict[str, Any]:
    aired = anime.get("aired") or {}
    return {
        "mal_id": anime.get("mal_id"),
        "title": anime.get("title_english") or anime.get("title"),
        "episodes": anime.get("episodes"),
        "status": anime.get("status"),
        "aired": aired.get("string"),
        "duration": anime.get("duration"),
        "rating": anime.get("rating"),
        "score": anime.get("score"),
        "scored_by": anime.get("scored_by"),
        "MyAnimeList_Rank": anime.get("rank"),
        "popularity": anime.get("popularity"),
        "members": anime.get("members"),
        "favorites": anime.get("favorites"),
        "year": anime.get("year"),
        "season": anime.get("season"),
        "studios": _names(anime.get("studios")),
        "genres": _names(anime.get("genres")),
    }


def transform_anime(
    raw_dir: Path = RAW_DIR, output_file: Path = PROCESSED_FILE
) -> pd.DataFrame:
    """Build the processed dataset from scratch so reruns are idempotent."""
    ensure_directories()
    files = sorted(raw_dir.glob("anime_page_*.json"), key=_page_number)
    if not files:
        raise FileNotFoundError(f"No raw anime pages found in {raw_dir}")

    records: list[dict[str, Any]] = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            data = payload.get("data")
            if not isinstance(data, list):
                raise ValueError("'data' must be a list")
            records.extend(_record(anime) for anime in data)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"Invalid raw page {path.name}: {exc}") from exc

    frame = pd.DataFrame.from_records(records, columns=COLUMNS)
    before = len(frame)
    frame = frame.dropna(subset=["mal_id"]).drop_duplicates("mal_id", keep="last")
    frame = frame.sort_values("mal_id").reset_index(drop=True)

    temporary = output_file.with_suffix(".csv.tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8")
    os.replace(temporary, output_file)
    LOGGER.info(
        "Transformation complete: %s rows (%s duplicates removed)",
        len(frame), before - len(frame),
    )
    return frame


if __name__ == "__main__":
    from pipeline_logging import configure_logging
    configure_logging()
    transform_anime()
