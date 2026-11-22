"""A small landing page for the completed OpenCity dashboards."""
import streamlit as st

def show_overview() -> None:
    """Direct visitors to the source-linked project dashboards."""
    st.title("OpenCity Surat", anchor=False)
    st.write("A student-built dashboard for exploring public Surat Municipal Corporation data.")

    st.divider()
    finance_column, water_column = st.columns(2)

    with finance_column:
        with st.container(border=True):
            st.subheader("Finance", anchor=False)
            st.caption(
                "Explore 19 years of official balance-sheet figures, revenue mix, "
                "year-on-year changes and a clearly marked estimate."
            )

    with water_column:
        with st.container(border=True):
            st.subheader("Drinking Water Quality", anchor=False)
            st.caption(
                "Explore monthly SMC sample totals, fit and unfit results, "
                "compliance rates and source reports."
            )

    st.info("Choose Finance or Water Quality from the sidebar to explore the available data.")
