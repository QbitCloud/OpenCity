import requests
import streamlit as st

from clients.client import get_finance_summary


def _rupees(value: float) -> str:
    """Use crore for a compact, readable public dashboard figure."""
    return f"₹{value / 10_000_000:,.1f} crore"


def show_finance() -> None:
    st.title("SMC Finance")
    st.write("Latest annual figures from Surat Municipal Corporation's published balance sheet.")

    try:
        data = get_finance_summary()
        metrics = data["metrics"]
        if not metrics:
            st.info("No finance data is available yet.")
            return

        columns = st.columns(len(metrics))
        for column, metric in zip(columns, metrics):
            column.metric(metric["label"], _rupees(metric["value"]))

        st.caption(f"{data['financial_year']} | Geography: {data['geography']}")
        st.markdown(f"[Source: Surat Municipal Corporation]({data['source_url']})")
        st.caption(f"Data retrieved: {data['retrieved_at']}")
    except requests.exceptions.HTTPError:
        st.warning("Finance data is unavailable from the API. Run the finance pipeline first.")
    except requests.exceptions.RequestException:
        st.warning("Cannot reach the backend. Check that it is running.")
    except (KeyError, TypeError, ValueError):
        st.error("The finance-data response has an unexpected format.")
