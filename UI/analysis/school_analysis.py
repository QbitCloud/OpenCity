import pandas as pd


# Format a number, or show that it is missing
def format_number(value, number_format="{:,.0f}"):
    if pd.isna(value):
        return "Not reported"
    return number_format.format(value)


# Get academic years in order
def get_academic_years(school_records):
    school_data = pd.DataFrame(school_records).sort_values("yearId")
    return school_data["academic_year"].tolist()


# chart data and summary for one year
def school_analysis(selected_school):
    # Convert numeric fields once
    numbers = pd.to_numeric(pd.Series(selected_school), errors="coerce")

    # Five KPI values
    total_schools = numbers.get("totSch")
    total_students = numbers.get("tenrF2Sec")
    total_teachers = numbers.get("ttch")
    internet_percentage = numbers.get("internetPer")

    schools_text = format_number(total_schools)
    students_text = format_number(total_students)
    teachers_text = format_number(total_teachers)
    internet_text = format_number(internet_percentage, "{:.2f}%")

    ratio_text = "Not reported"
    if pd.notna(total_students) and pd.notna(total_teachers) and total_teachers > 0:
        ratio_text = f"{total_students / total_teachers:.1f}"

    # Row 1, column 1: schools by management
    school_values = pd.Series({
        "Government": numbers.get("tschGovt"),
        "Govt aided": numbers.get("tschGovtAided"),
        "Private unaided": numbers.get("tschPvtUnaided"),
        "Other": numbers.get("tschOth"),
    })
    school_values = school_values.dropna()
    school_values = school_values[school_values > 0]

    # Row 1, column 2: students by management
    student_values = pd.Series({
        "Government": numbers.get("tenrF2SecGov"),
        "Govt aided": numbers.get("tenrF2SecGovAided"),
        "Private unaided": numbers.get("tenrF2SecPvtUnaided"),
        "Other": numbers.get("tenrF2SecOth"),
    })
    student_values = student_values.dropna()
    student_values = student_values[student_values > 0]

    # Row 1, column 3: students by stage
    stage_values = pd.Series({
        "Foundational": numbers.get("tenrF"),
        "Preparatory": numbers.get("tenrP"),
        "Middle": numbers.get("tenrM"),
        "Secondary": numbers.get("tenrS"),
    })
    stage_values = stage_values.dropna()
    stage_values = stage_values[stage_values > 0]

    # Row 2, column 1: available and functional facilities
    facility_comparison = pd.DataFrame({
        "Available": [numbers.get("elecPer"), numbers.get("waterPer"),
                      numbers.get("toiletPer"), numbers.get("compPer"),
                      numbers.get("toiletCwsnPer")],
        "Functional": [numbers.get("elecPerFun"), numbers.get("waterPerFun"),
                       numbers.get("toiletPerFun"), numbers.get("compPerFun"),
                       numbers.get("toiletCwsnPerFun")],
    }, index=["Electricity", "Water", "Toilets", "Computers", "Accessible toilets"])
    facility_comparison = facility_comparison.apply(pd.to_numeric).dropna(how="all")

    # Row 2, column 2: facility coverage
    facility_values = pd.Series({
        "Electricity": numbers.get("elecPer"),
        "Drinking water": numbers.get("waterPer"),
        "Toilets": numbers.get("toiletPer"),
        "Handwashing": numbers.get("handwashPer"),
        "Computers": numbers.get("compPer"),
        "Internet access": numbers.get("internetPer"),
        "Accessible toilets": numbers.get("toiletCwsnPer"),
        "Ramps with handrails": numbers.get("rampWithHandrailPer"),
        "Library / reading corner": numbers.get("libBbnkRcorPer"),
        "Functional smart classrooms": numbers.get("smartPerFun"),
        "Playgrounds": numbers.get("pgroundPer"),
        "Rainwater harvesting": numbers.get("rainWatPer"),
    })
    coverage_values = facility_values.dropna().sort_values()

    # Row 2, column 3: teachers by management
    teacher_values = pd.Series({
        "Government": numbers.get("ttchGovt"),
        "Govt aided": numbers.get("ttchGovtAided"),
        "Private unaided": numbers.get("ttchPvtUnaided"),
        "Other": numbers.get("ttchOth"),
    })
    teacher_values = teacher_values.dropna()

    # Summary table
    summary_rows = [
        {"Metric": "Schools", "Value": schools_text},
        {"Metric": "Students", "Value": students_text},
        {"Metric": "Teachers", "Value": teachers_text},
        {"Metric": "Students / teacher", "Value": ratio_text},
    ]

    for facility_name, facility_value in facility_values.items():
        value_text = format_number(facility_value, "{:.2f}%")
        summary_rows.append({"Metric": facility_name, "Value": value_text})

    # Format the last fetched time
    fetched_at = pd.to_datetime(selected_school["scraped_at"])

    return {
        "schools_text": schools_text,
        "students_text": students_text,
        "teachers_text": teachers_text,
        "ratio_text": ratio_text,
        "internet_text": internet_text,
        "school_values_labels": school_values.index.tolist(),
        "school_values": school_values.tolist(),
        "student_values_labels": student_values.index.tolist(),
        "student_values": student_values.tolist(),
        "stage_values_labels": stage_values.index.tolist(),
        "stage_values": stage_values.tolist(),
        "facility_labels": facility_comparison.index.tolist(),
        "available_values": facility_comparison["Available"].tolist(),
        "functional_values": facility_comparison["Functional"].tolist(),
        "coverage_labels": coverage_values.index.tolist(),
        "coverage_values": coverage_values.tolist(),
        "teacher_labels": teacher_values.index.tolist(),
        "teacher_values": teacher_values.tolist(),
        "summary_rows": summary_rows,
        "last_fetched": fetched_at,
    }
