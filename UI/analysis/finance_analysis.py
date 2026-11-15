"""Turn Finance API history into clear dashboard values."""
from __future__ import annotations

import pandas as pd


def rupees_in_crore(value: float | None) -> str:
    """Format an INR amount in crore, the scale used for the public charts."""
    if value is None or pd.isna(value):
        return "Not reported"
    return f"₹{value / 10_000_000:,.1f} crore"


def percent(value: float | None) -> str:
    """Format a percentage without inventing a value for missing data."""
    if value is None or pd.isna(value):
        return "Not reported"
    return f"{value:.1f}%"


def finance_analysis(history: list[dict], financial_year: str) -> dict:
    """Prepare selected-year and historic Finance data for the page."""
    data = pd.DataFrame(history).sort_values("financial_year")
    selected = data.loc[data["financial_year"] == financial_year].iloc[0]

    in_crore = data.copy()
    for column in ["income", "expenditure", "operating_balance", "tax_revenue", "non_tax_revenue"]:
        if column in in_crore:
            in_crore[column] = in_crore[column] / 10_000_000

    revenue_mix = pd.DataFrame(
        {
            "₹ crore": [
                selected.get("tax_revenue", float("nan")) / 10_000_000,
                selected.get("non_tax_revenue", float("nan")) / 10_000_000,
            ]
        },
        index=["Tax revenue", "Non-tax revenue"],
    ).dropna()

    summary_rows = in_crore[
        [
            "financial_year",
            "income",
            "expenditure",
            "operating_balance",
            "tax_revenue",
            "non_tax_revenue",
            "tax_revenue_share_percent",
            "source_url",
        ]
    ].rename(
        columns={
            "financial_year": "Financial year",
            "income": "Income (₹ crore)",
            "expenditure": "Expenditure (₹ crore)",
            "operating_balance": "Operating balance (₹ crore)",
            "tax_revenue": "Tax revenue (₹ crore)",
            "non_tax_revenue": "Non-tax revenue (₹ crore)",
            "tax_revenue_share_percent": "Tax revenue share (%)",
            "source_url": "Official source",
        }
    )
    summary_rows = summary_rows.round(
        {
            "Income (₹ crore)": 2,
            "Expenditure (₹ crore)": 2,
            "Operating balance (₹ crore)": 2,
            "Tax revenue (₹ crore)": 2,
            "Non-tax revenue (₹ crore)": 2,
            "Tax revenue share (%)": 2,
        }
    )

    return {
        "selected": selected,
        "history_crore": in_crore.set_index("financial_year"),
        "revenue_mix": revenue_mix,
        "summary_rows": summary_rows,
    }
