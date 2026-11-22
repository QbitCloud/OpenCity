import unittest
from unittest.mock import patch

from fastapi import HTTPException

from SERVER.api.routes import deepak_water_analysis
from SERVER.services.deepak_water import load_deepak_water_analysis


def observation(period_start, metric_id, value):
    return {
        "period_start": period_start,
        "metric_id": metric_id,
        "value": value,
        "source_url": f"https://example.test/{period_start}.pdf",
    }


class TestDeepakWaterAnalysis(unittest.TestCase):
    def test_builds_monthly_history(self):
        rows = [
            observation("2025-01-01", "water.samples_collected", 100),
            observation("2025-01-01", "water.samples_fit", 97),
            observation("2025-01-01", "water.samples_unfit", 3),
            observation("2025-01-01", "water.compliance_rate_percent", 97),
        ]

        with patch("SERVER.services.deepak_water.read_water_observations", return_value=rows):
            result = load_deepak_water_analysis()

        self.assertEqual(result["latest"]["samples_unfit"], 3)
        self.assertEqual(result["latest"]["compliance_rate_percent"], 97)
        self.assertEqual(result["reporting"]["reported_months"], 1)

    def test_endpoint_reports_missing_history(self):
        with patch(
            "SERVER.api.routes.load_deepak_water_analysis",
            return_value={"history": [], "latest": None, "reporting": {}},
        ):
            with self.assertRaises(HTTPException) as error:
                deepak_water_analysis()

        self.assertEqual(error.exception.status_code, 503)
