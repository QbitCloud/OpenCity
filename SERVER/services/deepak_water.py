"""Prepare Deepak's historic drinking-water quality data for the API."""
from __future__ import annotations

from deepak_pipeline.db import read_water_observations


COLLECTED = "water.samples_collected"
FIT = "water.samples_fit"
UNFIT = "water.samples_unfit"
COMPLIANCE = "water.compliance_rate_percent"


def build_history(observations: list[dict]) -> list[dict]:
    """Group individual Water Quality metrics into one clear row per month."""
    months: dict[str, dict] = {}

    for observation in observations:
        period_start = observation["period_start"]
        row = months.setdefault(
            period_start,
            {"period_start": period_start, "source_url": observation["source_url"]},
        )
        row[observation["metric_id"]] = observation["value"]

    history = []
    for period_start in sorted(months):
        row = months[period_start]
        if COLLECTED not in row or FIT not in row or UNFIT not in row:
            continue

        collected = row[COLLECTED]
        fit = row[FIT]
        history.append(
            {
                "period_start": period_start,
                "samples_collected": collected,
                "samples_fit": fit,
                "samples_unfit": row[UNFIT],
                "compliance_rate_percent": row.get(
                    COMPLIANCE,
                    round(fit / collected * 100, 2) if collected else None,
                ),
                "source_url": row["source_url"],
            }
        )

    return history


def reporting_completeness(history: list[dict]) -> dict:
    """Describe reported months without treating unavailable reports as zero."""
    if not history:
        return {"reported_months": 0, "first_month": None, "latest_month": None}

    return {
        "reported_months": len(history),
        "first_month": history[0]["period_start"],
        "latest_month": history[-1]["period_start"],
    }


def load_deepak_water_analysis() -> dict:
    """Return source-linked monthly Water Quality history for the dashboard."""
    history = build_history(read_water_observations())
    return {
        "unit": "samples tested",
        "history": history,
        "latest": history[-1] if history else None,
        "reporting": reporting_completeness(history),
    }
