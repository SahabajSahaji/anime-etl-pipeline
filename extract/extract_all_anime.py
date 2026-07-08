"""Resumable extraction of paginated anime records from the Jikan API."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

from config import (
    JIKAN_API_URL,
    MAX_RETRIES,
    RAW_DIR,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    ensure_directories,
)

LOGGER = logging.getLogger(__name__)


def _existing_pages(raw_dir: Path) -> set[int]:
    pages: set[int] = set()
    for path in raw_dir.glob("anime_page_*.json"):
        try:
            pages.add(int(path.stem.rsplit("_", 1)[1]))
        except (IndexError, ValueError):
            LOGGER.warning("Ignoring unexpected raw filename: %s", path.name)
    return pages


def _fetch_page(session: requests.Session, page: int) -> dict[str, Any]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                JIKAN_API_URL, params={"page": page}, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload.get("data"), list) or "pagination" not in payload:
                raise ValueError("API response is missing data or pagination")
            return payload
        except (requests.RequestException, ValueError) as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to extract page {page} after {MAX_RETRIES} attempts"
                ) from exc
            delay = min(2 ** (attempt - 1), 30)
            LOGGER.warning("Page %s failed (%s); retrying in %ss", page, exc, delay)
            time.sleep(delay)
    raise AssertionError("unreachable")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    os.replace(temporary, path)


def extract_all_anime(
    start_page: int | None = None,
    max_pages: int | None = None,
    overwrite: bool = False,
    session: requests.Session | None = None,
) -> int:
    """Extract pages, resume around existing files, and return pages downloaded."""
    ensure_directories()
    existing = _existing_pages(RAW_DIR)
    page = start_page or (max(existing, default=0) + 1)
    if page < 1:
        raise ValueError("start_page must be positive")

    downloaded = 0
    client = session or requests.Session()
    while max_pages is None or downloaded < max_pages:
        destination = RAW_DIR / f"anime_page_{page}.json"
        if destination.exists() and not overwrite:
            LOGGER.info("Skipping existing page %s", page)
            page += 1
            continue

        payload = _fetch_page(client, page)
        _write_json_atomic(destination, payload)
        downloaded += 1
        LOGGER.info("Saved page %s", page)

        if not payload["pagination"].get("has_next_page", False):
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    LOGGER.info("Extraction complete: %s page(s) downloaded", downloaded)
    return downloaded
