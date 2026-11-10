"""Prepare Deepak's historic Finance data for the API."""
from __future__ import annotations

from deepak_pipeline.db import read_finance_observations


INCOME = "finance.total_income"
EXPENDITURE = "finance.total_expenditure"
BALANCE = "finance.operating_balance"


def percentage_change(current_value: float, previous_value: float | None) -> float | None:
    """Return year-on-year change, or None when comparison is not possible."""
    if previous_value in (None, 0):
        return None

    return round((current_value - previous_value) / previous_value * 100, 2)


def three_year_average(values: list[float]) -> float | None:
    """Use up to the latest three reported values for a clear estimate."""
    if not values:
        return None

    recent_values = values[-3:]
    return round(sum(recent_values) / len(recent_values), 2)


def next_financial_year(financial_year: str) -> str:
    """Turn 2025-26 into 2026-27."""
    ending_year = int(financial_year.split("-")[1]) + 2000
    return f"{ending_year}-{str(ending_year + 1)[-2:]}"


def build_history(observations: list[dict]) -> list[dict]:
    """Group individual metrics into one clear record per financial year."""
    years: dict[str, dict] = {}

    for observation in observations:
        financial_year = observation["financial_year"]
        row = years.setdefault(
            financial_year,
            {
                "financial_year": financial_year,
                "source_url": observation["source_url"],
            },
        )

        row[observation["metric_id"]] = observation["value"]

    history = []
    previous_income = None
    previous_expenditure = None

    for financial_year in sorted(years):
        row = years[financial_year]
        income = row.get(INCOME)
        expenditure = row.get(EXPENDITURE)

        if income is None or expenditure is None:
            continue

        history.append(
            {
                "financial_year": financial_year,
                "income": income,
                "expenditure": expenditure,
                "operating_balance": row.get(BALANCE, income - expenditure),
                "income_change_percent": percentage_change(income, previous_income),
                "expenditure_change_percent": percentage_change(
                    expenditure,
                    previous_expenditure,
                ),
                "source_url": row["source_url"],
            }
        )

        previous_income = income
        previous_expenditure = expenditure

    return history


def build_forecast(history: list[dict]) -> dict | None:
    """Estimate the next year from the latest three reported years."""
    if not history:
        return None

    estimated_income = three_year_average([row["income"] for row in history])
    estimated_expenditure = three_year_average(
        [row["expenditure"] for row in history]
    )

    return {
        "financial_year": next_financial_year(history[-1]["financial_year"]),
        "method": "three-year average",
        "estimated_income": estimated_income,
        "estimated_expenditure": estimated_expenditure,
        "estimated_operating_balance": round(
            estimated_income - estimated_expenditure,
            2,
        ),
        "status": "estimate, not an official SMC forecast",
    }


def load_deepak_finance_analysis() -> dict:
    """Return history and a cautious next-year Finance estimate."""
    history = build_history(read_finance_observations())

    return {
        "unit": "INR",
        "history": history,
        "latest": history[-1] if history else None,
        "forecast": build_forecast(history),
    }
