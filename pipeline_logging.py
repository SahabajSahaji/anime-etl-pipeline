"""Consistent console and rotating-file logging."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config import LOG_DIR, ensure_directories


def configure_logging(verbose: bool = False) -> None:
    ensure_directories()
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        LOG_DIR / "pipeline.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[console, file_handler], force=True)
