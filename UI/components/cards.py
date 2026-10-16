import streamlit as st


def metric_card(title: str, value: str = "239 Rupee", note: str = ""):
    # KPI metric card component for overview page
    with st.container(border=True):
        st.subheader(title)
        st.write(value)
        if note:
            st.caption(note)
