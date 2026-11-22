from pymongo import MongoClient
from pymongo.errors import PyMongoError

from opencity_settings import MONGODB_DB, MONGODB_URI

is_connected = False

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    finance_documents = client[MONGODB_DB]["finance_source_documents"]
    finance_collection = client[MONGODB_DB]["finance_observations"]
    water_documents = client[MONGODB_DB]["water_source_documents"]
    water_collection = client[MONGODB_DB]["water_observations"]
    is_connected = True
except PyMongoError:
    print("MongoDB connection failed")


def save_document(financial_year, url, discovered_at):
    # Keep one link per financial year. Replace it if the page changes later.
    finance_documents.delete_many({"financial_year": financial_year})
    finance_documents.insert_one(
        {"financial_year": financial_year, "url": url, "discovered_at": discovered_at}
    )


def save_finance_year(finance_data, source_url):
    financial_year = finance_data["financial_year"]
    amount_unit = finance_data["amount_unit"]

    observations = [
        {
            "financial_year": financial_year,
            "metric_id": metric_id,
            "value": float(value),
            "amount_unit": amount_unit,
            "source_url": source_url,
        }
        for metric_id, value in finance_data.items()
        if metric_id not in {"financial_year", "amount_unit"}
    ]

    if not observations:
        raise ValueError("No new data, Existing records were kept.")

    # Replace this year's values with the new reading, so nothing is duplicated.
    finance_collection.delete_many({"financial_year": financial_year})
    finance_collection.insert_many(observations)


def save_water_document(period_start, url, discovered_at):
    # Keep one report link per month. Replace it if it changes later.
    water_documents.delete_many({"period_start": period_start})
    water_documents.insert_one(
        {"period_start": period_start, "url": url, "discovered_at": discovered_at}
    )


def save_water_month(water_data, source_url):
    period_start = water_data["period_start"]
    values = {
        "water.samples_collected": water_data["samples_collected"],
        "water.samples_fit": water_data["samples_fit"],
        "water.samples_unfit": water_data["samples_unfit"],
        "water.compliance_rate_percent": water_data["compliance_rate_percent"],
    }

    observations = [
        {
            "period_start": period_start,
            "metric_id": metric_id,
            "value": float(value),
            "source_url": source_url,
        }
        for metric_id, value in values.items()
    ]

    # Replace this month's values with the new reading, so nothing is duplicated.
    water_collection.delete_many({"period_start": period_start})
    water_collection.insert_many(observations)
