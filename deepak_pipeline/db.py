"""Local storage for official finance document links."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "deepak_finance.db"


def connect() -> sqlite3.Connection:
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
    return connection


def save_document(
    connection: sqlite3.Connection,
    financial_year: str,
    url: str,
    discovered_at: str,
) -> None:
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
    """Save one year's Finance values without creating duplicates."""
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
    """Return saved values in year and metric order."""
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
