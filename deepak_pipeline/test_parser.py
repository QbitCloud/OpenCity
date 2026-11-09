import unittest

from deepak_pipeline.parser import read_balance_sheet_text


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
