import streamlit as st

from analysis.school_analysis import get_academic_years, school_analysis
from clients.backend import get_schools
from components.charts import bar_chart, pie_chart
from components.school_charts import school_facility_chart


# Show the school dashboard
def school():
    # Title and year filter
    title_column, filter_column = st.columns([3, 1], vertical_alignment="bottom")

    with title_column:
        st.title("Surat Schools Analysis", anchor=False)

    school_records = get_schools()

    if school_records is None:
        st.error("School data is unavailable. Check the backend and MongoDB connection.")
        return

    if not school_records:
        st.info("No school data found. Run the school pipeline first.")
        return

    academic_years = get_academic_years(school_records)

    with filter_column:
        selected_year = st.selectbox("Academic year", academic_years, index=len(academic_years) - 1)

    for record in school_records:
        if record["academic_year"] == selected_year:
            selected_school = record
            break

    st.divider()

    analysis = school_analysis(selected_school)

    # KPI row
    st.subheader("Quick Numbers", anchor=False)
    st.caption(
        "A quick overview of schools, students, teachers and internet access for the selected year. "
        "The student–teacher ratio shows the average number of enrolled students per teacher."
    )
    school_column, student_column, teacher_column, ratio_column, internet_column = st.columns(5)

    # KPI column 1: Schools
    with school_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Schools", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['schools_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 2: Students
    with student_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Students", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['students_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 3: Teachers
    with teacher_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Teachers", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['teachers_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 4: Students / teacher
    with ratio_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Students / teacher", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['ratio_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 5: Internet access
    with internet_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Internet access", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['internet_text']}]", anchor=False, width="content", text_alignment="center")

    st.divider()

    # Chart row 1
    st.subheader("Schools and student enrolment", anchor=False)
    st.caption(
        "See how schools and student enrolment are distributed across government, government-aided "
        "and private management, alongside the distribution of students across school stages."
    )
    school_chart_column, student_chart_column, stage_chart_column = st.columns(3)

    # Row 1, column 1: School management
    with school_chart_column:
        with st.container(border=True):
            st.subheader("School management", text_alignment="center", anchor=False)
            st.caption("Schools by management type", text_alignment="center")

            pie_chart(analysis["school_values_labels"], analysis["school_values"])

    # Row 1, column 2: Enrolment management
    with student_chart_column:
        with st.container(border=True):
            st.subheader("Enrolment management", text_alignment="center", anchor=False)
            st.caption("Shares of reported student counts", text_alignment="center")

            pie_chart(analysis["student_values_labels"], analysis["student_values"])

    # Row 1, column 3: Enrolment by stage
    with stage_chart_column:
        with st.container(border=True):
            st.subheader("Enrolment by stage", text_alignment="center", anchor=False)
            st.caption("Students across school stages", text_alignment="center")

            pie_chart(analysis["stage_values_labels"], analysis["stage_values"])

    st.divider()

    # Chart row 2
    st.subheader("School facilities and teaching staff", anchor=False)
    st.caption(
        "Explore the percentage of schools reporting each facility and whether those facilities are "
        "functional. The staffing chart shows teacher counts across management types."
    )
    comparison_column, coverage_column, staff_column = st.columns(3)

    # Row 2, column 1: available and functional facilities
    with comparison_column:
        with st.container(border=True):
            st.subheader("Functional facilities", text_alignment="center", anchor=False)
            st.caption("Available and functional facilities (%)", text_alignment="center")

            school_facility_chart(analysis["facility_labels"], analysis["available_values"], analysis["functional_values"])

    # Row 2, column 2: facility coverage
    with coverage_column:
        with st.container(border=True):
            st.subheader("Facility coverage", text_alignment="center", anchor=False)
            st.caption("Schools reporting each facility (%)", text_alignment="center")

            bar_chart(analysis["coverage_labels"], analysis["coverage_values"], "Schools (%)")

    # Row 2, column 3: teachers by management
    with staff_column:
        with st.container(border=True):
            st.subheader("Teacher management", text_alignment="center", anchor=False)
            st.caption("Teachers by management type", text_alignment="center")

            bar_chart(analysis["teacher_labels"], analysis["teacher_values"], "Teachers")

    st.divider()

    # Summary table
    st.subheader("Metric summary", anchor=False)
    st.caption(
        "All key figures for the selected academic year in one table. "
        "Facility values are percentages of schools; missing figures are shown as ‘Not reported’."
    )
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
    st.divider()

    # Footer
    updated_column, source_column = st.columns([3, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        st.caption(analysis["last_fetched"])

    with source_column:
        st.link_button("View UDISE+ source", "https://udiseplus.gov.in/", width="stretch")
