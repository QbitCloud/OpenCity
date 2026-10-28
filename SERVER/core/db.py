"""Read-only access to the pipeline's SQLite database. The pipeline is the only writer."""
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from fastapi import HTTPException

from . import config


def connect(path=None) -> sqlite3.Connection:
    path = Path(path or config.DB_PATH)
    if not path.exists():
        raise HTTPException(503, f'database not found: run the pipeline refresh first ({path.name})')
    # as_uri() percent-encodes the path, so a '#' or '?' in a folder name cannot drop mode=ro
    conn = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_conn() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one read-only connection per request. The explicit transaction makes every query
    in the request read the same snapshot, even while the pipeline is writing."""
    conn = connect()
    try:
        conn.execute('BEGIN')
        yield conn
    finally:
        conn.close()


def rows(conn: sqlite3.Connection, sql: str, params=()) -> List[Dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params)]


def one(conn: sqlite3.Connection, sql: str, params=()) -> Optional[Dict[str, Any]]:
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None


def loads(text: Optional[str]) -> Dict[str, Any]:
    return json.loads(text) if text else {}


def json_path(key: str) -> str:
    """'mode' -> '$."mode"', for json_extract. Keys come from the URL, so only ASCII names are allowed."""
    if not key or not all(ch.isascii() and (ch.isalnum() or ch == '_') for ch in key):
        raise HTTPException(422, f'invalid field name {key!r}: use letters, digits and _ only')
    return f'$."{key}"'


def parse_pairs(pairs: List[str], name: str) -> List[Tuple[str, str]]:
    """['mode:truck', 'account:revenue'] -> [('mode', 'truck'), ('account', 'revenue')]."""
    if len(pairs) > config.MAX_FILTERS:
        raise HTTPException(422, f'at most {config.MAX_FILTERS} {name} filters per request')
    out = []
    for p in pairs:
        key, sep, value = p.partition(':')
        if not sep:
            raise HTTPException(422, f'{name} must look like key:value, got {p!r}')
        json_path(key)
        out.append((key, value))
    return out


def field_matches(column: str) -> str:
    """SQL test that a JSON field equals a value from the URL, as the API shows it: text and numbers as
    written, booleans as true/false, and a list matches if any element does. Takes (path, value, value)."""
    return (f"EXISTS (SELECT 1 FROM json_each({column}, ?) j WHERE "
            "CASE WHEN j.type IN ('true', 'false') THEN j.type ELSE CAST(j.value AS TEXT) END IN (?, ?))")


def match_params(key: str, value: str) -> List[str]:
    """Parameters for field_matches(). '1' also matches true and '0' false, as SQLite stores them."""
    alias = {'1': 'true', '0': 'false'}.get(value, value)
    return [json_path(key), value, alias]


def like(text: str) -> str:
    """Escape a user string for LIKE ... ESCAPE '\\'."""
    return '%' + text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
