from math import isfinite


ISSUE_THRESHOLD = 70

# Selected PGI-D 2025–26 weights, Annexure 2, pages 36–37.
# API availability fields are proxies for some report definitions.
WEIGHTS = {
    "waterPer": 2,
    "toiletGPerFun": 2,
    "toiletBPerFun": 2,
    "toiletCwsnPer": 2,
    "handwashPer": 2,
    "rainWatPer": 2,
    "pgroundPer": 4,
    "libBbnkRcorPer": 4,
    "rampWithHandrailPer": 4,
    "internetPer": 10,
    "compPer": 10,
    "smartPerFun": 10,
}


# Weighted coverage of the selected year's reported facilities.
def school_score(school):
    earned_points = 0
    total_weight = 0
    reported_metrics = 0

    for field, weight in WEIGHTS.items():
        try:
            coverage = float(school[field])
        except (KeyError, TypeError, ValueError):
            continue

        if not isfinite(coverage) or not 0 <= coverage <= 100:
            continue

        earned_points += coverage / 100 * weight
        total_weight += weight
        reported_metrics += 1

    if total_weight == 0:
        return {"score_text": "Not reported", "reported_metrics": 0}

    score = earned_points / total_weight * 100

    return {
        "score_text": f"{score:.1f} / 100",
        "reported_metrics": reported_metrics,
    }
