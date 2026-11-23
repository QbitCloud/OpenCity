import pandas as pd

# Issue when a detail is reported for fewer than this % of hospitals
DETAIL_THRESHOLD = 75

# Census 2011 population of Surat Municipal Corporation, counted within the city limits as extended in 2020
# (SMC demographics page: https://www.suratmunicipal.gov.in/TheCity/Demographics)
POPULATION = 4645384
# National Urban Health Mission norms: one urban health centre (UHC) for every 50,000 people, and one urban
# community health centre (UCHC) for every 2.5 lakh people, or 5 lakh in metros. Surat is a million-plus city,
# so the metro norm is used; set 250000 for the stricter one.
PEOPLE_PER_UHC = 50000
PEOPLE_PER_UCHC = 500000


# Start every word with a capital letter, keeping names like ENT as written
def clean_category(category):
    words = [word[0].upper() + word[1:] for word in category.split()]
    return " ".join(words)


# Short zone name for charts: "West Zone (Rander)" becomes "Rander", "East Zone - A" becomes "East A"
def short_zone(zone):
    if "(" in zone:
        return zone[zone.index("(") + 1:zone.index(")")]
    return " ".join(zone.replace("Zone", "").replace("-", " ").split())


# Find who runs a hospital from its listed type
def get_ownership(category):
    if "Government" in category or "Municipal" in category:
        return "Public"
    if "Trust" in category:
        return "Trust"
    return "Private"


# Build the hospital table with clean columns
def get_hospital_table(hospital_records):
    hospital_data = pd.DataFrame(hospital_records)

    # The website writes the same type in different letter cases
    hospital_data["category"] = hospital_data["category"].fillna("Not reported").apply(clean_category)
    return hospital_data


# Get hospital types in order
def get_hospital_types(hospital_records):
    hospital_data = get_hospital_table(hospital_records)
    return ["All"] + sorted(hospital_data["category"].unique().tolist())


# Directory rows for the selected hospital type
def hospital_directory(hospital_records, selected_type):
    hospital_data = get_hospital_table(hospital_records)

    if selected_type != "All":
        hospital_data = hospital_data[hospital_data["category"] == selected_type]

    directory = hospital_data[["name", "category", "address", "phone"]].fillna("Not reported")
    directory.columns = ["Hospital", "Type", "Address", "Phone"]
    return directory.to_dict("records")


# Chart data and issues for all hospitals
def hospital_analysis(hospital_records):
    hospital_data = get_hospital_table(hospital_records)

    # KPI values: every listed hospital, and the government hospitals among them
    hospitals_text = f"{len(hospital_data):,}"
    government_text = f"{hospital_data['category'].str.contains('Government').sum():,}"

    # Public (government or municipal), private and trust hospitals
    ownership_values = hospital_data["category"].apply(get_ownership).value_counts()
    ownership_values = ownership_values.reindex(["Public", "Private", "Trust"], fill_value=0)
    ownership_values = ownership_values[ownership_values > 0]

    # Details reported for each hospital
    detail_values = pd.Series({
        "Address": hospital_data["address"].notna().mean() * 100,
        "Phone": hospital_data["phone"].notna().mean() * 100,
        "Pincode": hospital_data["pincode"].notna().mean() * 100,
    })
    detail_values = detail_values.sort_values()

    # Format the last fetched time
    fetched_at = pd.to_datetime(hospital_data["scraped_at"].iloc[0])

    # Show details reported for fewer than DETAIL_THRESHOLD % of hospitals
    issues = []
    for detail_name, coverage in detail_values.items():
        if 0 <= coverage < DETAIL_THRESHOLD:
            issues.append({
                "title": detail_name + " reported",
                "details": f"Reported for {coverage:.2f}% of hospitals (below {DETAIL_THRESHOLD}%).",
                "value": f"{coverage:.2f}%",
                "location": "Surat district",
                "period": "Listing fetched " + fetched_at.strftime("%Y-%m-%d"),
                "source": "District Surat (surat.nic.in)",
            })

    return {
        "hospitals_text": hospitals_text,
        "government_text": government_text,
        "ownership_labels": ownership_values.index.tolist(),
        "ownership_values": ownership_values.tolist(),
        "issues": issues,
        "has_hospital_data": len(hospital_data) > 0,
        "last_fetched": fetched_at,
    }


# Count SMC's urban health centres and score them against the NUHM norms
def health_centre_analysis(centres):
    if not centres:
        return {
            "uhc_text": "Not available", "uchc_text": "Not available", "score": None, "score_text": "No data", "issues": [],
            "zone_labels": [], "zone_uhc": [], "zone_uchc": [],
        }

    centre_data = pd.DataFrame(centres)
    counts = centre_data["facility_type"].value_counts()
    fetched_at = pd.to_datetime(centre_data["scraped_at"].iloc[0])

    # Centres of each type in each zone, the zone with the most centres last
    zones = pd.crosstab(centre_data["zone_code"], centre_data["facility_type"])
    zones = zones.reindex(columns=["uhc", "uchc"], fill_value=0)
    zones = zones.loc[zones.sum(axis=1).sort_values().index]

    scores = []
    issues = []
    for facility_type, label, norm in [
        ("uhc", "Urban health centres", PEOPLE_PER_UHC),
        ("uchc", "Urban community health centres", PEOPLE_PER_UCHC),
    ]:
        count = counts.get(facility_type, 0)

        # People for each centre: fewer is better, and meeting the norm scores 100
        people = POPULATION / count if count else None
        score = min(norm / people, 1) * 100 if people else 0
        scores.append(score)

        if score < 100:
            value = f"1 per {people:,.0f} people" if people else "None listed"
            issues.append({
                "title": label,
                "details": f"{value}; the NUHM norm is 1 per {norm:,} people.",
                "value": value,
                "location": "Surat Municipal Corporation",
                "period": "Centre list fetched " + fetched_at.strftime("%Y-%m-%d"),
                "source": "SMC health centre list; Census 2011",
            })

    return {
        "uhc_text": f"{counts.get('uhc', 0):,}",
        "uchc_text": f"{counts.get('uchc', 0):,}",
        "score": sum(scores) / len(scores),
        "score_text": f"{sum(scores) / len(scores):.0f} / 100",
        "issues": issues,
        "zone_labels": [short_zone(zone) for zone in zones.index],
        "zone_uhc": zones["uhc"].tolist(),
        "zone_uchc": zones["uchc"].tolist(),
    }
