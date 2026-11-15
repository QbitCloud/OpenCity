import unittest

from UI.analysis.finance_analysis import finance_analysis
from UI.analysis.water_analysis import water_analysis


class TestDashboardAnalysis(unittest.TestCase):
    def test_finance_converts_display_values_to_crore(self):
        history = [
            {
                "financial_year": "2024-25",
                "income": 20_000_000,
                "expenditure": 15_000_000,
                "operating_balance": 5_000_000,
                "tax_revenue": 8_000_000,
                "non_tax_revenue": 4_000_000,
                "tax_revenue_share_percent": 40,
                "source_url": "https://example.test/finance.pdf",
            }
        ]

        result = finance_analysis(history, "2024-25")

        self.assertEqual(result["history_crore"].loc["2024-25", "income"], 2)
        self.assertEqual(result["revenue_mix"].loc["Tax revenue", "₹ crore"], 0.8)

    def test_water_lists_latest_month_first(self):
        history = [
            {
                "period_start": "2025-01-01",
                "samples_collected": 100,
                "samples_fit": 99,
                "samples_unfit": 1,
                "compliance_rate_percent": 99,
                "source_url": "https://example.test/january.pdf",
            },
            {
                "period_start": "2025-02-01",
                "samples_collected": 100,
                "samples_fit": 98,
                "samples_unfit": 2,
                "compliance_rate_percent": 98,
                "source_url": "https://example.test/february.pdf",
            },
        ]

        result = water_analysis(history)

        self.assertEqual(result["summary_rows"].iloc[0]["Month"], "Feb 2025")
