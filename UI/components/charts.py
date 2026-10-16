import streamlit as st


def chart_panel(title: str, subtitle: str = "chart metrics"):
    # chart metric card component for overview page
    with st.container(border=True):
        st.subheader(title)
        st.write(subtitle)
