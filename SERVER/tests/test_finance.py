import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from SERVER.api.routes import finance_summary


class TestFinanceSummary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "finance.csv"
        patcher = patch("SERVER.services.finance.CSV_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_csv(self, rows):
        columns = [
            "metric_id", "geo_level", "geo_code", "period_start", "value", "status",
            "source_url", "retrieved_at",
        ]
        with self.path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def test_returns_the_latest_financial_year(self):
        self.write_csv([
            {
                "metric_id": "finance.total_income", "geo_level": "smc_city", "geo_code": "smc",
                "period_start": "2024-04-01", "value": "100", "status": "reported",
                "source_url": "https://example.test/balance-sheet", "retrieved_at": "2026-10-28",
            },
            {
                "metric_id": "finance.total_income", "geo_level": "smc_city", "geo_code": "smc",
                "period_start": "2025-04-01", "value": "200", "status": "reported",
                "source_url": "https://example.test/balance-sheet", "retrieved_at": "2026-10-28",
            },
            {
                "metric_id": "finance.tax_revenue", "geo_level": "smc_city", "geo_code": "smc",
                "period_start": "2025-04-01", "value": "150", "status": "reported",
                "source_url": "https://example.test/balance-sheet", "retrieved_at": "2026-10-28",
            },
        ])

        result = finance_summary()

        self.assertEqual(result["financial_year"], "FY 2025-26")
        self.assertEqual(result["metrics"][0]["value"], 200.0)
        self.assertEqual(result["metrics"][1]["label"], "Tax revenue")

    def test_missing_csv_returns_service_unavailable(self):
        with self.assertRaises(HTTPException) as error:
            finance_summary()
        self.assertEqual(error.exception.status_code, 503)
