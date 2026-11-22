"""Historic Finance dashboard based on official SMC balance sheets."""
from __future__ import annotations

import requests
import pandas as pd
import streamlit as st

from analysis.finance_analysis import finance_analysis, percent, rupees_in_crore
from clients.client import get_deepak_finance_analysis


def _number_card(label: str, value: str) -> None:
    """Use the same bordered KPI style as the School dashboard."""
    with st.container(border=True):
        st.caption(label)
        st.subheader(value, anchor=False)


def show_finance() -> None:
    """Show source-linked historic Finance trends and a cautious next-year estimate."""
    title_column, filter_column = st.columns([3, 1], vertical_alignment="bottom")
    with title_column:
        st.title("SMC Finance", anchor=False)

    try:
        data = get_deepak_finance_analysis()
    except requests.exceptions.HTTPError:
        st.warning("Historic Finance data is unavailable. Run the Finance pipeline first.")
        return
    except requests.exceptions.RequestException:
        st.warning("Cannot reach the backend. Check that it is running.")
        return

    history = data.get("history", [])
    if not history:
        st.info("No official Finance values are available yet.")
        return

    years = [row["financial_year"] for row in history]
    with filter_column:
        selected_year = st.selectbox("Financial year", years, index=len(years) - 1)

    analysis = finance_analysis(history, selected_year)
    selected = analysis["selected"]

    st.caption(
        "Annual figures from Surat Municipal Corporation balance sheets. "
        "All money values are shown in ₹ crore."
    )
    st.divider()

    st.subheader("Quick numbers", anchor=False)
    st.caption("The selected year's income, spending, balance and own-revenue mix.")
    income_column, expense_column, balance_column, margin_column, tax_column, share_column = st.columns(6)
    with income_column:
        _number_card("Total income", rupees_in_crore(selected["income"]))
    with expense_column:
        _number_card("Total expenditure", rupees_in_crore(selected["expenditure"]))
    with balance_column:
        _number_card("Operating balance", rupees_in_crore(selected["operating_balance"]))
    with margin_column:
        _number_card(
            "Balance margin",
            percent(analysis["selected_balance_margin_percent"]),
        )
    with tax_column:
        _number_card("Tax revenue", rupees_in_crore(selected.get("tax_revenue")))
    with share_column:
        _number_card("Tax revenue share", percent(selected.get("tax_revenue_share_percent")))

    latest = data["latest"]
    if latest["operating_balance"] < 0:
        st.warning(
            f"Latest reported year ({latest['financial_year']}): expenditure exceeded "
            f"income by {rupees_in_crore(abs(latest['operating_balance']))}."
        )

    st.divider()
    history_crore = analysis["history_crore"]
    trend_column, mix_column, forecast_column = st.columns(3)
    with trend_column:
        with st.container(border=True):
            st.subheader("Income and expenditure", anchor=False)
            st.caption("Annual reported amounts in ₹ crore")
            st.line_chart(history_crore[["income", "expenditure"]].rename(
                columns={"income": "Income", "expenditure": "Expenditure"}
            ))
    with mix_column:
        with st.container(border=True):
            st.subheader("Revenue mix", anchor=False)
            st.caption(f"Tax and non-tax revenue in {selected_year}")
            st.bar_chart(analysis["revenue_mix"])
    with forecast_column:
        with st.container(border=True):
            st.subheader("Next-year estimate", anchor=False)
            forecast = data.get("forecast")
            if forecast:
                st.caption(f"{forecast['financial_year']} — three-year average; not an official forecast")
                forecast_chart = pd.DataFrame(
                    {
                        "₹ crore": [
                            forecast["estimated_income"] / 10_000_000,
                            forecast["estimated_expenditure"] / 10_000_000,
                            forecast["estimated_operating_balance"] / 10_000_000,
                        ]
                    },
                    index=["Income", "Expenditure", "Balance"],
                )
                st.bar_chart(forecast_chart)
            else:
                st.info("A forecast needs reported Finance history.")

    st.divider()
    balance_column, change_column, share_column = st.columns(3)
    with balance_column:
        with st.container(border=True):
            st.subheader("Operating balance", anchor=False)
            st.caption("Income minus expenditure")
            st.line_chart(history_crore[["operating_balance"]].rename(columns={"operating_balance": "₹ crore"}))
    with change_column:
        with st.container(border=True):
            st.subheader("Year-on-year change", anchor=False)
            st.caption("Change from the previous reported year")
            st.bar_chart(history_crore[["income_change_percent", "expenditure_change_percent"]].rename(
                columns={
                    "income_change_percent": "Income (%)",
                    "expenditure_change_percent": "Expenditure (%)",
                }
            ))
    with share_column:
        with st.container(border=True):
            st.subheader("Tax revenue share", anchor=False)
            st.caption("Tax revenue as a share of total income")
            st.line_chart(history_crore[["tax_revenue_share_percent"]].rename(
                columns={"tax_revenue_share_percent": "Tax revenue share (%)"}
            ))

    st.divider()
    change_column, range_column = st.columns(2)
    largest_change = analysis["largest_annual_change"]
    with change_column:
        with st.container(border=True):
            st.subheader("Largest annual movement", anchor=False)
            if largest_change:
                direction = "increase" if largest_change["percent"] >= 0 else "decrease"
                st.metric(
                    f"{largest_change['label']} — {largest_change['financial_year']}",
                    percent(abs(largest_change["percent"])),
                    direction,
                )
                st.caption("Largest absolute year-on-year movement across income and expenditure.")
    with range_column:
        with st.container(border=True):
            st.subheader("Financial stability range", anchor=False)
            stability = analysis["stability_range"]
            st.write(
                f"Strongest balance: **{rupees_in_crore(stability['strongest_balance'])}** "
                f"in **{stability['strongest_year']}**."
            )
            st.write(
                f"Weakest balance: **{rupees_in_crore(stability['weakest_balance'])}** "
                f"in **{stability['weakest_year']}**."
            )

    st.divider()
    st.subheader("Metric summary", anchor=False)
    st.caption("All reported Finance years. Every row retains its official SMC source link.")
    st.dataframe(analysis["summary_rows"], hide_index=True, width="stretch")
    st.link_button("View selected SMC balance sheet", selected["source_url"], width="stretch")
