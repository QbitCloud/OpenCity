
import pandas as pd
import requests
from clients.client import get_waste_collection
import streamlit as st
from components.cards import metric_card
from components.charts import chart_panel
from components.panels import info_panel

def show_overview() -> None:
    st.title("OpenCity Surat")
    st.write("Surat public data dashboard overview.")
    st.subheader("Door-to-door waste collection")

    try:
        data = get_waste_collection()
        waste = pd.DataFrame(data["observations"])

        if waste.empty:
            st.info("No waste-collection data is available yet.")
        else:
            waste["period_start"] = pd.to_datetime(waste["period_start"])
            waste["value"] = pd.to_numeric(waste["value"], errors="coerce")
            waste = waste.sort_values("period_start")

            # Keep unreported values missing, rather than treating them as zero.
            waste.loc[waste["status"] != "reported", "value"] = float("nan")
            reported = waste.dropna(subset=["value"])

            if reported.empty:
                st.info("No reported collection values are available.")
            else:
                latest = reported.iloc[-1]

                st.metric(
                    "Latest reported monthly average",
                    f"{latest['value']:,.3f} tonnes/day",
                )
                st.caption(
                    f"Reporting month: {latest['period_start']:%B %Y} "
                    f"| Geography: {data['geography']}"
                )

                # Include missing months so gaps remain visible.
                chart = waste.set_index("period_start")[["value"]].asfreq("MS")
                chart = chart.rename(columns={"value": "Tonnes per day"})
                st.line_chart(chart)

                st.markdown(
                    f"[Source: Surat Municipal Corporation]"
                    f"({latest['source_url']})"
                )
                st.caption(f"Data retrieved: {latest['retrieved_at']}")

    except requests.exceptions.HTTPError:
        st.warning("Waste data is unavailable from the API.")
    except requests.exceptions.RequestException:
        st.warning("Cannot reach the backend. Check that it is running.")
    except (KeyError, ValueError, TypeError):
        st.error("The waste-data response has an unexpected format.")
    st.divider()
    st.caption("Prototype sections below contain placeholder values.")


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
