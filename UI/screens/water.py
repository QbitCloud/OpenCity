"""Monthly drinking-water quality dashboard based on official SMC reports."""
from __future__ import annotations

import requests
import streamlit as st

from analysis.water_analysis import water_analysis
from clients.client import get_deepak_water_analysis


def _number_card(label: str, value: str) -> None:
    """Use the same bordered KPI style as the School dashboard."""
    with st.container(border=True):
        st.caption(label)
        st.subheader(value, anchor=False)


def show_water() -> None:
    """Show monthly reported water-sample results without treating gaps as zero."""
    st.title("Drinking Water Quality", anchor=False)
    st.caption(
        "Monthly citywide sample results published by Surat Municipal Corporation. "
        "A missing month means no parsed report, not zero samples."
    )

    try:
        data = get_deepak_water_analysis()
    except requests.exceptions.HTTPError:
        st.warning("Water Quality data is unavailable. Run the Water pipeline first.")
        return
    except requests.exceptions.RequestException:
        st.warning("Cannot reach the backend. Check that it is running.")
        return

    history = data.get("history", [])
    if not history:
        st.info("No official Water Quality values are available yet.")
        return

    analysis = water_analysis(history)
    latest = analysis["latest"]

    st.divider()
    st.subheader("Latest reported month", anchor=False)
    st.caption(f"{latest['period_start']:%B %Y} — all figures are sample counts.")
    collected_column, fit_column, unfit_column, rate_column, reports_column = st.columns(5)
    with collected_column:
        _number_card("Samples collected", f"{latest['samples_collected']:,.0f}")
    with fit_column:
        _number_card("Fit samples", f"{latest['samples_fit']:,.0f}")
    with unfit_column:
        _number_card("Unfit samples", f"{latest['samples_unfit']:,.0f}")
    with rate_column:
        _number_card("Compliance rate", f"{latest['compliance_rate_percent']:.1f}%")
    with reports_column:
        _number_card("Reports available", str(analysis["reported_months"]))

    monthly = analysis["monthly"]
    st.divider()
    quality_column, compliance_column, unfit_column = st.columns(3)
    with quality_column:
        with st.container(border=True):
            st.subheader("Fit and unfit samples", anchor=False)
            st.caption("Monthly citywide laboratory results")
            st.bar_chart(monthly[["samples_fit", "samples_unfit"]].rename(
                columns={"samples_fit": "Fit", "samples_unfit": "Unfit"}
            ))
    with compliance_column:
        with st.container(border=True):
            st.subheader("Compliance rate", anchor=False)
            st.caption("Fit samples as a percentage of samples collected")
            st.line_chart(monthly[["compliance_rate_percent"]].rename(
                columns={"compliance_rate_percent": "Compliance (%)"}
            ))
    with unfit_column:
        with st.container(border=True):
            st.subheader("Unfit sample trend", anchor=False)
            st.caption("This is a count, not a measure of severity")
            st.line_chart(monthly[["samples_unfit"]].rename(columns={"samples_unfit": "Unfit samples"}))

    st.divider()
    collection_column, annual_column, source_column = st.columns(3)
    with collection_column:
        with st.container(border=True):
            st.subheader("Samples collected", anchor=False)
            st.caption("Monthly monitoring activity")
            st.line_chart(monthly[["samples_collected"]].rename(
                columns={"samples_collected": "Samples collected"}
            ))
    with annual_column:
        with st.container(border=True):
            st.subheader("Annual reported totals", anchor=False)
            st.caption("Totals use only months that have a parsed official report")
            st.bar_chart(analysis["annual"])
    with source_column:
        with st.container(border=True):
            st.subheader("How to read this", anchor=False)
            st.caption(
                "Fit and unfit counts come from the city total in each SMC report. "
                "Use the source link in the table to inspect any month."
            )
            st.link_button("View latest SMC report", latest["source_url"], width="stretch")

    st.divider()
    st.subheader("Monthly source summary", anchor=False)
    st.caption("Reported months are shown newest first; missing months are intentionally not filled with zero.")
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
