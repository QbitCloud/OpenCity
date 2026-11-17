import pandas as pd


# Get reading dates in order
def get_dates(court_records):
    court_data = pd.DataFrame(court_records).sort_values("date")
    return court_data["date"].tolist()


# Find one row of a table by its name
def find_row(rows, name):
    for row in rows:
        if row["name"] == name:
            return row
    return {"civil": 0, "criminal": 0, "total": 0}


# chart data and summary for one reading
def court_analysis(selected_court):
    total_pending = selected_court["total_pending"]
    civil_pending = selected_court["civil_pending"]
    criminal_pending = selected_court["criminal_pending"]

    instituted = find_row(selected_court["particulars"], "Cases Instituted in Last Month")
    disposed = find_row(selected_court["particulars"], "Cases Disposed in Last Month")
    women = find_row(selected_court["particulars"], "Filed Cases By Woman")
    seniors = find_row(selected_court["particulars"], "Filed Cases By Senior Citizen")

    age_data = pd.DataFrame(selected_court["pending_by_age"])

    # Five KPI values
    pending_text = f"{total_pending:,}"
    civil_text = f"{civil_pending:,}"
    criminal_text = f"{criminal_pending:,}"

    # Clearance rate: cases disposed for every 100 cases filed last month
    clearance_text = "Not reported"
    if instituted["total"] > 0:
        clearance_text = f"{disposed['total'] / instituted['total'] * 100:.1f}%"

    # Share of pending cases that are more than five years old
    old_cases = age_data[age_data["age"].isin(["5 to 10 Years", "Above 10 Years"])]["total"].sum()
    old_text = "Not reported"
    if total_pending > 0:
        old_text = f"{old_cases / total_pending * 100:.1f}%"

    # Row 1, column 1: civil and criminal pending cases
    case_type_labels = ["Civil", "Criminal"]
    case_type_values = [civil_pending, criminal_pending]

    # Row 1, column 2: pending cases by age, civil and criminal side by side
    age_labels = age_data["age"].tolist()
    age_civil_values = age_data["civil"].tolist()
    age_criminal_values = age_data["criminal"].tolist()

    # Row 1, column 3: share of pending cases in each age band
    age_share_labels = age_data["age"].tolist()
    age_share_values = age_data["total"].tolist()

    # Row 2, column 1: cases filed and disposed last month
    flow_labels = ["Civil", "Criminal", "Total"]
    filed_values = [instituted["civil"], instituted["criminal"], instituted["total"]]
    disposed_values = [disposed["civil"], disposed["criminal"], disposed["total"]]

    # Row 2, column 2: pending cases filed by women and senior citizens
    filer_labels = ["Senior citizens", "Women"]
    filer_values = [seniors["total"], women["total"]]

    # Summary table
    summary_rows = [
        {"Metric": "Pending cases", "Civil": f"{civil_pending:,}", "Criminal": f"{criminal_pending:,}", "Total": pending_text},
    ]

    for row in selected_court["particulars"]:
        summary_rows.append({
            "Metric": row["name"],
            "Civil": f"{row['civil']:,}",
            "Criminal": f"{row['criminal']:,}",
            "Total": f"{row['total']:,}",
        })

    for row in selected_court["pending_by_age"]:
        summary_rows.append({
            "Metric": f"Pending: {row['age']}",
            "Civil": f"{row['civil']:,}",
            "Criminal": f"{row['criminal']:,}",
            "Total": f"{row['total']:,}",
        })

    # Format the last fetched time
    fetched_at = pd.to_datetime(selected_court["scraped_at"])

    return {
        "pending_text": pending_text,
        "civil_text": civil_text,
        "criminal_text": criminal_text,
        "clearance_text": clearance_text,
        "old_text": old_text,
        "case_type_labels": case_type_labels,
        "case_type_values": case_type_values,
        "age_labels": age_labels,
        "age_civil_values": age_civil_values,
        "age_criminal_values": age_criminal_values,
        "age_share_labels": age_share_labels,
        "age_share_values": age_share_values,
        "flow_labels": flow_labels,
        "filed_values": filed_values,
        "disposed_values": disposed_values,
        "filer_labels": filer_labels,
        "filer_values": filer_values,
        "summary_rows": summary_rows,
        "last_fetched": fetched_at,
    }
