"""Turn Finance API history into clear dashboard values."""
from __future__ import annotations

import pandas as pd

# Issue when tax revenue is below this % of total income (None = rule off)
TAX_SHARE_THRESHOLD = None


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


def largest_annual_change(data: pd.DataFrame) -> dict | None:
    """Find the largest reported income or expenditure change by magnitude."""
    candidates = []
    for column, label in [
        ("income_change_percent", "Income"),
        ("expenditure_change_percent", "Expenditure"),
    ]:
        if column not in data:
            continue
        for financial_year, value in data[column].dropna().items():
            candidates.append(
                {
                    "financial_year": financial_year,
                    "label": label,
                    "percent": value,
                }
            )

    return max(candidates, key=lambda item: abs(item["percent"])) if candidates else None


def finance_analysis(history: list[dict], financial_year: str) -> dict:
    """Prepare selected-year and historic Finance data for the page."""
    data = pd.DataFrame(history).sort_values("financial_year")
    selected = data.loc[data["financial_year"] == financial_year].iloc[0]

    in_crore = data.copy()
    for column in ["income", "expenditure", "operating_balance", "tax_revenue", "non_tax_revenue"]:
        if column in in_crore:
            in_crore[column] = in_crore[column] / 10_000_000

    in_crore["balance_margin_percent"] = (
        in_crore["operating_balance"] / in_crore["income"] * 100
    )
    history_crore = in_crore.set_index("financial_year")
    strongest_year = history_crore["operating_balance"].idxmax()
    weakest_year = history_crore["operating_balance"].idxmin()

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

    # Show the selected year's deficit, low tax share and spending growth above income growth
    issues = []
    balance = selected.get("operating_balance")
    if pd.notna(balance) and balance < 0:
        issues.append({
            "title": "Operating deficit",
            "details": f"Expenditure exceeded income by {rupees_in_crore(abs(balance))}.",
            "value": rupees_in_crore(balance),
        })

    tax_share = selected.get("tax_revenue_share_percent")
    if TAX_SHARE_THRESHOLD is not None and pd.notna(tax_share) and tax_share < TAX_SHARE_THRESHOLD:
        issues.append({
            "title": "Tax revenue share",
            "details": f"Tax revenue is {percent(tax_share)} of income (below {TAX_SHARE_THRESHOLD}%).",
            "value": percent(tax_share),
        })

    income_change = selected.get("income_change_percent")
    expenditure_change = selected.get("expenditure_change_percent")
    if pd.notna(income_change) and pd.notna(expenditure_change) and expenditure_change > income_change:
        issues.append({
            "title": "Expenditure grew faster than income",
            "details": f"Expenditure changed {expenditure_change:+.1f}% and income {income_change:+.1f}% "
                       "from the previous year.",
            "value": f"{expenditure_change:+.1f}% vs {income_change:+.1f}%",
        })

    return {
        "issues": issues,
        "has_finance_data": pd.notna(selected.get("income")) and pd.notna(selected.get("expenditure")),
        "selected": selected,
        "history_crore": history_crore,
        "revenue_mix": revenue_mix,
        "summary_rows": summary_rows,
        "selected_balance_margin_percent": history_crore.loc[
            financial_year, "balance_margin_percent"
        ],
        "largest_annual_change": largest_annual_change(history_crore),
        "stability_range": {
            "strongest_year": strongest_year,
            "strongest_balance": history_crore.loc[
                strongest_year, "operating_balance"
            ],
            "weakest_year": weakest_year,
            "weakest_balance": history_crore.loc[
                weakest_year, "operating_balance"
            ],
        },
    }
