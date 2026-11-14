"""Save official Finance documents and their historic values."""
import argparse
from datetime import datetime
import time
from zoneinfo import ZoneInfo

from deepak_pipeline.db import connect, save_document, save_finance_year
from deepak_pipeline.parser import read_balance_sheet_pdf
from deepak_pipeline.scrapper import (
    discover_balance_sheets,
    fetch_document,
)


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


def run(first_financial_year: int = 2007) -> int:
    discovered_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    reports = discover_balance_sheets()
    database = connect()

    saved_years = 0

    for start_year, url in reports.items():
        save_document(database, financial_year(start_year), url, discovered_at)

        if start_year < first_financial_year:
            continue

        finance_data = read_balance_sheet_pdf(fetch_document(url))
        save_finance_year(database, finance_data, url)
        saved_years += 1
        time.sleep(1)

    print(discovery_summary(reports))
    print(f"Saved Finance values for {saved_years} years.")
    return len(reports)


if __name__ == "__main__":
    command = argparse.ArgumentParser(
        description="Store official SMC Finance observations."
    )
    command.add_argument(
        "--from-year",
        type=int,
        default=2007,
        help="First financial-year start to parse (default: 2007).",
    )
    arguments = command.parse_args()
    run(arguments.from_year)
