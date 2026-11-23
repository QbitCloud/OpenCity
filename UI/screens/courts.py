import streamlit as st

from analysis.court_analysis import court_analysis, get_dates
from analysis.court_score import court_scores
from clients.backend import get_courts
from screens.issues import issue_details
from components.charts import bar_chart, pie_chart
from components.court_charts import paired_bar_chart


# Show the court dashboard
def court():
    # Title and date filter
    title_column, filter_column = st.columns([3, 1], vertical_alignment="bottom")

    with title_column:
        st.title("Surat Courts Analysis", anchor=False)

    court_records = get_courts()

    if court_records is None:
        st.error("Court data is unavailable. Check the backend and MongoDB connection.")
        return

    if not court_records:
        st.info("No court data found. Run the court pipeline first.")
        return

    dates = get_dates(court_records)

    with filter_column:
        selected_date = st.selectbox("Reading date", dates, index=len(dates) - 1)

    for record in court_records:
        if record["date"] == selected_date:
            selected_court = record
            break

    st.divider()

    analysis = court_analysis(selected_court)
    scores = court_scores(selected_court, court_records)

    # KPI row
    st.subheader("Quick Numbers", anchor=False)
    st.caption(
        "A quick overview of cases pending in the Surat district courts."
    )
    pending_column, civil_column, criminal_column, clearance_column, score_column = st.columns(5)

    # KPI column 1: Pending cases
    with pending_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Pending cases", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['pending_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 2: Civil
    with civil_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Civil", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['civil_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 3: Criminal
    with criminal_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Criminal", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['criminal_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 4: Clearance rate
    with clearance_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Clearance rate", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['clearance_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 5: Court score against the baseline
    with score_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Court score", width="content", text_alignment="center")
            st.header(f":yellow[{scores['score_text']}]", anchor=False, width="content", text_alignment="center")

    st.divider()

    # Chart row 1
    st.subheader("Pending cases and their age", anchor=False)
    st.caption(
        "See how pending cases split between civil and criminal matters, "
        "and how long they have been waiting in court."
    )
    case_type_column, age_column, age_share_column = st.columns(3)

    # Row 1, column 1: Civil and criminal
    with case_type_column:
        with st.container(border=True):
            st.subheader("Case type", text_alignment="center", anchor=False)
            st.caption("Pending cases by case type", text_alignment="center")

            pie_chart(analysis["case_type_labels"], analysis["case_type_values"])

    # Row 1, column 2: Age of pending cases
    with age_column:
        with st.container(border=True):
            st.subheader("Case age", text_alignment="center", anchor=False)
            st.caption("Civil and criminal cases by age", text_alignment="center")

            paired_bar_chart(analysis["age_labels"], analysis["age_civil_values"], analysis["age_criminal_values"],
                             "Civil", "Criminal", "Pending cases")

    # Row 1, column 3: Share of each age band
    with age_share_column:
        with st.container(border=True):
            st.subheader("Age share", text_alignment="center", anchor=False)
            st.caption("Share of pending cases in each age band", text_alignment="center")

            pie_chart(analysis["age_share_labels"], analysis["age_share_values"])

    st.divider()

    # Chart row 2
    st.subheader("Case flow and who files", anchor=False)
    st.caption(
        "Compare the cases filed and disposed last month, and see how many pending cases "
        "were filed by women and by senior citizens."
    )
    flow_column, filer_column = st.columns(2)

    # Row 2, column 1: Filed and disposed last month
    with flow_column:
        with st.container(border=True):
            st.subheader("Last month", text_alignment="center", anchor=False)
            st.caption("Cases filed and disposed", text_alignment="center")

            paired_bar_chart(analysis["flow_labels"], analysis["filed_values"], analysis["disposed_values"],
                             "Filed", "Disposed", "Cases")

    # Row 2, column 2: Women and senior citizens
    with filer_column:
        with st.container(border=True):
            st.subheader("Filed by", text_alignment="center", anchor=False)
            st.caption("Pending cases filed by women and senior citizens", text_alignment="center")

            bar_chart(analysis["filer_labels"], analysis["filer_values"], "Pending cases")

    st.divider()

    # Summary table
    st.subheader("Metric summary", anchor=False)
    st.caption(
        "All court figures for the selected date in one table, split into civil and criminal cases. "
        "Figures are shown as published; the age bands may not add up exactly to the total."
    )
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
    st.divider()

    # Issues section: metrics below the baseline or worse than the last reading
    st.subheader(f"Court issues · {selected_date}", anchor=False)
    st.caption("Metrics below the baseline, or that got worse since the last reading.")

    if not scores["issues"]:
        st.info("No metric is below the baseline or got worse since the last reading.")
    else:
        for issue in scores["issues"]:
            with st.container(border=True):
                issue_column, action_column = st.columns([4, 1], vertical_alignment="center")
                with issue_column:
                    st.text(issue["title"])
                    st.caption(issue["details"])
                with action_column:
                    if st.button("See issue", key="issue_" + issue["title"], width="stretch"):
                        st.session_state.issue_source_page = st.Page(court, title="Courts")
                        st.session_state.selected_issue = {
                            "metric": issue["title"],
                            "category": "Courts",
                            "location": "Surat district",
                            "period": "NJDG reading of " + selected_date,
                            "source": "NJDG",
                            "value": issue["value"],
                            "baseline": issue["baseline"],
                            "figure": issue["figure"],
                        }
                        st.switch_page(st.Page(issue_details, title="Issue details", url_path="issue"))

    st.divider()

    # Footer
    updated_column, source_column = st.columns([3, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        st.caption(analysis["last_fetched"])

    with source_column:
        st.link_button("View NJDG source", "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14", width="stretch")
