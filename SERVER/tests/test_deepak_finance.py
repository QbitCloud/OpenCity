import unittest
from unittest.mock import patch

from fastapi import HTTPException

from SERVER.api.routes import deepak_finance_analysis
from SERVER.services.deepak_finance import load_deepak_finance_analysis


def observation(financial_year, metric_id, value):
    return {
        "financial_year": financial_year,
        "metric_id": metric_id,
        "value": value,
        "amount_unit": "INR",
        "source_url": f"https://example.test/{financial_year}.pdf",
    }


class TestDeepakFinanceAnalysis(unittest.TestCase):
    def test_builds_history_and_three_year_forecast(self):
        rows = []
        for year, income, expenditure in [
            ("2021-22", 100.0, 80.0),
            ("2022-23", 140.0, 100.0),
            ("2023-24", 160.0, 120.0),
            ("2024-25", 200.0, 150.0),
        ]:
            rows.extend(
                [
                    observation(year, "finance.total_income", income),
                    observation(year, "finance.total_expenditure", expenditure),
                    observation(year, "finance.operating_balance", income - expenditure),
                ]
            )

        with patch("SERVER.services.deepak_finance.read_finance_observations", return_value=rows):
            result = load_deepak_finance_analysis()

        self.assertEqual(len(result["history"]), 4)
        self.assertEqual(result["latest"]["income_change_percent"], 25.0)
        self.assertEqual(result["forecast"]["financial_year"], "2025-26")
        self.assertEqual(result["forecast"]["estimated_income"], 166.67)
        self.assertEqual(result["forecast"]["estimated_expenditure"], 123.33)

    def test_endpoint_reports_missing_history(self):
        with patch(
            "SERVER.api.routes.load_deepak_finance_analysis",
            return_value={"history": [], "latest": None, "forecast": None},
        ):
            with self.assertRaises(HTTPException) as error:
                deepak_finance_analysis()

        self.assertEqual(error.exception.status_code, 503)
