from datetime import datetime, timezone
from typing import Optional

from .database import connection

DEFAULT_STATUS = "Pendiente"


def _row_to_dict(row) -> Optional[dict]:
    return dict(row) if row is not None else None


def create_task(title: str, status: str = DEFAULT_STATUS) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, status, created_at) VALUES (?, ?, ?)",
            (title, status, created_at),
        )
        task_id = cursor.lastrowid
    return get_task(task_id)


def list_tasks() -> list[dict]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id ASC").fetchall()
    return [dict(row) for row in rows]


def get_task(task_id: int) -> Optional[dict]:
    with connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_dict(row)


def update_task_status(task_id: int, status: str) -> Optional[dict]:
    with connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)
        )
        if cursor.rowcount == 0:
            return None
    return get_task(task_id)


def delete_task(task_id: int) -> bool:
    with connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0
