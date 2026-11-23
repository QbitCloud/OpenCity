from .court_analysis import find_row


# The metrics that are scored against the baseline. They are all rates. Each one has: key, label, unit,
# which way is better, and the figure whose responsible post (court_pipeline/responsible.py) answers for it.
METRICS = [
    ("clearance", "Clearance rate, last month", "%", "higher", "Cases Disposed in Last Month"),
    ("civil_clearance", "Civil clearance rate, last month", "%", "higher", "civil_pending"),
    ("criminal_clearance", "Criminal clearance rate, last month", "%", "higher", "criminal_pending"),
    ("older_than_5", "Pending cases older than 5 years", "%", "lower", "pending_by_age"),
    ("older_than_10", "Pending cases older than 10 years", "%", "lower", "pending_by_age"),
    ("months_to_clear", "Months to clear the backlog", "months", "lower", "total_pending"),
]

# The value each metric is scored against, in the metric's unit (percent or months).
# None means no baseline yet: that metric is left out of the score.
# https://gujarathighcourt.nic.in/hccms/sites/default/files/IDPReport/Monthly_and_Quarterly_Case_Clearance_Rate_CCR_of_High_Court_of_Gujarat_and_District_Judiciary_of_Gujarat_for_the_Year_2025.pdf
#       vs
# URL = "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14"
BASELINE = {
    "clearance": 103,
    "civil_clearance": None,
    "criminal_clearance": None,
    "older_than_5": None,
    "older_than_10": None,
    "months_to_clear": None,
}

# How far behind the baseline a metric must be before it counts as an issue
MARGIN = 0.05


# a / b, or None when b is zero
def ratio(a, b):
    if not b:
        return None
    return a / b


# a as a percentage of b, or None when b is zero
def percent(a, b):
    value = ratio(a, b)
    if value is None:
        return None
    return value * 100


# The rates of one reading
def court_rates(record):
    instituted = find_row(record["particulars"], "Cases Instituted in Last Month")
    disposed = find_row(record["particulars"], "Cases Disposed in Last Month")
    ages = {row["age"]: row["total"] for row in record["pending_by_age"]}
    pending = record["total_pending"]

    return {
        # Cases disposed for every 100 filed last month; below 100% the backlog grows
        "clearance": percent(disposed["total"], instituted["total"]),
        "civil_clearance": percent(disposed["civil"], instituted["civil"]),
        "criminal_clearance": percent(disposed["criminal"], instituted["criminal"]),
        "older_than_5": percent(ages.get("5 to 10 Years", 0) + ages.get("Above 10 Years", 0), pending),
        "older_than_10": percent(ages.get("Above 10 Years", 0), pending),
        # How long the courts would take to clear today's pending cases at last month's pace, with no new cases
        "months_to_clear": ratio(pending, disposed["total"]),
    }


# Show a rate with its unit
def format_rate(value, unit):
    if value is None:
        return "Not reported"
    if unit == "%":
        return f"{value:.1f}%"
    return f"{value:.1f} months"


# The last reading before the selected date
def previous_reading(records, selected_date):
    earlier = [record for record in records if record["date"] < selected_date]
    if not earlier:
        return None
    return max(earlier, key=lambda record: record["date"])


# How Surat compares with the baseline: above 1 is better, below 1 is worse
def advantage(value, baseline, better):
    if better == "higher":
        top, bottom = value, baseline
    else:
        top, bottom = baseline, value

    if bottom == 0:
        # Zero where zero is best counts as matching or beating the baseline
        return 1.0
    return top / bottom


# Has the metric moved the wrong way since the last reading?
def worsened(value, previous, better):
    if value is None or previous is None:
        return False

    change = round(value, 1) - round(previous, 1)
    if better == "higher":
        return change < 0
    return change > 0


# Score Surat against the baseline, and list the metrics that lag it or got worse since the last reading
def court_scores(selected_court, court_records):
    previous_court = previous_reading(court_records, selected_court["date"])

    rates = court_rates(selected_court)
    previous_rates = court_rates(previous_court) if previous_court else {}

    issues = []
    scores = []
    for key, label, unit, better, responsible_key in METRICS:
        value = rates[key]
        baseline = BASELINE[key]
        previous = previous_rates.get(key)

        reasons = []
        if value is not None and baseline is not None:
            lead = advantage(value, baseline, better)
            scores.append(min(lead, 1.0) * 100)
            if lead < 1 - MARGIN:
                reasons.append(f"Below the baseline ({format_rate(baseline, unit)}).")
        if worsened(value, previous, better):
            reasons.append(f"Worse than on {previous_court['date']} ({format_rate(previous, unit)}).")

        if reasons:
            value_text = format_rate(value, unit)
            issues.append({
                "title": label,
                "details": f"Surat: {value_text}. " + " ".join(reasons),
                "value": value_text,
                "baseline": format_rate(baseline, unit) if baseline is not None else "",
                # The court figure whose responsible post answers for this metric (court_officials "figures")
                "figure": responsible_key,
            })

    score_text = "No baseline set"
    if scores:
        score_text = f"{sum(scores) / len(scores):.0f} / 100"

    return {"score_text": score_text, "issues": issues}
