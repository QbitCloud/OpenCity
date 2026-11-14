import streamlit as st

from screens.overview import show_overview
from screens.schools import school
from screens.officials import officials


st.set_page_config(
    page_title="OpenCity Surat",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("<style>.stMainBlockContainer { padding-top: 3rem; padding-bottom: 3rem; }</style>")

st.sidebar.title("OpenCity Surat", anchor=False)

# These pages will get their dashboards later.
def health():
    st.title("Health", anchor=False)


def water():
    st.title("Water", anchor=False)


def crimes():
    st.title("Crimes", anchor=False)


def finance():
    st.title("Finance", anchor=False)


def sources():
    st.title("Sources", anchor=False)


# Native Streamlit sidebar navigation.
pages = {
    "Explore": [
        st.Page(show_overview, title="Home", icon=":material/home:", default=True),
        st.Page(school, title="School", icon=":material/school:"),
        st.Page(health, title="Health", icon=":material/health_and_safety:"),
        st.Page(officials, title="Officials", icon=":material/groups:"),
        st.Page(water, title="Water", icon=":material/water_drop:"),
        st.Page(crimes, title="Crimes", icon=":material/local_police:"),
        st.Page(finance, title="Finance", icon=":material/account_balance:"),
    ],
    "Resources": [
        st.Page(sources, title="Sources", icon=":material/link:"),
    ],
}

page = st.navigation(pages, position="hidden")

with st.sidebar:
    for section, section_pages in pages.items():
        st.caption(section)
        for navigation_page in section_pages:
            st.page_link(navigation_page)

page.run()
