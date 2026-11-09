import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .schemas import (
    MAX_ASSIGNEE_LENGTH,
    MAX_ATTACHMENT_SIZE,
    MAX_DESCRIPTION_LENGTH,
    MAX_LINK_LABEL_LENGTH,
    MAX_LINK_URL_LENGTH,
    MAX_TAG_LENGTH,
    MAX_TITLE_LENGTH,
)

_APP_DIR = Path(__file__).resolve().parent.parent

# En Vercel el sistema de archivos es de solo lectura salvo /tmp (efímero):
# la base y los adjuntos viven ahí y no persisten entre despliegues.
_ON_VERCEL = bool(os.environ.get("VERCEL"))

DEFAULT_DB_PATH = Path("/tmp/kanban/tasks.db") if _ON_VERCEL else _APP_DIR / "tasks.db"
DEFAULT_STORAGE_PATH = (
    Path("/tmp/kanban/storage") if _ON_VERCEL else _APP_DIR / "storage"
)

CREATE_TASKS_TABLE = f"""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
        CHECK (length(trim(title)) BETWEEN 1 AND {MAX_TITLE_LENGTH}),
    description TEXT NOT NULL DEFAULT ''
        CHECK (length(description) <= {MAX_DESCRIPTION_LENGTH}),
    status TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK (status IN ('Pendiente', 'En curso', 'Terminada')),
    priority TEXT NOT NULL DEFAULT 'Media'
        CHECK (priority IN ('Baja', 'Media', 'Alta')),
    assignee TEXT NOT NULL DEFAULT ''
        CHECK (length(assignee) <= {MAX_ASSIGNEE_LENGTH}),
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

CREATE_TAGS_TABLE = f"""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
        CHECK (length(trim(name)) BETWEEN 1 AND {MAX_TAG_LENGTH})
)
"""

CREATE_TASK_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
)
"""

CREATE_LINKS_TABLE = f"""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    url TEXT NOT NULL CHECK (length(url) BETWEEN 8 AND {MAX_LINK_URL_LENGTH}),
    label TEXT NOT NULL DEFAULT '' CHECK (length(label) <= {MAX_LINK_LABEL_LENGTH}),
    created_at TEXT NOT NULL
)
"""

CREATE_ACTIVITY_TABLE = """
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
)
"""


def get_db_path() -> Path:
    return Path(os.environ.get("KANBAN_DB_PATH", DEFAULT_DB_PATH))


def get_storage_path() -> Path:
    return Path(os.environ.get("KANBAN_STORAGE_PATH", DEFAULT_STORAGE_PATH))


def _turso_url() -> str:
    return os.environ.get("TURSO_DATABASE_URL", "").strip()


def using_remote_db() -> bool:
    """Indica si la aplicación usa Turso en lugar de SQLite local."""
    return bool(_turso_url())


def get_connection() -> Any:
    url = _turso_url()
    if url:
        import turso_serverless

        connection = turso_serverless.connect(
            url,
            auth_token=os.environ.get("TURSO_AUTH_TOKEN") or None,
        )
        connection.row_factory = turso_serverless.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

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


def _table_columns(conn: sqlite3.Connection, name: str) -> set[str]:
    return {
        row["name"] for row in conn.execute(f"PRAGMA table_info({name})").fetchall()
    }


REQUIRED_TASK_COLUMNS = {
    "description",
    "due_date",
    "position",
    "deleted_at",
    "priority",
    "assignee",
}

# Definiciones usadas para completar columnas faltantes de forma aditiva.
MISSING_TASK_COLUMN_DEFINITIONS = {
    "description": "description TEXT NOT NULL DEFAULT ''",
    "due_date": "due_date TEXT",
    "position": "position INTEGER NOT NULL DEFAULT 0",
    "deleted_at": "deleted_at TEXT",
    "priority": "priority TEXT NOT NULL DEFAULT 'Media'",
    "assignee": "assignee TEXT NOT NULL DEFAULT ''",
}


def _needs_migration(conn: sqlite3.Connection) -> bool:
    """Detecta si a `tasks` le falta alguna columna esperada del esquema."""
    if _table_sql(conn, "tasks") is None:
        return False
    return bool(REQUIRED_TASK_COLUMNS - _table_columns(conn, "tasks"))


def _migrate_tasks(conn: sqlite3.Connection) -> None:
    """Migración aditiva: agrega las columnas faltantes sin recrear la tabla.

    No se renombra ni se recrea `tasks` para no romper las claves foráneas de
    subtasks/attachments que apuntan a esta tabla.
    """
    columns = _table_columns(conn, "tasks")
    for name, definition in MISSING_TASK_COLUMN_DEFINITIONS.items():
        if name not in columns:
            try:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {definition}")
            except Exception as exc:
                # Dos instancias pueden migrar a la vez en un arranque en frío.
                if "duplicate column" not in str(exc).lower():
                    raise


def _attachments_table_outdated(conn: sqlite3.Connection) -> bool:
    """Detecta si el ``CHECK`` de tamaño de `attachments` quedó desactualizado.

    El límite se incrusta en el ``CREATE TABLE``; como ``CREATE TABLE IF NOT
    EXISTS`` no lo actualiza en bases existentes, se compara el SQL guardado
    con el definido por la aplicación.
    """
    sql = _table_sql(conn, "attachments")
    if sql is None:
        return False
    return " ".join(sql.split()) != " ".join(CREATE_ATTACHMENTS_TABLE.split())


def _migrate_attachments(conn: sqlite3.Connection) -> None:
    """Reconstruye `attachments` para aplicar el nuevo límite de tamaño.

    SQLite no permite modificar una restricción ``CHECK``, así que se renombra,
    se crea la tabla actualizada y se copian las filas. Nada referencia a
    `attachments`, por lo que el reemplazo no rompe claves foráneas.
    """
    conn.execute("ALTER TABLE attachments RENAME TO attachments_legacy")
    conn.execute(CREATE_ATTACHMENTS_TABLE)
    conn.execute(
        "INSERT INTO attachments (id, task_id, filename, stored_name, "
        "content_type, size_bytes, created_at) "
        "SELECT id, task_id, filename, stored_name, content_type, size_bytes, "
        "created_at FROM attachments_legacy"
    )
    conn.execute("DROP TABLE attachments_legacy")


def init_db() -> None:
    if (
        _ON_VERCEL
        and not using_remote_db()
        and os.environ.get("KANBAN_ALLOW_EPHEMERAL") != "1"
    ):
        raise RuntimeError(
            "TURSO_DATABASE_URL no está configurada. En Vercel el sistema de "
            "archivos es efímero y cada instancia vería una base distinta. "
            "Configurá Turso o definí KANBAN_ALLOW_EPHEMERAL=1 para permitir "
            "una base temporal."
        )

    if not using_remote_db():
        db_path = get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)

    from .storage import ensure_storage_ready

    ensure_storage_ready()

    with connection() as conn:
        if _needs_migration(conn):
            _migrate_tasks(conn)
        if _attachments_table_outdated(conn):
            _migrate_attachments(conn)
        conn.execute(CREATE_TASKS_TABLE)
        conn.execute(CREATE_SUBTASKS_TABLE)
        conn.execute(CREATE_ATTACHMENTS_TABLE)
        conn.execute(CREATE_TAGS_TABLE)
        conn.execute(CREATE_TASK_TAGS_TABLE)
        conn.execute(CREATE_LINKS_TABLE)
        conn.execute(CREATE_ACTIVITY_TABLE)
