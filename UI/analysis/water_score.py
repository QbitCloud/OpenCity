from math import isfinite


ISSUE_THRESHOLD = 95
MAX_POINTS = 50

# PJS reference bands; the 5% split is our dashboard rule.
SCORE_BANDS = [(95, 50), (75, 40), (50, 30), (25, 20), (5, 10), (0, 0)]


# Convert the latest month's compliance into a score out of 100.
def water_score(compliance):
    try:
        compliance = float(compliance)
    except (TypeError, ValueError):
        return "Not reported"

    if not isfinite(compliance) or not 0 <= compliance <= 100:
        return "Not reported"

    for minimum, points in SCORE_BANDS:
        if compliance >= minimum:
            score = points / MAX_POINTS * 100
            return f"{score:.0f} / 100"
