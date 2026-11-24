"""Landing page: a map of Surat, the city score and each dashboard's main score."""
from pathlib import Path

import requests
import streamlit as st

from analysis.overview_analysis import city_scores
from clients.backend import get_courts, get_health_centres, get_schools
from clients.client import get_deepak_finance_analysis, get_deepak_water_analysis

MAP_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "surat_map.png"


def _fetch(get_data):
    """Call a backend client that raises on errors; None when the data is unavailable."""
    try:
        return get_data()
    except requests.exceptions.RequestException:
        return None


def show_overview() -> None:
    """Show a map of Surat, the city score as a rating out of 5 stars, and every page's main score out of 100."""
    st.title(" ", anchor=False)
    st.write(" ")

    if MAP_IMAGE.exists():
        st.image(str(MAP_IMAGE), width="stretch")
        st.caption("© OpenStreetMap contributors.")

    # st.divider()

    scores = city_scores(
        get_schools(),
        get_health_centres(),
        _fetch(get_deepak_water_analysis),
        get_courts(),
        _fetch(get_deepak_finance_analysis),
    )

    # City score
    # st.subheader("City score", anchor=False)
    # st.caption(
    #     "The average of the five page scores below, with every page weighted equally, as a rating out of 5 stars "
    #     "(average ÷ 20, rounded to the nearest star). Pages without data are left out."
    # )
    _, city_column, _ = st.columns([1, 2, 1])

    with city_column:
        with st.container(border=True, horizontal_alignment="center"):
            st.text("Surat", width="content", text_alignment="center")
            st.header(f":yellow[{scores['city_stars']}]", anchor=False, width="content", text_alignment="center")
            st.text(scores["city_text"], width="content", text_alignment="center")
            st.caption(scores["city_detail"], text_alignment="center")

    st.divider()

    # Page scores
    st.subheader("Page scores", anchor=False)
    st.caption(
        "The score each page shows for its latest data, out of 100. Select a page's name to open it. "
        "School: the PGI-D-weighted infrastructure score. "
        "Health: SMC's health centres against the National Urban Health Mission norms. "
        "Water Quality: the latest month's compliance in the score bands. "
        "Courts: Surat's clearance rate against Gujarat's. "
        "Finance: the finance score built from four flags."
    )

    # Each card links to its page, with the sidebar's icon. The pages are imported here because
    # screens/issues.py imports this module, so importing them at the top would be circular.
    from screens.courts import court
    from screens.finance import show_finance
    from screens.hospitals import hospital
    from screens.schools import school
    from screens.water import show_water

    pages = {
        "School": st.Page(school, title="School", icon=":material/school:"),
        "Health": st.Page(hospital, title="Health", icon=":material/health_and_safety:"),
        "Water Quality": st.Page(show_water, title="Water Quality", icon=":material/water_drop:"),
        "Courts": st.Page(court, title="Courts", icon=":material/local_police:"),
        "Finance": st.Page(show_finance, title="Finance", icon=":material/account_balance:"),
    }

    for column, page in zip(st.columns(5), scores["pages"]):
        with column:
            with st.container(border=True, height="stretch", horizontal_alignment="center"):
                st.page_link(pages[page["page"]])
                st.header(f":yellow[{page['score_text']}]", anchor=False, width="content", text_alignment="center")
                if page["score"] is not None:
                    st.progress(page["score"] / 100)
                st.caption(page["metric"], text_alignment="center")
                st.caption(page["detail"], text_alignment="center")
