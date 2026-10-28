import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from SERVER.api.routes import waste_collection


class TestWasteCollection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "waste.csv"

        patcher = patch(
            "SERVER.services.waste_collection.CSV_PATH",
            self.path,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_csv(self, rows):
        columns = [
            "metric_id", "geo_level", "geo_code", "dims",
            "period_start", "period_end", "value", "status",
            "source_url", "retrieved_at",
        ]
        with self.path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def test_available_data(self):
        self.write_csv([{
            "metric_id": "swm.avg_collection_mt_per_day",
            "geo_level": "smc_city",
            "geo_code": "smc",
            "dims": '{"mode":"door_to_door"}',
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "value": "100.5",
            "status": "reported",
            "source_url": "https://example.test/source",
            "retrieved_at": "2026-10-28",
        }])

        result = waste_collection()

        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["observations"][0]["value"], 100.5)
        self.assertEqual(result["unit"], "metric tonnes per day")

    def test_missing_csv(self):
        with self.assertRaises(HTTPException) as error:
            waste_collection()

        self.assertEqual(error.exception.status_code, 503)

    def test_empty_dataset(self):
        self.write_csv([])

        with self.assertRaises(HTTPException) as error:
            waste_collection()

        self.assertEqual(error.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
