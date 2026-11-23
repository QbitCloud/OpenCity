import streamlit as st

from analysis.hospital_analysis import (
    DETAIL_THRESHOLD,
    PEOPLE_PER_UCHC,
    PEOPLE_PER_UHC,
    POPULATION,
    get_hospital_types,
    health_centre_analysis,
    hospital_analysis,
    hospital_directory,
)
from clients.backend import get_health_centres, get_hospitals
from screens.issues import issue_details
from components.charts import pie_chart
from components.court_charts import paired_bar_chart


# Show the hospital dashboard
def hospital():
    # Title and hospital type filter
    title_column, filter_column = st.columns([3, 1], vertical_alignment="bottom")

    with title_column:
        st.title("Surat Hospitals Analysis", anchor=False)

    hospital_records = get_hospitals()

    if hospital_records is None:
        st.error("Hospital data is unavailable. Check the backend and MongoDB connection.")
        return

    if not hospital_records:
        st.info("No hospital data found. Run the hospital pipeline first.")
        return

    hospital_types = get_hospital_types(hospital_records)

    with filter_column:
        selected_type = st.selectbox("Hospital type", hospital_types)

    st.divider()

    analysis = hospital_analysis(hospital_records)
    centres = get_health_centres()
    centre_analysis = health_centre_analysis(centres)

    # KPI row: listed hospitals, and SMC's urban health centres scored against the national norms
    st.subheader("Quick Numbers", anchor=False)
    st.caption(
        "The hospitals listed for Surat district and how many of them are government hospitals, whatever "
        "hospital type is selected. Then the urban health centres (UHC) and urban community health centres (UCHC) "
        "run by Surat Municipal Corporation. "
        f"The health score rates them against the National Urban Health Mission norms of one UHC for every "
        f"{PEOPLE_PER_UHC:,} people and one UCHC for every {PEOPLE_PER_UCHC:,} people, using Surat's "
        f"Census 2011 population of {POPULATION:,}. 100 means Surat meets both norms."
    )

    if centres is None:
        st.warning("Health centre data is unavailable. Check the backend and MongoDB connection.")
    elif not centres:
        st.info("No health centre data found. Run the health pipeline first.")

    hospital_column, government_column, uhc_column, uchc_column, score_column = st.columns(5)

    # KPI column 1: Hospitals
    with hospital_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Hospitals", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['hospitals_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 2: Government hospitals
    with government_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Government hospitals", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['government_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 3: Urban health centres
    with uhc_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Urban health centres", width="content", text_alignment="center")
            st.header(f":yellow[{centre_analysis['uhc_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 4: Urban community health centres
    with uchc_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Urban community HCs", width="content", text_alignment="center")
            st.header(f":yellow[{centre_analysis['uchc_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 5: Health score against the norms
    with score_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Health score", width="content", text_alignment="center")
            st.header(f":yellow[{centre_analysis['score_text']}]", anchor=False, width="content", text_alignment="center")

    st.divider()

    # Chart row: SMC's health centres and the listed hospitals
    st.subheader("Health centres and hospitals", anchor=False)
    st.caption("How SMC's health centres are spread across its zones, and who runs the hospitals listed for Surat district.")
    zone_chart_column, ownership_chart_column = st.columns(2)

    # Column 1: Centres by zone
    with zone_chart_column:
        with st.container(border=True):
            st.subheader("Centres by zone", text_alignment="center", anchor=False)
            st.caption("Urban health centres (UHC) and urban community health centres (UCHC) in each SMC zone", text_alignment="center")

            paired_bar_chart(
                centre_analysis["zone_labels"], centre_analysis["zone_uhc"], centre_analysis["zone_uchc"],
                "UHC", "UCHC", "Centres",
            )

    # Column 2: Public and private hospitals
    with ownership_chart_column:
        with st.container(border=True):
            st.subheader("Public and private", text_alignment="center", anchor=False)
            st.caption("Public means government or municipal; trust hospitals are run by charities", text_alignment="center")

            pie_chart(analysis["ownership_labels"], analysis["ownership_values"])

    st.divider()

    # Directory table
    st.subheader("Hospital directory", anchor=False)
    st.caption(
        "Every listed hospital of the selected hospital type with its address and phone number. "
        "Missing details are shown as ‘Not reported’."
    )
    st.dataframe(hospital_directory(hospital_records, selected_type), hide_index=True, width="stretch")
    st.divider()

    # Issues section: details reported below the threshold, and health centres below the norms
    st.subheader("Hospital issues", anchor=False)
    st.caption(
        f"Hospital details reported for fewer than {DETAIL_THRESHOLD}% of listed hospitals, and SMC health "
        "centres that fall short of the National Urban Health Mission norms."
    )
    issues = analysis["issues"] + centre_analysis["issues"]

    if not analysis["has_hospital_data"]:
        st.info("Not enough hospital data is reported to identify gaps.")
    elif not issues:
        st.info("No hospital or health centre metric is below its threshold.")
    else:
        for issue in issues:
            with st.container(border=True):
                issue_column, action_column = st.columns([4, 1], vertical_alignment="center")
                with issue_column:
                    st.text(issue["title"])
                    st.caption(issue["details"])
                with action_column:
                    if st.button("See issue", key="issue_" + issue["title"], width="stretch"):
                        st.session_state.issue_source_page = st.Page(hospital, title="Hospital")
                        st.session_state.selected_issue = {
                            "metric": issue["title"],
                            "category": "Health",
                            "location": issue["location"],
                            "period": issue["period"],
                            "source": issue["source"],
                            "value": issue["value"],
                        }
                        st.switch_page(st.Page(issue_details, title="Issue details", url_path="issue"))

    st.divider()

    # Footer
    updated_column, hospital_source_column, centre_source_column = st.columns([2, 1, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        st.caption(analysis["last_fetched"])

    with hospital_source_column:
        st.link_button("View District Surat source", "https://surat.nic.in/public-utility-category/hospitals/", width="stretch")

    with centre_source_column:
        st.link_button("View SMC health centres", "https://www.suratmunicipal.gov.in/Departments/PMJAYUHC", width="stretch")
