"""Project-defined Finance baseline flags for the dashboard."""
from __future__ import annotations

import math


OFFICIAL_REFERENCES = [
    {
        "title": "NUDM Urban Analytics Standard",
        "url": "https://www.nudm.mohua.gov.in/wp-content/uploads/2025/05/UA-Standard-NUDM.pdf",
        "details": "Defines urban finance indicators such as own-source revenue, without colour cut-offs.",
    },
    {
        "title": "16th Finance Commission — municipal reporting context",
        "url": "https://www.indiabudget.gov.in/doc/16fcvol1.pdf",
        "details": "A reporting and transparency reference, not a financial-health score.",
    },
]

PROJECT_LEGEND = (
    "Green, Amber, Orange and Red are OpenCity project-defined interpretation "
    "bands. They are not an official government rating."
)

STATUS_TONE = {
    "Green": "success",
    "Amber": "warning",
    "Orange": "warning",
    "Red": "error",
    "Not enough data": "info",
}


def _number(value: object) -> float | None:
    """Return a usable number while keeping missing data missing."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _higher_is_better(value: object, green: float, amber: float, orange: float) -> str:
    """Label a Finance metric where a larger value is preferable."""
    number = _number(value)
    if number is None:
        return "Not enough data"
    if number >= green:
        return "Green"
    if number >= amber:
        return "Amber"
    if number >= orange:
        return "Orange"
    return "Red"


def _lower_is_better(value: object, green: float, amber: float, orange: float) -> str:
    """Label a Finance metric where a smaller value is preferable."""
    number = _number(value)
    if number is None:
        return "Not enough data"
    if number <= green:
        return "Green"
    if number <= amber:
        return "Amber"
    if number <= orange:
        return "Orange"
    return "Red"


def _component(
    name: str,
    value: object,
    baseline: str,
    weight: int,
    status: str,
    value_text: str,
) -> dict:
    """Create one visible Finance flag and its contribution to the score."""
    multiplier = {
        "Green": 1.0,
        "Amber": 0.70,
        "Orange": 0.35,
        "Red": 0.0,
    }
    return {
        "name": name,
        "value": value_text,
        "status": status,
        "baseline": baseline,
        "points": None if status == "Not enough data" else round(weight * multiplier[status]),
        "weight": weight,
    }


def _percent(value: object) -> str:
    number = _number(value)
    return "Not reported" if number is None else f"{number:.1f}%"


def _points(value: object) -> str:
    number = _number(value)
    return "Not reported" if number is None else f"{number:+.1f} points"


def _years(value: object) -> str:
    number = _number(value)
    if number is None:
        return "Not reported"
    return f"{number:.0f} year" if number == 1 else f"{number:.0f} years"


def _overall_status(score: int) -> str:
    """Turn the transparent 0–100 Finance score into one top-of-page flag."""
    if score >= 85:
        return "Green"
    if score >= 70:
        return "Amber"
    if score >= 50:
        return "Orange"
    return "Red"


def finance_baseline(
    balance_margin: object,
    expenditure_growth_gap: object,
    own_source_revenue: object,
    stable_years: object,
) -> dict:
    """Return the Finance score and the four flags behind it."""
    components = [
        _component(
            "Operating balance margin",
            balance_margin,
            "Green ≥5%, Amber ≥0%, Orange ≥-5%, Red <-5%",
            35,
            _higher_is_better(balance_margin, 5.0, 0.0, -5.0),
            _percent(balance_margin),
        ),
        _component(
            "Expenditure growth above income",
            expenditure_growth_gap,
            "Green ≤2 points, Amber ≤5, Orange ≤10, Red >10",
            25,
            _lower_is_better(expenditure_growth_gap, 2.0, 5.0, 10.0),
            _points(expenditure_growth_gap),
        ),
        _component(
            "Own-source revenue proxy",
            own_source_revenue,
            "Green ≥50%, Amber ≥35%, Orange ≥20%, Red <20%",
            25,
            _higher_is_better(own_source_revenue, 50.0, 35.0, 20.0),
            _percent(own_source_revenue),
        ),
        _component(
            "Three-year balance stability",
            stable_years,
            "Green 3 years, Amber 2, Orange 1, Red 0",
            15,
            _higher_is_better(stable_years, 3.0, 2.0, 1.0),
            _years(stable_years),
        ),
    ]

    if any(component["points"] is None for component in components):
        return {
            "score": None,
            "status": "Not enough data",
            "tone": STATUS_TONE["Not enough data"],
            "components": components,
            "action": "Publish the missing Finance value before assigning a status.",
        }

    score = sum(component["points"] for component in components)
    status = _overall_status(score)
    actions = {
        "Green": "Continue publishing source-linked annual accounts and monitor the trend.",
        "Amber": "Review the next annual account and watch income against expenditure.",
        "Orange": "Review the selected balance sheet before drawing conclusions.",
        "Red": "Treat this as a review flag, not an allegation. Verify the source report first.",
    }
    return {
        "score": score,
        "status": status,
        "tone": STATUS_TONE[status],
        "components": components,
        "action": actions[status],
    }
