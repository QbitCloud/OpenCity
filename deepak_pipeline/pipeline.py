"""Save the official historic finance documents."""
from datetime import datetime
from zoneinfo import ZoneInfo

from deepak_pipeline.db import connect, save_document
from deepak_pipeline.scrapper import discover_balance_sheets


def run() -> int:
    discovered_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    reports = discover_balance_sheets()
    connection = connect()

    for start_year, url in reports.items():
        financial_year = f"{start_year}-{str(start_year + 1)[-2:]}"
        save_document(connection, financial_year, url, discovered_at)

    connection.close()
    print(f"Saved {len(reports)} official balance-sheet links.")
    return len(reports)


if __name__ == "__main__":
    run()
