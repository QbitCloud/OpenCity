"""Local SQLite storage for official Finance and Water Quality observations."""
from __future__ import annotations

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "deepak_finance.db"


def connect() -> sqlite3.Connection:
    """Open the local database and create its duplicate-prevention tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS source_document (
            financial_year TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            discovered_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS finance_observation (
            financial_year TEXT NOT NULL,
            metric_id TEXT NOT NULL,
            value REAL NOT NULL,
            amount_unit TEXT NOT NULL,
            source_url TEXT NOT NULL,
            PRIMARY KEY (financial_year, metric_id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS water_source_document (
            period_start TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            discovered_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS water_observation (
            period_start TEXT NOT NULL,
            metric_id TEXT NOT NULL,
            value REAL NOT NULL,
            source_url TEXT NOT NULL,
            PRIMARY KEY (period_start, metric_id)
        )
        """
    )
    connection.commit()
    return connection


def save_document(
    connection: sqlite3.Connection,
    financial_year: str,
    url: str,
    discovered_at: str,
) -> None:
    """Save one official PDF link, replacing it if the page changes later."""
    connection.execute(
        """
        INSERT INTO source_document (financial_year, url, discovered_at)
        VALUES (?, ?, ?)
        ON CONFLICT(financial_year) DO UPDATE SET
            url = excluded.url,
            discovered_at = excluded.discovered_at
        """,
        (financial_year, url, discovered_at),
    )
    connection.commit()


def save_finance_year(
    connection: sqlite3.Connection,
    finance_data: dict,
    source_url: str,
) -> None:
    """Save one year's metrics without creating duplicate observations."""
    financial_year = finance_data["financial_year"]
    amount_unit = finance_data["amount_unit"]

    for metric_id, value in finance_data.items():
        if metric_id in {"financial_year", "amount_unit"}:
            continue

        connection.execute(
            """
            INSERT INTO finance_observation (
                financial_year,
                metric_id,
                value,
                amount_unit,
                source_url
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(financial_year, metric_id) DO UPDATE SET
                value = excluded.value,
                amount_unit = excluded.amount_unit,
                source_url = excluded.source_url
            """,
            (
                financial_year,
                metric_id,
                value,
                amount_unit,
                source_url,
            ),
        )

    connection.commit()


def read_finance_observations() -> list[dict]:
    """Return Finance observations in financial-year and metric order."""
    connection = connect()
    rows = connection.execute(
        """
        SELECT financial_year, metric_id, value, amount_unit, source_url
        FROM finance_observation
        ORDER BY financial_year, metric_id
        """
    ).fetchall()
    connection.close()

    return [
        {
            "financial_year": financial_year,
            "metric_id": metric_id,
            "value": value,
            "amount_unit": amount_unit,
            "source_url": source_url,
        }
        for financial_year, metric_id, value, amount_unit, source_url in rows
    ]


def save_water_document(
    connection: sqlite3.Connection,
    period_start: str,
    url: str,
    discovered_at: str,
) -> None:
    """Save a Water Quality report link, replacing it if it changes later."""
    connection.execute(
        """
        INSERT INTO water_source_document (period_start, url, discovered_at)
        VALUES (?, ?, ?)
        ON CONFLICT(period_start) DO UPDATE SET
            url = excluded.url,
            discovered_at = excluded.discovered_at
        """,
        (period_start, url, discovered_at),
    )
    connection.commit()


def save_water_month(
    connection: sqlite3.Connection,
    water_data: dict,
    source_url: str,
) -> None:
    """Save one month's clear Water Quality metrics without duplicates."""
    period_start = water_data["period_start"]
    values = {
        "water.samples_collected": water_data["samples_collected"],
        "water.samples_fit": water_data["samples_fit"],
        "water.samples_unfit": water_data["samples_unfit"],
        "water.compliance_rate_percent": water_data["compliance_rate_percent"],
    }

    for metric_id, value in values.items():
        connection.execute(
            """
            INSERT INTO water_observation (period_start, metric_id, value, source_url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(period_start, metric_id) DO UPDATE SET
                value = excluded.value,
                source_url = excluded.source_url
            """,
            (period_start, metric_id, value, source_url),
        )

    connection.commit()


def read_water_observations() -> list[dict]:
    """Return Water Quality observations in month and metric order."""
    connection = connect()
    rows = connection.execute(
        """
        SELECT period_start, metric_id, value, source_url
        FROM water_observation
        ORDER BY period_start, metric_id
        """
    ).fetchall()
    connection.close()

    return [
        {
            "period_start": period_start,
            "metric_id": metric_id,
            "value": value,
            "source_url": source_url,
        }
        for period_start, metric_id, value, source_url in rows
    ]
