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
