import streamlit as st


def info_panel(title: str, text: str):
    # panel component for overview page
    with st.container(border=True):
        st.subheader(title)
        st.write(text)
