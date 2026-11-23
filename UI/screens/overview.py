"""Landing page: each dashboard's main score and the city score built from them."""
import requests
import streamlit as st

from analysis.overview_analysis import city_scores
from clients.backend import get_courts, get_health_centres, get_schools
from clients.client import get_deepak_finance_analysis, get_deepak_water_analysis


def _fetch(get_data):
    """Call a backend client that raises on errors; None when the data is unavailable."""
    try:
        return get_data()
    except requests.exceptions.RequestException:
        return None


def show_overview() -> None:
    """Show every page's main metric as a score out of 100, and the city score."""
    st.title("OpenCity Surat", anchor=False)
    st.write("A student-built dashboard for exploring public data on Surat's schools, health, water, courts and finances.")
    st.divider()

    scores = city_scores(
        get_schools(),
        get_health_centres(),
        _fetch(get_deepak_water_analysis),
        get_courts(),
        _fetch(get_deepak_finance_analysis),
    )

    # City score
    st.subheader("City score", anchor=False)
    st.caption("The average of the five page scores below, with every page weighted equally. Pages without data are left out.")
    _, city_column, _ = st.columns(3)

    with city_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Surat", width="content", text_alignment="center")
            st.header(f":yellow[{scores['city_text']}]", anchor=False, width="content", text_alignment="center")
            st.caption(scores["city_detail"], text_alignment="center")

    st.divider()

    # Page scores
    st.subheader("Page scores", anchor=False)
    st.caption(
        "The score each page shows for its latest data, out of 100. "
        "School: the PGI-D-weighted infrastructure score. "
        "Hospital: SMC's health centres against the National Urban Health Mission norms. "
        "Water Quality: the latest month's compliance in the score bands. "
        "Courts: Surat's clearance rate against Gujarat's. "
        "Finance: the finance score built from four flags."
    )

    for column, page in zip(st.columns(5), scores["pages"]):
        with column:
            with st.container(border=True, horizontal_alignment="center"):
                st.text(page["page"], width="content", text_alignment="center")
                st.header(f":yellow[{page['score_text']}]", anchor=False, width="content", text_alignment="center")
                st.caption(page["metric"], text_alignment="center")
                st.caption(page["detail"], text_alignment="center")
