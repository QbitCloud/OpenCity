import unittest
from unittest.mock import patch

from deepak_pipeline.scrapper import discover_balance_sheets


class FakeResponse:
    text = """
        <a href='/files/BalanceSheet_22_23.pdf'>2022-23</a>
        <a href='/files/BalanceSheet_21_22.pdf'>2021-22</a>
        <a href='/files/other.pdf'>Other</a>
    """

    def raise_for_status(self):
        return None


class TestFinanceDiscovery(unittest.TestCase):
    @patch("deepak_pipeline.scrapper.requests.get", return_value=FakeResponse())
    def test_discovers_and_sorts_balance_sheets(self, _get):
        reports = discover_balance_sheets()
        self.assertEqual(list(reports), [2021, 2022])
        self.assertTrue(reports[2022].endswith("BalanceSheet_22_23.pdf"))
