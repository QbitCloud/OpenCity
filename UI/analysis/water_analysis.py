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
    }
