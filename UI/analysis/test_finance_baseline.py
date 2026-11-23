"""Checks for the Finance baseline flags."""
from __future__ import annotations

import unittest

from analysis.finance_baseline import finance_baseline


class FinanceBaselineTests(unittest.TestCase):
    def test_green_finance_values_receive_a_green_score(self) -> None:
        result = finance_baseline(8.0, 1.0, 55.0, 3)

        self.assertEqual(result["score"], 100)
        self.assertEqual(result["status"], "Green")

    def test_negative_margin_is_flagged(self) -> None:
        result = finance_baseline(-2.0, 1.0, 55.0, 3)

        self.assertEqual(result["components"][0]["status"], "Orange")

    def test_missing_finance_value_does_not_make_a_score(self) -> None:
        result = finance_baseline(2.0, None, 55.0, 3)

        self.assertIsNone(result["score"])
        self.assertEqual(result["status"], "Not enough data")


if __name__ == "__main__":
    unittest.main()
