"""Save the official historic finance documents."""
from datetime import datetime
from zoneinfo import ZoneInfo

from deepak_pipeline.db import connect, save_document
from deepak_pipeline.scrapper import discover_balance_sheets


def financial_year(start_year: int) -> str:
    return f"FY {start_year}-{str(start_year + 1)[-2:]}"


def discovery_summary(reports: dict[int, str]) -> str:
    if not reports:
        return "No official balance-sheet links were found."
    years = sorted(reports)
    return (
        f"Saved {len(reports)} official balance-sheet links: "
        f"{financial_year(years[0])} to {financial_year(years[-1])}."
    )


def run() -> int:
    discovered_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    reports = discover_balance_sheets()
    connection = connect()

    for start_year, url in reports.items():
        save_document(connection, financial_year(start_year), url, discovered_at)

    connection.close()
    print(discovery_summary(reports))
    return len(reports)


if __name__ == "__main__":
    run()
