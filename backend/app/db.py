import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data.db"

PREVIEW_LENGTH = 120


def _connect() -> sqlite3.Connection:
    # Read on every connection so tests can point DB_PATH at a temp file.
    conn = sqlite3.connect(os.getenv("DB_PATH") or DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def _row_to_entry(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "text": row["text"],
        "summary": row["summary"],
        "tags": json.loads(row["tags"]),
        "created_at": row["created_at"],
    }


def create_entry(text: str, summary: str, tags: list[str]) -> dict:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO entries (text, summary, tags, created_at) VALUES (?, ?, ?, ?)",
            (text, summary, json.dumps(tags), created_at),
        )
        entry_id = cursor.lastrowid
    return {
        "id": entry_id,
        "text": text,
        "summary": summary,
        "tags": tags,
        "created_at": created_at,
    }


def list_entries() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY id DESC").fetchall()
    entries = []
    for row in rows:
        entry = _row_to_entry(row)
        entry["preview"] = entry.pop("text")[:PREVIEW_LENGTH]
        entries.append(entry)
    return entries


def get_entry(entry_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    return _row_to_entry(row) if row else None
