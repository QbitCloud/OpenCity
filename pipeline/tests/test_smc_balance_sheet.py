import unittest
from unittest.mock import patch

from opencity.model import Raw
from opencity.sources import smc_balance_sheet as balance_sheet


STATEMENT = '''
INCOME AND EXPENDITURE ACCOUNT FOR THE YEAR ENDED 31 MARCH, 2026
Income                                      Sch. No.       2025-2026       2024-2025
Tax Revenues                                13             20,80,52,10,307.45 20,30,84,40,797.35
Non Tax Revenues                            14             14,66,33,03,994.34 15,64,18,09,256.70
Govt. Grants, Contri. & Subsidies           15             1,87,32,65,973.00  1,97,23,38,521.26
Compensation in lieu of Octroi              16             8,56,71,49,755.00  7,90,17,40,065.00
Other Income                                17             2,13,90,31,223.60  1,91,03,37,435.04
                                                       48,04,79,61,253.39 47,73,46,66,075.35
Expenditure
Payments & Benefits to Employees            18             22,30,03,31,378.70 21,16,61,47,774.99
Administration Expenses                     19             4,97,31,45,399.53  5,04,56,93,657.58
Loss on Sale of Assets                                      1,00,000.00     2,00,000.00
                                                       49,04,25,10,762.27 47,03,18,30,466.22
Net Surplus for the year before taxation                   -99,45,49,508.88 70,28,35,609.13
Excess of Income Over Expenditure                          69,29,80,756.47 85,66,71,011.92
Notes forming part of Accounts
'''


def raw() -> Raw:
    return Raw('file://balance-sheet.pdf', b'%PDF', 'application/pdf', 0, '', True, '2026-10-01T00:00:00+05:30')


class TestSmcBalanceSheet(unittest.TestCase):
    @patch.object(balance_sheet, 'pdf_text', return_value=STATEMENT)
    def test_parses_income_statement_for_both_financial_years(self, _pdf_text):
        result = balance_sheet.parse(raw())
        balance_sheet.validate(result, raw())

        self.assertEqual(len(result.observations), 20)
        values = {(o.metric_id, o.period_start): o.value for o in result.observations}
        self.assertEqual(values['finance.tax_revenue', '2025-04-01'], 20805210307.45)
        self.assertEqual(values['finance.total_income', '2024-04-01'], 47734666075.35)
        self.assertEqual(values['finance.net_surplus_before_tax', '2025-04-01'], -994549508.88)

    @patch.object(balance_sheet, 'pdf_text', return_value='not a balance sheet')
    def test_rejects_pdf_without_the_income_statement(self, _pdf_text):
        with self.assertRaisesRegex(Exception, 'income and expenditure'):
            balance_sheet.parse(raw())
