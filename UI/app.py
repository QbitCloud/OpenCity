import sys
from pathlib import Path

import streamlit as st

# Let the dashboard import opencity_settings from the repo root.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from screens.overview import show_overview
from screens.finance import show_finance
from screens.water import show_water

from screens.overview import show_overview
from screens.hospitals import hospital
from screens.courts import court
from screens.schools import school


st.set_page_config(
    page_title="OpenCity Surat",
    layout="wide",
)

st.html("<style>.stMainBlockContainer { padding-top: 3rem; padding-bottom: 3rem; }</style>")


pages = [
    "Overview",
    "Hospitals",
    "Schools",
    "Finance",
    "Courts",
    "Water Quality",
    # "Food",
    # "Health & Environment",
    # "Council",
    # "RTI Tracker",
    # "Data Gaps",
    # "Sources",
    # "Data Status",
    # "About",
]

selected_page = st.sidebar.radio("Navigation", pages)

if selected_page == "Overview":
    show_overview()
elif selected_page == "Hospitals":
    hospital()
elif selected_page == "Courts":
    court()
elif selected_page == "Schools":
    school()
elif selected_page == "Finance":
    show_finance()
elif selected_page == "Water Quality":
    show_water()
else:
    st.title(selected_page, anchor=False)
