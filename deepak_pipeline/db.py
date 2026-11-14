"""MongoDB storage for Deepak's Finance pipeline."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from dotenv import load_dotenv


DOCUMENTS = "deepak_finance_documents"
OBSERVATIONS = "deepak_finance_observations"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


@lru_cache
def get_client() -> MongoClient:
    """Create one reusable MongoDB client from local environment settings."""
    mongo_uri = os.environ.get("MONGODB_URI")

    if not mongo_uri:
        raise RuntimeError("Set MONGODB_URI before running the Finance pipeline.")

    return MongoClient(mongo_uri, serverSelectionTimeoutMS=10_000)


def connect() -> Database:
    """Return the Finance database and create its duplicate-prevention indexes."""
    database_name = os.environ.get("MONGODB_DATABASE", "opencity")
    database = get_client()[database_name]

    database[DOCUMENTS].create_index("financial_year", unique=True)
    database[OBSERVATIONS].create_index(
        [("financial_year", ASCENDING), ("metric_id", ASCENDING)],
        unique=True,
    )

    return database


def save_document(
    database: Database,
    financial_year: str,
    url: str,
    discovered_at: str,
) -> None:
    """Save one official PDF link, replacing it if the page changes later."""
    database[DOCUMENTS].update_one(
        {"financial_year": financial_year},
        {
            "$set": {
                "financial_year": financial_year,
                "url": url,
                "discovered_at": discovered_at,
            }
        },
        upsert=True,
    )


def save_finance_year(
    database: Database,
    finance_data: dict,
    source_url: str,
) -> None:
    """Save one year's metrics without creating duplicate observations."""
    financial_year = finance_data["financial_year"]
    amount_unit = finance_data["amount_unit"]

    for metric_id, value in finance_data.items():
        if metric_id in {"financial_year", "amount_unit"}:
            continue

        database[OBSERVATIONS].update_one(
            {
                "financial_year": financial_year,
                "metric_id": metric_id,
            },
            {
                "$set": {
                    "financial_year": financial_year,
                    "metric_id": metric_id,
                    "value": value,
                    "amount_unit": amount_unit,
                    "source_url": source_url,
                }
            },
            upsert=True,
        )


def read_finance_observations() -> list[dict]:
    """Return Finance observations in financial-year and metric order."""
    rows = connect()[OBSERVATIONS].find({}, {"_id": 0}).sort(
        [("financial_year", ASCENDING), ("metric_id", ASCENDING)]
    )
    return list(rows)
