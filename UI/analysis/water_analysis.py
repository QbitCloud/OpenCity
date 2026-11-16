"""Turn Water Quality API history into clear dashboard values."""
from __future__ import annotations

import pandas as pd


def water_analysis(history: list[dict]) -> dict:
    """Prepare monthly trends, annual totals and a source-linked summary table."""
    data = pd.DataFrame(history).copy()
    data["period_start"] = pd.to_datetime(data["period_start"])
    data = data.sort_values("period_start")
    data["month"] = data["period_start"].dt.strftime("%b %Y")
    data["year"] = data["period_start"].dt.year
    data["unfit_rate_percent"] = (
        data["samples_unfit"] / data["samples_collected"] * 100
    )
    data["unfit_change"] = data["samples_unfit"].diff()

    trailing_months = data.tail(12)
    expected_months = pd.period_range(
        data["period_start"].min(),
        data["period_start"].max(),
        freq="M",
    )
    reported_periods = data["period_start"].dt.to_period("M")
    missing_months = expected_months.difference(reported_periods)
    twelve_month_sample_average = trailing_months["samples_collected"].mean()

    annual = (
        data.groupby("year")[["samples_collected", "samples_fit", "samples_unfit"]]
        .sum()
        .rename(columns={
            "samples_collected": "Samples collected",
            "samples_fit": "Fit samples",
            "samples_unfit": "Unfit samples",
        })
    )

    summary_rows = data.sort_values("period_start", ascending=False)[
        [
            "month",
            "samples_collected",
            "samples_fit",
            "samples_unfit",
            "compliance_rate_percent",
            "source_url",
        ]
    ].rename(columns={
        "month": "Month",
        "samples_collected": "Samples collected",
        "samples_fit": "Fit samples",
        "samples_unfit": "Unfit samples",
        "compliance_rate_percent": "Compliance rate (%)",
        "source_url": "Official source",
    })

    return {
        "latest": data.iloc[-1],
        "monthly": data.set_index("period_start"),
        "annual": annual,
        "summary_rows": summary_rows,
        "reported_months": len(data),
        "latest_unfit_rate_percent": data.iloc[-1]["unfit_rate_percent"],
        "latest_unfit_change": data.iloc[-1]["unfit_change"],
        "trailing_compliance_percent": trailing_months[
            "compliance_rate_percent"
        ].mean(),
        "latest_samples_vs_average_percent": (
            (data.iloc[-1]["samples_collected"] / twelve_month_sample_average - 1)
            * 100
        ),
        "reporting_completeness_percent": len(data) / len(expected_months) * 100,
        "missing_months": [str(month) for month in missing_months],
    }
