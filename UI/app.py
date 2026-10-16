import streamlit as st
from screens.overview import show_overview

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
    "Water & Rain",
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
else:
    dummy(selected_page)