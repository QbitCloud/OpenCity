import streamlit as st
from components.cards import metric_card
from components.charts import chart_panel
from components.panels import info_panel

def show_overview() -> None:
    st.title("OpenCity Surat")
    st.write("Surat public data dashboard overview.")

    # 4 Summary cards using reusable metric_card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Municipal Income")
    with col2:
        metric_card("Municipal Expenditure")
    with col3:
        metric_card("Waste Collected")
    with col4:
        metric_card("RTI Requests")

    st.write("")

    # 3 Chart panels using reusable chart_panel
    chart1, chart2, chart3 = st.columns(3)
    with chart1:
        chart_panel("Budget Trends")
    with chart2:
        chart_panel("Waste Collection Trends")
    with chart3:
        chart_panel("RTI Requests Status")

    st.write("")

    # Wide table beside smaller panel using reusable info_panel
    col_table, col_info = st.columns([2, 1])
    with col_table:
        info_panel("Dataset Summary Table", "dummy data ")
    with col_info:
        info_panel("Data Gaps Panel", "dymmu gap")
