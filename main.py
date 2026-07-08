"""Command-line entry point for the production anime ETL pipeline."""

from __future__ import annotations

import argparse
import logging
import time

from load.load_to_sqlite import load_to_sqlite
from pipeline_logging import configure_logging
from transform.transform_anime import transform_anime
from validation.validate_anime import validate_anime

LOGGER = logging.getLogger(__name__)


def run_pipeline(
    extract: bool = False,
    start_page: int | None = None,
    max_pages: int | None = None,
    quality_threshold: float | None = None,
) -> dict[str, float | int]:
    started = time.monotonic()
    if extract:
        from extract.extract_all_anime import extract_all_anime
        extract_all_anime(start_page=start_page, max_pages=max_pages)
    frame = transform_anime()
    metrics = validate_anime(fail_threshold=quality_threshold)
    loaded = load_to_sqlite()
    if loaded != len(frame):
        raise RuntimeError("Loaded row count does not match transformed row count")
    LOGGER.info("Pipeline succeeded in %.2fs", time.monotonic() - started)
    return metrics


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anime ETL pipeline")
    parser.add_argument("--extract", action="store_true", help="fetch new API pages first")
    parser.add_argument("--start-page", type=int, help="first API page to request")
    parser.add_argument("--max-pages", type=int, help="maximum API pages to download")
    parser.add_argument(
        "--quality-threshold", type=float,
        help="fail when record-level quality is below this percentage",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser


if __name__ == "__main__":
    args = _parser().parse_args()
    configure_logging(args.verbose)
    try:
        run_pipeline(
            extract=args.extract,
            start_page=args.start_page,
            max_pages=args.max_pages,
            quality_threshold=args.quality_threshold,
        )
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise SystemExit(1)
