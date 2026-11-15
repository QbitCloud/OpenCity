import streamlit as st
from screens.overview import show_overview
from screens.finance import show_finance
from screens.water import show_water

# Page setup
st.set_page_config(
    page_title="OpenCity Surat",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("OpenCity Surat")
pages: list[str] = [
    "Overview",
    "Finance",
    "Food",
    "Health & Environment",
    "Water Quality",
    "Council",
    "RTI Tracker",
    "Data Gaps",
    "Sources",
    "Data Status",
    "About"
]
selected_page: str = str(st.sidebar.radio("Navigation", pages))

# Sidebar disclaimer
st.sidebar.caption("OpenCity Surat")

def dummy(page_name: str):
    st.header(page_name)

# Main routing
if selected_page == "Overview":
    show_overview()
elif selected_page == "Finance":
    show_finance()
elif selected_page == "Water Quality":
    show_water()
else:
    dummy(selected_page)
