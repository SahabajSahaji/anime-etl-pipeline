"""Data-contract checks and quality reporting for transformed anime data."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config import (
    INVALID_RECORDS_FILE,
    PROCESSED_FILE,
    QUALITY_REPORT_FILE,
    ensure_directories,
)

LOGGER = logging.getLogger(__name__)
REQUIRED_COLUMNS = {
    "mal_id", "title", "episodes", "score", "genres", "studios", "year",
    "popularity",
}


def validate_anime(
    csv_file: Path = PROCESSED_FILE,
    report_file: Path = QUALITY_REPORT_FILE,
    invalid_records_file: Path = INVALID_RECORDS_FILE,
    fail_threshold: float | None = None,
) -> dict[str, float | int]:
    """Validate the processed dataset and optionally fail below a score threshold."""
    ensure_directories()
    frame = pd.read_csv(csv_file)
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if frame.empty:
        raise ValueError("Processed dataset is empty")

    checks = {
        "Missing Title": frame["title"].isna() | frame["title"].astype(str).str.strip().eq(""),
        "Missing Score": frame["score"].isna(),
        "Missing Genres": frame["genres"].isna() | frame["genres"].fillna("").str.strip().eq(""),
        "Missing Studios": frame["studios"].isna() | frame["studios"].fillna("").str.strip().eq(""),
        "Missing Year": frame["year"].isna(),
        "Missing Popularity": frame["popularity"].isna(),
        "Invalid Score": frame["score"].notna() & ~frame["score"].between(0, 10),
        "Invalid Episodes": frame["episodes"].notna() & frame["episodes"].lt(0),
        "Duplicate MAL ID": frame["mal_id"].duplicated(keep=False),
    }

    invalid_parts = []
    for issue, mask in checks.items():
        if mask.any():
            part = frame.loc[mask, ["mal_id", "title"]].copy()
            part["issue"] = issue
            invalid_parts.append(part)
    invalid = (
        pd.concat(invalid_parts, ignore_index=True)
        if invalid_parts
        else pd.DataFrame(columns=["mal_id", "title", "issue"])
    )
    invalid.to_csv(invalid_records_file, index=False, encoding="utf-8")

    failed_rows = pd.concat([mask for mask in checks.values()], axis=1).any(axis=1).sum()
    valid_rows = len(frame) - int(failed_rows)
    quality_score = valid_rows / len(frame) * 100
    metrics: dict[str, float | int] = {
        "total_records": len(frame),
        "valid_records": valid_rows,
        "records_with_issues": int(failed_rows),
        "total_issues": len(invalid),
        "quality_score": quality_score,
    }

    lines = [
        "===== DATA QUALITY REPORT =====", "",
        f"Total Records: {len(frame)}",
        f"Valid Records: {valid_rows}",
        f"Records With Issues: {failed_rows}", "",
    ]
    lines.extend(f"{name}: {int(mask.sum())}" for name, mask in checks.items())
    lines.extend(["", f"Total Issues: {len(invalid)}", f"Data Quality Score: {quality_score:.2f}%"])
    report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Validation complete: %.2f%% record quality", quality_score)

    if fail_threshold is not None and quality_score < fail_threshold:
        raise ValueError(
            f"Quality score {quality_score:.2f}% is below {fail_threshold:.2f}%"
        )
    return metrics


if __name__ == "__main__":
    from pipeline_logging import configure_logging
    configure_logging()
    validate_anime()
