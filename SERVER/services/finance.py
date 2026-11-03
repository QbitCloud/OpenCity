"""Read the latest annual SMC finance figures exported by the pipeline."""
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "export" / "observations" / "smc_balance_sheet.csv"

METRICS = {
    "finance.total_income": "Total income",
    "finance.total_expenditure": "Total expenditure",
    "finance.excess_income_over_expenditure": "Excess of income over expenditure",
    "finance.tax_revenue": "Tax revenue",
}


def load_finance_summary():
    rows = []
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if (
                row["metric_id"] in METRICS
                and row["geo_level"] == "smc_city"
                and row["geo_code"] == "smc"
                and row["status"] == "reported"
                and row["value"]
            ):
                rows.append(row)

    if not rows:
        return {"metrics": []}

    latest_start = max(row["period_start"] for row in rows)
    latest = [row for row in rows if row["period_start"] == latest_start]
    latest.sort(key=lambda row: list(METRICS).index(row["metric_id"]))

    return {
        "financial_year": f"FY {latest_start[:4]}-{str(int(latest_start[:4]) + 1)[-2:]}",
        "unit": "rupees",
        "geography": "SMC city",
        "source_url": latest[0]["source_url"],
        "retrieved_at": latest[0]["retrieved_at"],
        "metrics": [
            {"id": row["metric_id"], "label": METRICS[row["metric_id"]], "value": float(row["value"])}
            for row in latest
        ],
    }
