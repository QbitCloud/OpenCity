import streamlit as st

from analysis.hospital_analysis import get_hospital_types, hospital_analysis, hospital_directory
from clients.backend import get_hospitals
from components.charts import bar_chart, pie_chart


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

    # KPI row
    st.subheader("Quick Numbers", anchor=False)
    st.caption(
        "A quick overview of the hospitals listed for Surat and who runs them. "
        "The counts cover every listed hospital, whatever hospital type is selected."
    )
    hospital_column, government_column, municipal_column, trust_column, private_column = st.columns(5)

    # KPI column 1: Hospitals
    with hospital_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Hospitals", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['hospitals_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 2: Government
    with government_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Government", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['government_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 3: Municipal
    with municipal_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Municipal", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['municipal_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 4: Trust
    with trust_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Trust", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['trust_text']}]", anchor=False, width="content", text_alignment="center")

    # KPI column 5: Private
    with private_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Private", width="content", text_alignment="center")
            st.header(f":yellow[{analysis['private_text']}]", anchor=False, width="content", text_alignment="center")

    st.divider()

    # Chart row 1
    st.subheader("Hospital ownership and types", anchor=False)
    st.caption(
        "See how the listed hospitals are split across government, municipal, trust and private "
        "ownership, the hospital types on the list, and how complete the published details are."
    )
    ownership_chart_column, type_chart_column, detail_chart_column = st.columns(3)

    # Row 1, column 1: Hospital ownership
    with ownership_chart_column:
        with st.container(border=True):
            st.subheader("Hospital ownership", text_alignment="center", anchor=False)
            st.caption("Hospitals by who runs them", text_alignment="center")

            pie_chart(analysis["ownership_labels"], analysis["ownership_values"])

    # Row 1, column 2: Hospital types
    with type_chart_column:
        with st.container(border=True):
            st.subheader("Hospital types", text_alignment="center", anchor=False)
            st.caption("Hospitals by listed type", text_alignment="center")

            bar_chart(analysis["type_labels"], analysis["type_values"], "Hospitals")

    # Row 1, column 3: Details reported
    with detail_chart_column:
        with st.container(border=True):
            st.subheader("Details reported", text_alignment="center", anchor=False)
            st.caption("Hospitals listing each detail (%)", text_alignment="center")

            bar_chart(analysis["detail_labels"], analysis["detail_values"], "Hospitals (%)")

    st.divider()

    # Directory table
    st.subheader("Hospital directory", anchor=False)
    st.caption(
        "Every listed hospital of the selected hospital type with its address and phone number. "
        "Missing details are shown as ‘Not reported’."
    )
    st.dataframe(hospital_directory(hospital_records, selected_type), hide_index=True, width="stretch")
    st.divider()

    # Footer
    updated_column, source_column = st.columns([3, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        st.caption(analysis["last_fetched"])

    with source_column:
        st.link_button("View District Surat source", "https://surat.nic.in/public-utility-category/hospitals/", width="stretch")
