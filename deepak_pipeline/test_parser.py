import unittest

from deepak_pipeline.parser import read_balance_sheet_text, read_water_quality_text


SAMPLE_BALANCE_SHEET = """
INCOME AND EXPENDITURE ACCOUNT FOR THE YEAR ENDED 31 MARCH, 2025

Tax Revenues                         1,300.00  1,120.00
Non Tax Revenues                       420.00    390.00
                                  2,860.00  2,540.00
Expenditure
                                  2,540.00  2,310.00
Net Surplus for the year before taxation
"""


class TestFinanceParser(unittest.TestCase):
    def test_reads_finance_values_from_balance_sheet_text(self):
        finance_data = read_balance_sheet_text(SAMPLE_BALANCE_SHEET)

        self.assertEqual(finance_data["financial_year"], "2024-25")
        self.assertEqual(finance_data["amount_unit"], "INR")
        self.assertEqual(finance_data["finance.total_income"], 2860.00)
        self.assertEqual(finance_data["finance.total_expenditure"], 2540.00)
        self.assertEqual(finance_data["finance.tax_revenue"], 1300.00)
        self.assertEqual(finance_data["finance.operating_balance"], 320.00)

    def test_reads_an_older_as_on_march_date(self):
        older_text = SAMPLE_BALANCE_SHEET.replace(
            "FOR THE YEAR ENDED 31 MARCH, 2025",
            "As on 31st March 2006",
        )

        finance_data = read_balance_sheet_text(older_text)

        self.assertEqual(finance_data["financial_year"], "2005-06")

    def test_reads_water_sample_totals(self):
        report_text = """
            Monthly laboratory report
            City total      ૧,૨૩૪     1,220     14
        """

        water_data = read_water_quality_text(report_text, 2025, 1)

        self.assertEqual(water_data["period_start"], "2025-01-01")
        self.assertEqual(water_data["samples_collected"], 1234)
        self.assertEqual(water_data["samples_fit"], 1220)
        self.assertEqual(water_data["samples_unfit"], 14)
        self.assertEqual(water_data["compliance_rate_percent"], 98.87)
