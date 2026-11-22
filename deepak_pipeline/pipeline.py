"""Save official Finance and Water Quality documents and historic values."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from deepak_pipeline.db import (
    is_connected,
    save_document,
    save_finance_year,
    save_water_document,
    save_water_month,
)
from deepak_pipeline.parser import read_balance_sheet_pdf, read_water_quality_pdf
from deepak_pipeline.scrapper import (
    discover_balance_sheets,
    discover_water_quality_reports,
    fetch_document,
    polite_pause,
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


def run_finance(first_financial_year: int = 2007) -> int:
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return 0

    discovered_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    reports = discover_balance_sheets()
    saved_years = 0

    for start_year, url in reports.items():
        save_document(financial_year(start_year), url, discovered_at)

        if start_year < first_financial_year:
            continue

        finance_data = read_balance_sheet_pdf(fetch_document(url))
        save_finance_year(finance_data, url)
        saved_years += 1
        polite_pause()

    print(discovery_summary(reports))
    print(f"Saved Finance values for {saved_years} years.")
    return len(reports)


def run_water(first_year: int = 2024) -> int:
    """Discover and store official monthly drinking-water sample totals."""
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return 0

    discovered_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    reports = discover_water_quality_reports()
    saved_months = 0

    for (year, month), url in reports.items():
        period_start = f"{year}-{month:02d}-01"
        save_water_document(period_start, url, discovered_at)

        if year < first_year:
            continue

        water_data = read_water_quality_pdf(fetch_document(url), year, month)
        save_water_month(water_data, url)
        saved_months += 1
        polite_pause()

    print(f"Saved {len(reports)} official Water Quality report links.")
    print(f"Saved Water Quality values for {saved_months} months.")
    return len(reports)


def run(first_financial_year: int = 2007) -> int:
    """Keep the original Finance-only function available for existing users."""
    return run_finance(first_financial_year)


if __name__ == "__main__":
    command = argparse.ArgumentParser(
        description="Store official SMC Finance or Water Quality observations."
    )
    command.add_argument(
        "--finance-from-year",
        type=int,
        default=2007,
        help="First financial-year start to parse (default: 2007).",
    )
    command.add_argument(
        "--water-from-year",
        type=int,
        help="First calendar year of monthly Water Quality reports to parse.",
    )
    arguments = command.parse_args()

    if arguments.water_from_year is not None:
        run_water(arguments.water_from_year)
    else:
        run_finance(arguments.finance_from_year)
