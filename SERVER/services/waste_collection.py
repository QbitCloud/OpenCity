import csv
import json
from pathlib import Path

# Locate the CSV relative to the project, not the terminal folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "export"
    / "observations"
    / "smc_swm.csv"
)


def load_waste_collection():
    observations = []

    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            mode = json.loads(row["dims"] or "{}").get("mode")

            if (
                row["metric_id"] != "swm.avg_collection_mt_per_day"
                or row["geo_level"] != "smc_city"
                or row["geo_code"] != "smc"
                or mode != "door_to_door"
            ):
                continue

            value = None
            if row["status"] == "reported" and row["value"]:
                value = float(row["value"])

            observations.append({
                "period_start": row["period_start"],
                "period_end": row["period_end"],
                "value": value,
                "status": row["status"],
                "source_url": row["source_url"],
                "retrieved_at": row["retrieved_at"],
            })

    observations.sort(key=lambda item: item["period_start"])

    return {
        "metric": "door_to_door_waste_collection",
        "unit": "metric tonnes per day",
        "geography": "SMC city",
        "observations": observations,
    }
