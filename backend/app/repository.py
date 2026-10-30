from datetime import date, datetime, timezone
from typing import Optional

from .database import connection
from .schemas import MAX_ATTACHMENTS_PER_TASK

DEFAULT_STATUS = "Pendiente"
DONE_STATUS = "Terminada"
REOPEN_STATUS = "En curso"


class DomainError(Exception):
    """Regla de negocio incumplida; la capa de rutas la traduce a HTTP."""


class PendingSubtasksError(DomainError):
    def __init__(self, pending: int) -> None:
        self.pending = pending
        super().__init__("La tarea tiene subtareas pendientes")


class AttachmentLimitError(DomainError):
    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"Una tarea no puede tener más de {limit} archivos adjuntos")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_iso() -> str:
    return date.today().isoformat()


def _as_iso(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value is not None else None


def _active_row(conn, task_id: int):
    return conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND deleted_at IS NULL", (task_id,)
    ).fetchone()


def _subtasks_of(conn, task_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC", (task_id,)
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def _attachments_of(conn, task_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM attachments WHERE task_id = ? ORDER BY id ASC", (task_id,)
    ).fetchall()
    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "content_type": row["content_type"],
            "size_bytes": row["size_bytes"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def _task_dict(conn, row) -> dict:
    subtasks = _subtasks_of(conn, row["id"])
    due_date = row["due_date"]
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "due_date": due_date,
        "position": row["position"],
        "created_at": row["created_at"],
        "overdue": bool(due_date)
        and due_date < _today_iso()
        and row["status"] != DONE_STATUS,
        "subtask_total": len(subtasks),
        "subtask_done": sum(1 for item in subtasks if item["done"]),
        "subtasks": subtasks,
        "attachments": _attachments_of(conn, row["id"]),
    }


def _recalculate_positions(conn, status: str) -> None:
    """Reindexa la columna para mantener posiciones 0..n-1 sin huecos."""
    rows = conn.execute(
        "SELECT id FROM tasks WHERE status = ? AND deleted_at IS NULL "
        "ORDER BY position ASC, id ASC",
        (status,),
    ).fetchall()
    for index, row in enumerate(rows):
        conn.execute("UPDATE tasks SET position = ? WHERE id = ?", (index, row["id"]))


def _apply_move(conn, task_id: int, source_status: str, status: str, position):
    """Reubica la tarea dentro de la columna destino y reindexa ambas."""
    target_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM tasks WHERE status = ? AND deleted_at IS NULL "
            "AND id <> ? ORDER BY position ASC, id ASC",
            (status, task_id),
        ).fetchall()
    ]
    if position is None:
        index = len(target_ids)
    else:
        index = max(0, min(position, len(target_ids)))
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    target_ids.insert(index, task_id)
    for order, item_id in enumerate(target_ids):
        conn.execute("UPDATE tasks SET position = ? WHERE id = ?", (order, item_id))
    if source_status != status:
        _recalculate_positions(conn, source_status)


def create_task(
    title: str, description: str = "", due_date: Optional[date] = None
) -> dict:
    with connection() as conn:
        position = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks WHERE status = ? "
            "AND deleted_at IS NULL",
            (DEFAULT_STATUS,),
        ).fetchone()["total"]
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, status, due_date, position, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                title,
                description,
                DEFAULT_STATUS,
                _as_iso(due_date),
                position,
                _now_iso(),
            ),
        )
        task_id = cursor.lastrowid
    return get_task(task_id)


def list_tasks(overdue_only: bool = False) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY "
            "CASE status WHEN 'Pendiente' THEN 0 WHEN 'En curso' THEN 1 ELSE 2 END, "
            "position ASC, id ASC"
        ).fetchall()
        tasks = [_task_dict(conn, row) for row in rows]
    if overdue_only:
        tasks = [task for task in tasks if task["overdue"]]
    return tasks


def get_task(task_id: int) -> Optional[dict]:
    with connection() as conn:
        row = _active_row(conn, task_id)
        return _task_dict(conn, row) if row is not None else None


def update_task(
    task_id: int,
    title: str,
    description: str = "",
    due_date: Optional[date] = None,
) -> Optional[dict]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, due_date = ? WHERE id = ?",
            (title, description, _as_iso(due_date), task_id),
        )
    return get_task(task_id)


