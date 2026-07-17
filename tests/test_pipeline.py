from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from load.load_to_sqlite import load_to_sqlite
from transform.transform_anime import transform_anime
from validation.validate_anime import validate_anime


def anime(mal_id: int, title: str, score: float | None = 8.0) -> dict:
    return {
        "mal_id": mal_id,
        "title": title,
        "title_english": None,
        "episodes": 12,
        "status": "Finished Airing",
        "aired": {"string": "2020"},
        "duration": "24 min",
        "rating": "PG-13",
        "score": score,
        "scored_by": 100,
        "rank": 1,
        "popularity": 10,
        "members": 1000,
        "favorites": 50,
        "year": 2020,
        "season": "spring",
        "studios": [{"name": "Studio A"}],
        "genres": [{"name": "Action"}],
    }


class PipelineTest(unittest.TestCase):
    def test_transform_validate_and_load_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            raw.mkdir()
            (raw / "anime_page_1.json").write_text(
                json.dumps({"data": [anime(1, "Old"), anime(2, "Second", None)]}),
                encoding="utf-8",
            )
            (raw / "anime_page_2.json").write_text(
                json.dumps({"data": [anime(1, "Updated")]}), encoding="utf-8"
            )
            csv_file = root / "anime.csv"
            report = root / "report.txt"
            invalid = root / "invalid.csv"
            database = root / "anime.db"

            frame = transform_anime(raw, csv_file)
            self.assertEqual(len(frame), 2)
            self.assertEqual(frame.loc[frame["mal_id"] == 1, "title"].item(), "Updated")

            metrics = validate_anime(csv_file, report, invalid)
            self.assertEqual(metrics["total_records"], 2)
            self.assertEqual(metrics["critical_records"],0)
            self.assertEqual(metrics["records_with_warnings"], 1)
            self.assertEqual(metrics["quality_score"], 100.0)

            self.assertEqual(load_to_sqlite(csv_file, database), 2)
            connection = sqlite3.connect(database)
            try:
                count, distinct = connection.execute(
                    "SELECT COUNT(*), COUNT(DISTINCT mal_id) FROM anime"
                ).fetchone()
                indexes = connection.execute("PRAGMA index_list(anime)").fetchall()
            finally:
                connection.close()
            self.assertEqual((count, distinct), (2, 2))
            self.assertTrue(any(row[1] == "ux_anime_mal_id" for row in indexes))

    def test_transform_rejects_malformed_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory)
            (raw / "anime_page_1.json").write_text("not json", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Invalid raw page"):
                transform_anime(raw, raw / "output.csv")


if __name__ == "__main__":
    unittest.main()
