"""Database access layer for EBMS, environment-aware.

APP_ENV=development (default) -> SQLite, zero setup, file lives in database/ebms_dev.db
APP_ENV=production            -> MySQL, pooled connections, reads DB_* from .env

Everything above this module (models/services) writes plain SQL with `%s`
placeholders and reads rows as dicts, regardless of which backend is
actually active; `_CursorAdapter` below hides the difference.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = BASE_DIR / "database"


def _detect_backend() -> str:
    env = os.getenv("APP_ENV", "development").strip().lower()
    return "mysql" if env == "production" else "sqlite"


DB_BACKEND = _detect_backend()

# A single exception type callers can catch regardless of backend, e.g. for
# UNIQUE constraint violations under concurrent inserts (check-then-insert
# races: two requests both pass an "already exists?" check before either
# commits). Production always has mysql-connector installed anyway, so this
# import isn't a burden the way the pooled connection setup would be.
if DB_BACKEND == "mysql":
    from mysql.connector import IntegrityError
else:
    from sqlite3 import IntegrityError

# ---------------------------------------------------------------- SQLite --
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", DATABASE_DIR / "ebms_dev.db"))


def _sqlite_connect():
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ----------------------------------------------------------------- MySQL --
_mysql_pool = None


def _get_mysql_pool():
    global _mysql_pool
    if _mysql_pool is None:
        # Imported lazily so dev machines without mysql-connector installed
        # (or a MySQL server running) never need it to run in dev mode.
        import mysql.connector
        from mysql.connector import pooling

        _mysql_pool = pooling.MySQLConnectionPool(
            pool_name="ebms_pool",
            pool_size=5,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME", "ebms_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
        )
    return _mysql_pool


# ------------------------------------------------------------- Adapters --
@contextmanager
def get_connection():
    """Yield a raw connection for the active backend."""
    if DB_BACKEND == "mysql":
        conn = _get_mysql_pool().get_connection()
        try:
            yield conn
        finally:
            conn.close()  # returns to the pool, doesn't kill it
    else:
        conn = _sqlite_connect()
        try:
            yield conn
        finally:
            conn.close()


class _CursorAdapter:
    """Wraps the backend's raw cursor so calling code can always write
    MySQL-style `%s` placeholders and always get dict rows back."""

    def __init__(self, cursor, backend):
        self._cursor = cursor
        self._backend = backend

    def execute(self, query, params=None):
        if self._backend == "sqlite":
            query = query.replace("%s", "?").replace("NOW()", "CURRENT_TIMESTAMP")
        self._cursor.execute(query, params or ())

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(row) if self._backend == "sqlite" else row

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(r) for r in rows] if self._backend == "sqlite" else rows

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def close(self):
        self._cursor.close()


@contextmanager
def get_cursor(dictionary=True, commit=False):
    """Yield a cursor on a connection for the active backend; optionally
    commits on success and always rolls back on error."""
    with get_connection() as conn:
        raw_cursor = conn.cursor(dictionary=dictionary) if DB_BACKEND == "mysql" else conn.cursor()
        cursor = _CursorAdapter(raw_cursor, DB_BACKEND)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


def init_db():
    """Create tables if they don't exist yet. Safe to call on every startup."""
    schema_file = "schema_mysql.sql" if DB_BACKEND == "mysql" else "schema_sqlite.sql"
    sql = (DATABASE_DIR / schema_file).read_text(encoding="utf-8")

    with get_connection() as conn:
        if DB_BACKEND == "sqlite":
            conn.executescript(sql)
            conn.commit()
        else:
            cursor = conn.cursor()
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            conn.commit()
            cursor.close()
