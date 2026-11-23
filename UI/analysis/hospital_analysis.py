import pandas as pd

# Issue when a detail is reported for fewer than this % of hospitals
DETAIL_THRESHOLD = 75
# Issue when government + municipal hospitals are below this % of all hospitals (None = rule off)
PUBLIC_SHARE_THRESHOLD = None


# Start every word with a capital letter, keeping names like ENT as written
def clean_category(category):
    words = [word[0].upper() + word[1:] for word in category.split()]
    return " ".join(words)


# Find who runs the hospital from its category
def get_ownership(category):
    if "Government" in category:
        return "Government"
    if "Municipal" in category:
        return "Municipal"
    if "Trust" in category:
        return "Trust"
    return "Private"


# Build the hospital table with clean columns
def get_hospital_table(hospital_records):
    hospital_data = pd.DataFrame(hospital_records)

    # The website writes the same type in different letter cases
    hospital_data["category"] = hospital_data["category"].fillna("Not reported").apply(clean_category)
    hospital_data["ownership"] = hospital_data["category"].apply(get_ownership)
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


# chart data and summary for all hospitals
def hospital_analysis(hospital_records):
    hospital_data = get_hospital_table(hospital_records)

    # Five KPI values
    total_hospitals = len(hospital_data)
    ownership_counts = hospital_data["ownership"].value_counts()

    hospitals_text = f"{total_hospitals:,}"
    government_text = f"{ownership_counts.get('Government', 0):,}"
    municipal_text = f"{ownership_counts.get('Municipal', 0):,}"
    trust_text = f"{ownership_counts.get('Trust', 0):,}"
    private_text = f"{ownership_counts.get('Private', 0):,}"

    # Row 1, column 1: hospitals by ownership
    ownership_values = pd.Series({
        "Government": ownership_counts.get("Government", 0),
        "Municipal": ownership_counts.get("Municipal", 0),
        "Trust": ownership_counts.get("Trust", 0),
        "Private": ownership_counts.get("Private", 0),
    })
    ownership_values = ownership_values[ownership_values > 0]

    # Row 1, column 2: hospitals by type
    type_values = hospital_data["category"].value_counts().sort_values()

    # Row 1, column 3: details reported for each hospital
    detail_values = pd.Series({
        "Address": hospital_data["address"].notna().mean() * 100,
        "Phone": hospital_data["phone"].notna().mean() * 100,
        "Pincode": hospital_data["pincode"].notna().mean() * 100,
    })
    detail_values = detail_values.sort_values()

    # Show details reported for fewer than DETAIL_THRESHOLD % of hospitals
    issues = []
    for detail_name, coverage in detail_values.items():
        if 0 <= coverage < DETAIL_THRESHOLD:
            issues.append({
                "title": detail_name + " reported",
                "details": f"Reported for {coverage:.2f}% of hospitals (below {DETAIL_THRESHOLD}%).",
                "percent": float(coverage),
            })

    # Show a low share of government and municipal hospitals
    public_hospitals = ownership_counts.get("Government", 0) + ownership_counts.get("Municipal", 0)
    public_share = public_hospitals / total_hospitals * 100 if total_hospitals else 0
    if PUBLIC_SHARE_THRESHOLD is not None and public_share < PUBLIC_SHARE_THRESHOLD:
        issues.append({
            "title": "Government and municipal hospitals",
            "details": f"{public_share:.2f}% of listed hospitals (below {PUBLIC_SHARE_THRESHOLD}%).",
            "percent": float(public_share),
        })

    # Format the last fetched time
    fetched_at = pd.to_datetime(hospital_data["scraped_at"].iloc[0])

    return {
        "hospitals_text": hospitals_text,
        "government_text": government_text,
        "municipal_text": municipal_text,
        "trust_text": trust_text,
        "private_text": private_text,
        "ownership_labels": ownership_values.index.tolist(),
        "ownership_values": ownership_values.tolist(),
        "type_labels": type_values.index.tolist(),
        "type_values": type_values.tolist(),
        "detail_labels": detail_values.index.tolist(),
        "detail_values": detail_values.tolist(),
        "issues": issues,
        "has_hospital_data": total_hospitals > 0,
        "fetched_date": fetched_at.strftime("%Y-%m-%d"),
        "last_fetched": fetched_at,
    }
