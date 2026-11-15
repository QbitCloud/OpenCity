import tempfile
import unittest
from pathlib import Path

from deepak_pipeline import db


class TestFinanceStorage(unittest.TestCase):
    def setUp(self):
        self.temporary_folder = tempfile.TemporaryDirectory()
        self.original_database_path = db.DATABASE_PATH
        db.DATABASE_PATH = Path(self.temporary_folder.name) / "finance.db"

    def tearDown(self):
        db.DATABASE_PATH = self.original_database_path
        self.temporary_folder.cleanup()

    def test_saves_and_updates_a_finance_year(self):
        finance_data = {
            "financial_year": "2024-25",
            "amount_unit": "INR",
            "finance.total_income": 2860.00,
            "finance.total_expenditure": 2540.00,
        }

        connection = db.connect()
        db.save_finance_year(connection, finance_data, "https://example.test/one.pdf")

        finance_data["finance.total_income"] = 2900.00
        db.save_finance_year(connection, finance_data, "https://example.test/two.pdf")
        connection.close()

        observations = db.read_finance_observations()

        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[1]["value"], 2900.00)
        self.assertEqual(observations[1]["source_url"], "https://example.test/two.pdf")

    def test_saves_and_updates_a_water_month(self):
        water_data = {
            "period_start": "2025-01-01",
            "samples_collected": 1234,
            "samples_fit": 1220,
            "samples_unfit": 14,
            "compliance_rate_percent": 98.87,
        }

        connection = db.connect()
        db.save_water_month(connection, water_data, "https://example.test/one.pdf")
        water_data["samples_unfit"] = 12
        db.save_water_month(connection, water_data, "https://example.test/two.pdf")
        connection.close()

        observations = db.read_water_observations()

        self.assertEqual(len(observations), 4)
        unfit = next(item for item in observations if item["metric_id"] == "water.samples_unfit")
        self.assertEqual(unfit["value"], 12)
        self.assertEqual(unfit["source_url"], "https://example.test/two.pdf")
