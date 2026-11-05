"""P1 的 SQLite 数据访问层。"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "customers.db"


def get_db_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))


def connect() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_customers(keyword: str = "") -> list[sqlite3.Row]:
    conn = connect()
    try:
        keyword = keyword.strip()
        if keyword:
            escaped = (
                keyword.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            pattern = f"%{escaped}%"
            rows = conn.execute(
                """
                SELECT id, name, phone, company, note, created_at
                FROM customers
                WHERE name LIKE ? ESCAPE '\\'
                   OR phone LIKE ? ESCAPE '\\'
                ORDER BY id DESC
                """,
                (pattern, pattern),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, name, phone, company, note, created_at
                FROM customers
                ORDER BY id DESC
                """
            ).fetchall()
        return list(rows)
    finally:
        conn.close()


def create_customer(name: str, phone: str, company: str, note: str) -> int:
    conn = connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO customers (name, phone, company, note, created_at)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            """,
            (name, phone, company, note),
        )
        conn.commit()
        return int(cur.lastrowid or 0)
    finally:
        conn.close()
