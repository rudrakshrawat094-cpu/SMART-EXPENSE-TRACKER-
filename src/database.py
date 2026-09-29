"""Storage layer: thin wrapper over sqlite3 using parameterised queries only (prevents SQL injection)."""
import sqlite3
from pathlib import Path

from .config import DB_PATH
from .exceptions import DatabaseError, DuplicateError
from .logger import get_logger

log = get_logger("database")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      REAL NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    date        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS budgets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category     TEXT NOT NULL,
    month        TEXT NOT NULL,
    limit_amount REAL NOT NULL CHECK (limit_amount > 0),
    UNIQUE (user_id, category, month)
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses (user_id, date);
"""


class Database:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        try:
            if self.path != ":memory:":
                Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.executescript(SCHEMA)
        except (sqlite3.Error, OSError) as exc:
            log.exception("Could not open database %s", self.path)
            raise DatabaseError(f"Could not open database: {exc}") from exc

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        """Run a write statement inside a transaction (auto-commit / rollback)."""
        try:
            with self.conn:
                return self.conn.execute(sql, params)
        except sqlite3.IntegrityError as exc:
            log.warning("Integrity error: %s", exc)
            raise DuplicateError(str(exc)) from exc
        except sqlite3.Error as exc:
            log.exception("Database write failed")
            raise DatabaseError(str(exc)) from exc

    def query(self, sql: str, params=()) -> list:
        try:
            return self.conn.execute(sql, params).fetchall()
        except sqlite3.Error as exc:
            log.exception("Database read failed")
            raise DatabaseError(str(exc)) from exc

    def query_one(self, sql: str, params=()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def close(self) -> None:
        self.conn.close()
