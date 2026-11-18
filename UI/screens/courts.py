import streamlit as st

from analysis.court_analysis import court_analysis, get_dates
from clients.backend import get_courts
from components.charts import bar_chart, pie_chart
from components.court_charts import paired_bar_chart


# Show the post responsible for a figure, with the judge's name under it if known
def show_responsible(person):
    st.caption(f"Responsible: {person['post']}", text_alignment="center")
    if person["name"]:
        st.caption(person["name"], text_alignment="center")


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

    # KPI row
    st.subheader("Quick Numbers", anchor=False)
    st.caption(
        "A quick overview of cases pending in the Surat district courts on the selected date. "
        "The clearance rate compares cases disposed with cases filed last month; "
        "below 100% means the backlog is growing."
    )
    pending_column, civil_column, criminal_column, clearance_column, old_column = st.columns(5)

    # KPI column 1: Pending cases
    with pending_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Pending cases", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['pending_text']}]", anchor=False, width="content", text_alignment="center")
            show_responsible(analysis["pending_person"])

    # KPI column 2: Civil
    with civil_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Civil", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['civil_text']}]", anchor=False, width="content", text_alignment="center")
            show_responsible(analysis["civil_person"])

    # KPI column 3: Criminal
    with criminal_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Criminal", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['criminal_text']}]", anchor=False, width="content", text_alignment="center")
            show_responsible(analysis["criminal_person"])

    # KPI column 4: Clearance rate
    with clearance_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Clearance rate", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['clearance_text']}]", anchor=False, width="content", text_alignment="center")
            show_responsible(analysis["clearance_person"])

    # KPI column 5: Older than 5 years
    with old_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Older than 5 years", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['old_text']}]", anchor=False, width="content", text_alignment="center")
            show_responsible(analysis["old_person"])

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
        "All court figures for the selected date in one table, split into civil and criminal cases, "
        "with the post responsible for each and the judge holding that post. "
        "Figures are shown as published; the age bands may not add up exactly to the total."
    )
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
    st.divider()

    # Footer
    updated_column, source_column = st.columns([3, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        st.caption(analysis["last_fetched"])

    with source_column:
        st.link_button("View NJDG source", "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14", width="stretch")
