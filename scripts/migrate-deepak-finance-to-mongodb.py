"""Copy existing local Deepak Finance SQLite data to MongoDB once."""
import sqlite3
from pathlib import Path

from deepak_pipeline.db import connect, save_document, save_finance_year


SQLITE_PATH = Path(__file__).resolve().parents[1] / "data" / "deepak_finance.db"


def run() -> None:
    if not SQLITE_PATH.exists():
        raise FileNotFoundError(f"SQLite data not found: {SQLITE_PATH}")

    old_database = sqlite3.connect(SQLITE_PATH)
    mongo_database = connect()

    document_rows = old_database.execute(
        "SELECT financial_year, url, discovered_at FROM source_document"
    ).fetchall()

    for financial_year, url, discovered_at in document_rows:
        save_document(mongo_database, financial_year, url, discovered_at)

    observation_rows = old_database.execute(
        """
        SELECT financial_year, metric_id, value, amount_unit, source_url
        FROM finance_observation
        """
    ).fetchall()

    values_by_year = {}
    for financial_year, metric_id, value, amount_unit, source_url in observation_rows:
        finance_data = values_by_year.setdefault(
            financial_year,
            {"financial_year": financial_year, "amount_unit": amount_unit},
        )
        finance_data[metric_id] = value
        finance_data["source_url"] = source_url

    for finance_data in values_by_year.values():
        source_url = finance_data.pop("source_url")
        save_finance_year(mongo_database, finance_data, source_url)

    old_database.close()
    print(f"Migrated {len(document_rows)} documents and {len(values_by_year)} Finance years.")


if __name__ == "__main__":
    run()
