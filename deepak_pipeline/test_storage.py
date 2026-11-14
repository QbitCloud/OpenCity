import unittest
from unittest.mock import MagicMock, patch

from deepak_pipeline import db


class TestFinanceStorage(unittest.TestCase):
    def setUp(self):
        self.documents = MagicMock()
        self.observations = MagicMock()
        self.database = {
            db.DOCUMENTS: self.documents,
            db.OBSERVATIONS: self.observations,
        }

    def test_saves_a_document_by_financial_year(self):
        db.save_document(
            self.database,
            "FY 2024-25",
            "https://example.test/2024-25.pdf",
            "2026-11-14T10:00:00+05:30",
        )

        self.documents.update_one.assert_called_once_with(
            {"financial_year": "FY 2024-25"},
            {
                "$set": {
                    "financial_year": "FY 2024-25",
                    "url": "https://example.test/2024-25.pdf",
                    "discovered_at": "2026-11-14T10:00:00+05:30",
                }
            },
            upsert=True,
        )

    def test_saves_each_finance_metric_with_an_upsert(self):
        finance_data = {
            "financial_year": "2024-25",
            "amount_unit": "INR",
            "finance.total_income": 2860.00,
            "finance.total_expenditure": 2540.00,
        }

        db.save_finance_year(
            self.database,
            finance_data,
            "https://example.test/2024-25.pdf",
        )

        self.assertEqual(self.observations.update_one.call_count, 2)

    def test_reads_sorted_observations(self):
        self.observations.find.return_value.sort.return_value = [
            {"financial_year": "2024-25", "metric_id": "finance.total_income"}
        ]

        with patch("deepak_pipeline.db.connect", return_value=self.database):
            rows = db.read_finance_observations()

        self.assertEqual(rows[0]["financial_year"], "2024-25")
