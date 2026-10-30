import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .schemas import (
    MAX_ATTACHMENT_SIZE,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
)

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "tasks.db"
DEFAULT_STORAGE_PATH = Path(__file__).resolve().parent.parent / "storage"

CREATE_TASKS_TABLE = f"""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
        CHECK (length(trim(title)) BETWEEN 1 AND {MAX_TITLE_LENGTH}),
    description TEXT NOT NULL DEFAULT ''
        CHECK (length(description) <= {MAX_DESCRIPTION_LENGTH}),
    status TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK (status IN ('Pendiente', 'En curso', 'Terminada')),
    due_date TEXT CHECK (
        due_date IS NULL
        OR due_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),
    position INTEGER NOT NULL DEFAULT 0 CHECK (position >= 0),
    deleted_at TEXT,
    created_at TEXT NOT NULL
)
"""

CREATE_SUBTASKS_TABLE = """
CREATE TABLE IF NOT EXISTS subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 100),
    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    created_at TEXT NOT NULL
)
"""

CREATE_ATTACHMENTS_TABLE = f"""
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    content_type TEXT NOT NULL DEFAULT 'application/octet-stream',
    size_bytes INTEGER NOT NULL
        CHECK (size_bytes > 0 AND size_bytes <= {MAX_ATTACHMENT_SIZE}),
    created_at TEXT NOT NULL
)
"""


def get_db_path() -> Path:
    return Path(os.environ.get("KANBAN_DB_PATH", DEFAULT_DB_PATH))


def get_storage_path() -> Path:
    return Path(os.environ.get("KANBAN_STORAGE_PATH", DEFAULT_STORAGE_PATH))


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
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


def _table_sql(conn: sqlite3.Connection, name: str) -> str | None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone()
    return row["sql"] if row is not None else None


def _needs_migration(conn: sqlite3.Connection) -> bool:
    """Detecta un esquema anterior de `tasks` (sin CHECK ni columnas nuevas)."""
    sql = _table_sql(conn, "tasks")
    if sql is None:
        return False
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
    }
    required = {"description", "due_date", "position", "deleted_at"}
    return "CHECK" not in sql or not required <= columns


def _migrate_tasks(conn: sqlite3.Connection) -> None:
    conn.execute("ALTER TABLE tasks RENAME TO tasks_legacy")
    conn.execute(CREATE_TASKS_TABLE)
    conn.execute(
        """
        INSERT INTO tasks (id, title, description, status, due_date, position,
                           deleted_at, created_at)
        SELECT id, title, '', status, NULL, 0, NULL, created_at
        FROM tasks_legacy
        """
    )
    conn.execute("DROP TABLE tasks_legacy")
    conn.execute(
        """
        UPDATE tasks SET position = (
            SELECT COUNT(*) FROM tasks AS previous
            WHERE previous.status = tasks.status
              AND previous.id < tasks.id
        )
        """
    )


def init_db() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    get_storage_path().mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        if _needs_migration(conn):
            _migrate_tasks(conn)
        conn.execute(CREATE_TASKS_TABLE)
        conn.execute(CREATE_SUBTASKS_TABLE)
        conn.execute(CREATE_ATTACHMENTS_TABLE)