def move_task(task_id: int, status: str, position: Optional[int] = None):
    """Mueve o reordena la tarea. Devuelve None si no existe."""
    with connection() as conn:
        row = _active_row(conn, task_id)
        if row is None:
            return None
        if status == DONE_STATUS:
            pending = conn.execute(
                "SELECT COUNT(*) AS total FROM subtasks "
                "WHERE task_id = ? AND done = 0",
                (task_id,),
            ).fetchone()["total"]
            if pending > 0:
                raise PendingSubtasksError(pending)
        _apply_move(conn, task_id, row["status"], status, position)
    return get_task(task_id)


def delete_task(task_id: int) -> bool:
    """Marca la tarea como eliminada, conservándola para poder deshacer."""
    with connection() as conn:
        row = _active_row(conn, task_id)
        if row is None:
            return False
        conn.execute(
            "UPDATE tasks SET deleted_at = ? WHERE id = ?", (_now_iso(), task_id)
        )
        _recalculate_positions(conn, row["status"])
    return True


def restore_task(task_id: int) -> Optional[dict]:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND deleted_at IS NOT NULL",
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        position = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks WHERE status = ? "
            "AND deleted_at IS NULL",
            (row["status"],),
        ).fetchone()["total"]
        conn.execute(
            "UPDATE tasks SET deleted_at = NULL, position = ? WHERE id = ?",
            (position, task_id),
        )
    return get_task(task_id)


def create_subtask(task_id: int, title: str, done: bool = False) -> Optional[dict]:
    with connection() as conn:
        row = _active_row(conn, task_id)
        if row is None:
            return None
        conn.execute(
            "INSERT INTO subtasks (task_id, title, done, created_at) "
            "VALUES (?, ?, ?, ?)",
            (task_id, title, 1 if done else 0, _now_iso()),
        )
        if not done and row["status"] == DONE_STATUS:
            _apply_move(conn, task_id, DONE_STATUS, REOPEN_STATUS, None)
    return get_task(task_id)


def update_subtask(
    subtask_id: int, title: Optional[str] = None, done: Optional[bool] = None
) -> Optional[dict]:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM subtasks WHERE id = ?", (subtask_id,)
        ).fetchone()
        if row is None or _active_row(conn, row["task_id"]) is None:
            return None
        task_id = row["task_id"]
        if title is not None:
            conn.execute(
                "UPDATE subtasks SET title = ? WHERE id = ?", (title, subtask_id)
            )
        if done is not None:
            conn.execute(
                "UPDATE subtasks SET done = ? WHERE id = ?",
                (1 if done else 0, subtask_id),
            )
            if not done and _active_row(conn, task_id)["status"] == DONE_STATUS:
                _apply_move(conn, task_id, DONE_STATUS, REOPEN_STATUS, None)
    return get_task(task_id)


def delete_subtask(subtask_id: int) -> Optional[dict]:
    with connection() as conn:
        row = conn.execute(
            "SELECT task_id FROM subtasks WHERE id = ?", (subtask_id,)
        ).fetchone()
        if row is None or _active_row(conn, row["task_id"]) is None:
            return None
        task_id = row["task_id"]
        conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    return get_task(task_id)


def create_attachment(
    task_id: int,
    filename: str,
    stored_name: str,
    content_type: str,
    size_bytes: int,
) -> Optional[dict]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        total = conn.execute(
            "SELECT COUNT(*) AS total FROM attachments WHERE task_id = ?",
            (task_id,),
        ).fetchone()["total"]
        if total >= MAX_ATTACHMENTS_PER_TASK:
            raise AttachmentLimitError(MAX_ATTACHMENTS_PER_TASK)
        conn.execute(
            "INSERT INTO attachments (task_id, filename, stored_name, "
            "content_type, size_bytes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, filename, stored_name, content_type, size_bytes, _now_iso()),
        )
    return get_task(task_id)


def get_attachment(task_id: int, attachment_id: int) -> Optional[dict]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        row = conn.execute(
            "SELECT * FROM attachments WHERE id = ? AND task_id = ?",
            (attachment_id, task_id),
        ).fetchone()
        return dict(row) if row is not None else None


def delete_attachment(task_id: int, attachment_id: int) -> Optional[tuple]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        row = conn.execute(
            "SELECT stored_name FROM attachments WHERE id = ? AND task_id = ?",
            (attachment_id, task_id),
        ).fetchone()
        if row is None:
            return None
        conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        stored_name = row["stored_name"]
    return get_task(task_id), stored_name
