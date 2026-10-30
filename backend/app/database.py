import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "tasks.db"

CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 100),
    status TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK (status IN ('Pendiente', 'En curso', 'Terminada')),
    created_at TEXT NOT NULL
)
"""


def get_db_path() -> Path:
    return Path(os.environ.get("KANBAN_DB_PATH", DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _needs_migration(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'tasks'"
    ).fetchone()
    return row is not None and "CHECK" not in row["sql"]


def init_db() -> None:
    get_db_path().parent.mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        if _needs_migration(conn):
            conn.execute("ALTER TABLE tasks RENAME TO tasks_legacy")
            conn.execute(CREATE_TASKS_TABLE)
            conn.execute(
                """
                INSERT INTO tasks (id, title, status, created_at)
                SELECT id, title, status, created_at FROM tasks_legacy
                """
            )
            conn.execute("DROP TABLE tasks_legacy")
        else:
            conn.execute(CREATE_TASKS_TABLE)
