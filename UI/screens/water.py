"""Monthly drinking-water quality dashboard based on official SMC reports."""
from __future__ import annotations

import requests
import streamlit as st

from analysis.water_analysis import COMPLIANCE_THRESHOLD, water_analysis
from clients.client import get_deepak_water_analysis
from screens.issues import issue_details


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
    collected_column, unfit_rate_column, change_column, compliance_column, average_column, coverage_column = st.columns(6)
    with collected_column:
        _number_card("Samples collected", f"{latest['samples_collected']:,.0f}")
    with unfit_rate_column:
        _number_card("Unfit-sample rate", f"{analysis['latest_unfit_rate_percent']:.1f}%")
    with change_column:
        change = analysis["latest_unfit_change"]
        _number_card("Unfit samples vs last month", "First reported month" if change is None else f"{change:+.0f}")
    with compliance_column:
        _number_card("12-month compliance", f"{analysis['trailing_compliance_percent']:.1f}%")
    with average_column:
        _number_card("Samples vs 12-month average", f"{analysis['latest_samples_vs_average_percent']:+.1f}%")
    with coverage_column:
        _number_card("Reporting completeness", f"{analysis['reporting_completeness_percent']:.0f}%")

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
            st.subheader("Unfit-sample rate", anchor=False)
            st.caption("Unfit samples as a share of samples collected")
            st.line_chart(monthly[["unfit_rate_percent"]].rename(
                columns={"unfit_rate_percent": "Unfit rate (%)"}
            ))

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
            if analysis["missing_months"]:
                st.caption("Missing reports: " + ", ".join(analysis["missing_months"]))
            else:
                st.caption("All months in the displayed period have a parsed report.")
            st.link_button("View latest SMC report", latest["source_url"], width="stretch")

    st.divider()
    st.subheader("Monthly source summary", anchor=False)
    st.caption("Reported months are shown newest first; missing months are intentionally not filled with zero.")
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
    st.divider()

    # Issues section: low compliance, rising unfit-sample rate, missing reports
    st.subheader(f"Water Quality issues · {analysis['latest_month']}", anchor=False)
    rule = "An unfit-sample rate higher than the month before, or missing monthly reports."
    if COMPLIANCE_THRESHOLD is not None:
        rule += f" Compliance below {COMPLIANCE_THRESHOLD}% in the latest month."
    st.caption(rule)

    if not analysis["has_water_data"]:
        st.info("Not enough Water Quality data is reported to identify issues.")
    elif not analysis["issues"]:
        st.info("No Water Quality metric crossed its threshold in the latest month.")
    else:
        for issue in analysis["issues"]:
            with st.container(border=True):
                issue_column, action_column = st.columns([4, 1], vertical_alignment="center")
                with issue_column:
                    st.text(issue["title"])
                    st.caption(issue["details"])
                with action_column:
                    if st.button("See issue", key="issue_" + issue["title"], width="stretch"):
                        st.session_state.issue_source_page = st.Page(show_water, title="Water Quality")
                        st.session_state.selected_issue = {
                            "metric": issue["title"],
                            "category": "Water",
                            "location": "Surat Municipal Corporation",
                            "period": analysis["latest_month"],
                            "source": "SMC Hydraulic department",
                            "value": issue["value"],
                        }
                        st.switch_page(st.Page(issue_details, title="Issue details", url_path="issue"))
