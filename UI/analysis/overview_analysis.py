from analysis.court_analysis import get_dates
from analysis.court_score import court_scores
from analysis.finance_analysis import finance_analysis
from analysis.hospital_analysis import health_centre_analysis
from analysis.school_analysis import get_academic_years
from analysis.school_score import school_score
from analysis.water_analysis import water_analysis
from analysis.water_score import water_score, water_score_value


# One page's card: the score its own page shows (latest data), as a number for the city score and as text
def page_score(page, score, score_text, metric, detail):
    return {"page": page, "score": score, "score_text": score_text, "metric": metric, "detail": detail}


# School: the weighted infrastructure score of the latest academic year, as on the School page
def school_page(school_records):
    if not school_records:
        return page_score("School", None, "No data", "Infrastructure score", "No school data")

    latest_year = get_academic_years(school_records)[-1]
    selected_school = next(record for record in school_records if record["academic_year"] == latest_year)
    score = school_score(selected_school)
    return page_score("School", score["score"], score["score_text"], "Infrastructure score", "Academic year " + latest_year)


# Hospital: SMC's health centres against the NUHM norms, as on the Hospital page
def hospital_page(centres):
    analysis = health_centre_analysis(centres)
    return page_score("Hospital", analysis["score"], analysis["score_text"], "Health centres against norms", "Census 2011 population")


# Water Quality: the latest month's compliance in the score bands, as on the Water Quality page
def water_page(water_data):
    if not water_data or not water_data.get("history"):
        return page_score("Water Quality", None, "No data", "Latest month's compliance", "No water data")

    analysis = water_analysis(water_data["history"])
    compliance = analysis["latest"]["compliance_rate_percent"]
    return page_score(
        "Water Quality", water_score_value(compliance), water_score(compliance),
        "Latest month's compliance", analysis["latest_month"],
    )


# Courts: the court score of the latest NJDG reading, as on the Courts page
def courts_page(court_records):
    if not court_records:
        return page_score("Courts", None, "No data", "Court score", "No court data")

    latest_date = get_dates(court_records)[-1]
    selected_court = next(record for record in court_records if record["date"] == latest_date)
    score = court_scores(selected_court, court_records)
    return page_score("Courts", score["score"], score["score_text"], "Court score", "NJDG reading of " + latest_date)


# Finance: the OpenCity finance score of the latest financial year, as on the Finance page
def finance_page(finance_data):
    history = (finance_data or {}).get("history")
    if not history:
        return page_score("Finance", None, "No data", "Finance score", "No finance data")

    latest_year = history[-1]["financial_year"]
    score = finance_analysis(history, latest_year)["baseline"]["score"]
    score_text = "Not enough data" if score is None else f"{score} / 100"
    return page_score("Finance", score, score_text, "Finance score", "Financial year " + latest_year)


# Every page's score, and the city score: their average, with every page weighted equally
def city_scores(school_records, centres, water_data, court_records, finance_data):
    pages = [
        school_page(school_records),
        hospital_page(centres),
        water_page(water_data),
        courts_page(court_records),
        finance_page(finance_data),
    ]
    scored = [page["score"] for page in pages if page["score"] is not None]
    city = sum(scored) / len(scored) if scored else None

    return {
        "pages": pages,
        "city_text": "No data" if city is None else f"{city:.0f} / 100",
        "city_detail": f"Average of {len(scored)} of {len(pages)} page scores",
    }
