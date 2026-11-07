import streamlit as st

from screens.overview import show_overview
from screens.schools import school


st.set_page_config(
    page_title="OpenCity Surat",
    layout="wide",
)

st.html("<style>.stMainBlockContainer { padding-top: 3rem; padding-bottom: 3rem; }</style>")


pages = [
    "Schools",
    "Overview",
    "Finance",
    "Food",
    "Health & Environment",
    "Water & Rain",
    "Council",
    "RTI Tracker",
    "Data Gaps",
    "Sources",
    "Data Status",
    "About",
]

selected_page = st.sidebar.radio("Navigation", pages)

if selected_page == "Overview":
    show_overview()
elif selected_page == "Schools":
    school()
else:
    st.title(selected_page, anchor=False)
