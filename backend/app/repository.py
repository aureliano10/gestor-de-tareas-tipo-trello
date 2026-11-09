from datetime import date, datetime, timezone
from typing import Optional

from .database import connection
from .schemas import (
    DEFAULT_PRIORITY,
    DUPLICATE_LINK_MESSAGE,
    MAX_ATTACHMENTS_PER_TASK,
    MAX_LINKS_PER_TASK,
    MAX_SUBTASKS_PER_TASK,
    MAX_TAGS_PER_TASK,
    TOO_MANY_LINKS_MESSAGE,
    TOO_MANY_SUBTASKS_MESSAGE,
    TOO_MANY_TAGS_MESSAGE,
)

DEFAULT_STATUS = "Pendiente"
DONE_STATUS = "Terminada"
REOPEN_STATUS = "En curso"

STATUS_ORDER = {DEFAULT_STATUS: 0, REOPEN_STATUS: 1, DONE_STATUS: 2}
PRIORITY_ORDER = {"Alta": 0, "Media": 1, "Baja": 2}


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


class TagLimitError(DomainError):
    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(TOO_MANY_TAGS_MESSAGE)


class LinkLimitError(DomainError):
    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(TOO_MANY_LINKS_MESSAGE)


class SubtaskLimitError(DomainError):
    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(TOO_MANY_SUBTASKS_MESSAGE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_iso() -> str:
    return date.today().isoformat()


def is_overdue(
    due_date: Optional[str], status: str, today: Optional[str] = None
) -> bool:
    """Indica si una tarea está vencida.

    Una tarea está vencida cuando tiene fecha límite anterior a hoy y su
    estado no es "Terminada". El parámetro ``today`` permite inyectar la
    fecha de referencia (formato ISO) para comprobar la regla de forma
    aislada, sin depender del reloj del sistema.
    """
    if not due_date or status == DONE_STATUS:
        return False
    return due_date < (today or _today_iso())


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


def _log_activity(conn, task_id: int, action: str, detail: str = "") -> None:
    conn.execute(
        "INSERT INTO activity (task_id, action, detail, created_at) "
        "VALUES (?, ?, ?, ?)",
        (task_id, action, detail, _now_iso()),
    )


def _log_set_changes(
    conn,
    task_id: int,
    old_items: list[tuple[str, str]],
    new_items: list[tuple[str, str]],
    removed_message: str,
    added_message: str,
) -> None:
    """Registra las bajas y altas de un conjunto comparando por clave.

    ``old_items`` y ``new_items`` son listas de pares ``(clave, texto)``.
    ``removed_message`` y ``added_message`` son plantillas que reciben el
    texto visible de cada elemento (por ejemplo ``"Etiqueta agregada: {}"``).
    """
    new_keys = {key for key, _ in new_items}
    old_keys = {key for key, _ in old_items}
    for key, display in old_items:
        if key not in new_keys:
            _log_activity(conn, task_id, removed_message.format(display))
    for key, display in new_items:
        if key not in old_keys:
            _log_activity(conn, task_id, added_message.format(display))


def _tags_of(conn, task_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT tags.name AS name FROM tags "
        "JOIN task_tags ON task_tags.tag_id = tags.id "
        "WHERE task_tags.task_id = ? ORDER BY tags.name ASC",
        (task_id,),
    ).fetchall()
    return [row["name"] for row in rows]


def _links_of(conn, task_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM links WHERE task_id = ? ORDER BY id ASC", (task_id,)
    ).fetchall()
    return [
        {
            "id": row["id"],
            "url": row["url"],
            "label": row["label"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def _activity_of(conn, task_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM activity WHERE task_id = ? ORDER BY id DESC LIMIT 20",
        (task_id,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "action": row["action"],
            "detail": row["detail"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def _resolve_tag_id(conn, name: str) -> int:
    row = conn.execute(
        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()
    if row is not None:
        return row["id"]
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    return cursor.lastrowid


def _set_tags(conn, task_id: int, names: list[str]) -> None:
    names = names or []
    if len(names) > MAX_TAGS_PER_TASK:
        raise TagLimitError(MAX_TAGS_PER_TASK)
    tag_ids = [_resolve_tag_id(conn, name) for name in names]
    conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
    for tag_id in tag_ids:
        conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (task_id, tag_id),
        )


def _normalize_links(links) -> list[tuple[str, str]]:
    """Valida los enlaces recibidos y devuelve pares (url, label)."""
    links = links or []
    if len(links) > MAX_LINKS_PER_TASK:
        raise LinkLimitError(MAX_LINKS_PER_TASK)
    normalized: list[tuple[str, str]] = []
    seen: set[str] = set()
    for link in links:
        if isinstance(link, dict):
            url = link.get("url", "")
            label = link.get("label", "") or ""
        else:
            url = link.url
            label = link.label or ""
        key = url.lower()
        if key in seen:
            raise ValueError(DUPLICATE_LINK_MESSAGE)
        seen.add(key)
        normalized.append((url, label))
    return normalized


def _set_links(conn, task_id: int, pairs: list[tuple[str, str]]) -> None:
    conn.execute("DELETE FROM links WHERE task_id = ?", (task_id,))
    for url, label in pairs:
        conn.execute(
            "INSERT INTO links (task_id, url, label, created_at) VALUES (?, ?, ?, ?)",
            (task_id, url, label, _now_iso()),
        )


def _row_to_dict(row) -> dict:
    """Convierte una fila en dict sin depender del tipo de driver."""
    return {key: row[key] for key in row.keys()}


def _task_dict(conn, row) -> dict:
    subtasks = _subtasks_of(conn, row["id"])
    due_date = row["due_date"]
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "assignee": row["assignee"],
        "due_date": due_date,
        "position": row["position"],
        "created_at": row["created_at"],
        "overdue": is_overdue(due_date, row["status"]),
        "subtask_total": len(subtasks),
        "subtask_done": sum(1 for item in subtasks if item["done"]),
        "subtasks": subtasks,
        "attachments": _attachments_of(conn, row["id"]),
        "tags": _tags_of(conn, row["id"]),
        "links": _links_of(conn, row["id"]),
        "activity": _activity_of(conn, row["id"]),
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


def _annotate_subtask_title(subtask) -> str:
    if isinstance(subtask, dict):
        return subtask["title"]
    return subtask.title


def create_task(
    title: str,
    description: str = "",
    due_date: Optional[date] = None,
    priority: str = DEFAULT_PRIORITY,
    assignee: str = "",
    subtasks=None,
    tags=None,
    links=None,
) -> dict:
    subtasks = subtasks or []
    tags = tags or []
    links = links or []
    if len(subtasks) > MAX_SUBTASKS_PER_TASK:
        raise SubtaskLimitError(MAX_SUBTASKS_PER_TASK)
    if len(tags) > MAX_TAGS_PER_TASK:
        raise TagLimitError(MAX_TAGS_PER_TASK)
    normalized_links = _normalize_links(links)
    with connection() as conn:
        position = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks WHERE status = ? "
            "AND deleted_at IS NULL",
            (DEFAULT_STATUS,),
        ).fetchone()["total"]
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, status, priority, assignee, "
            "due_date, position, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                title,
                description,
                DEFAULT_STATUS,
                priority,
                assignee,
                _as_iso(due_date),
                position,
                _now_iso(),
            ),
        )
        task_id = cursor.lastrowid
        _log_activity(conn, task_id, "Tarea creada")
        for subtask in subtasks:
            sub_title = _annotate_subtask_title(subtask)
            conn.execute(
                "INSERT INTO subtasks (task_id, title, done, created_at) "
                "VALUES (?, ?, 0, ?)",
                (task_id, sub_title, _now_iso()),
            )
            _log_activity(conn, task_id, f"Subtarea agregada: {sub_title}")
        _set_tags(conn, task_id, tags)
        for name in tags:
            _log_activity(conn, task_id, f"Etiqueta agregada: {name}")
        _set_links(conn, task_id, normalized_links)
        for url, label in normalized_links:
            _log_activity(conn, task_id, f"Enlace agregado: {label or url}")
    return get_task(task_id)


def _group_by_status(tasks: list[dict]) -> list[list[dict]]:
    groups: dict[int, list[dict]] = {}
    for task in tasks:
        groups.setdefault(STATUS_ORDER.get(task["status"], 3), []).append(task)
    return [groups[key] for key in sorted(groups)]


def _sort_tasks(tasks: list[dict], sort: str) -> list[dict]:
    """Ordena manteniendo el agrupamiento por estado como criterio primario."""
    ordered: list[dict] = []
    for group in _group_by_status(tasks):
        if sort == "priority":
            group = sorted(
                group,
                key=lambda task: (
                    PRIORITY_ORDER.get(task["priority"], 3),
                    task["position"],
                    task["id"],
                ),
            )
        elif sort == "due":
            group = sorted(
                group,
                key=lambda task: (
                    task["due_date"] is None,
                    task["due_date"] or "",
                    task["id"],
                ),
            )
        elif sort == "created":
            group = sorted(group, key=lambda task: task["created_at"], reverse=True)
        else:
            group = sorted(group, key=lambda task: (task["position"], task["id"]))
        ordered.extend(group)
    return ordered


def list_tasks(
    overdue_only: bool = False,
    query: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = "position",
) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY "
            "CASE status WHEN 'Pendiente' THEN 0 WHEN 'En curso' THEN 1 ELSE 2 END, "
            "position ASC, id ASC"
        ).fetchall()
        tasks = [_task_dict(conn, row) for row in rows]
    if query:
        needle = query.strip().lower()
        tasks = [
            task
            for task in tasks
            if needle in task["title"].lower()
            or needle in (task["description"] or "").lower()
        ]
    if priority:
        tasks = [task for task in tasks if task["priority"] == priority]
    if tag:
        wanted = tag.strip().lower()
        tasks = [
            task
            for task in tasks
            if any(name.lower() == wanted for name in task["tags"])
        ]
    if overdue_only:
        tasks = [task for task in tasks if task["overdue"]]
    return _sort_tasks(tasks, sort)


def get_task(task_id: int) -> Optional[dict]:
    with connection() as conn:
        row = _active_row(conn, task_id)
        return _task_dict(conn, row) if row is not None else None


def update_task(
    task_id: int,
    title: str,
    description: str = "",
    due_date: Optional[date] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: Optional[list] = None,
    links: Optional[list] = None,
) -> Optional[dict]:
    with connection() as conn:
        row = _active_row(conn, task_id)
        if row is None:
            return None
        normalized_links = _normalize_links(links) if links is not None else None
        if title != row["title"]:
            _log_activity(conn, task_id, "Título actualizado")
        if description != row["description"]:
            _log_activity(conn, task_id, "Descripción actualizada")
        if _as_iso(due_date) != row["due_date"]:
            _log_activity(conn, task_id, "Fecha límite actualizada")
        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, due_date = ? WHERE id = ?",
            (title, description, _as_iso(due_date), task_id),
        )
        if priority is not None and priority != row["priority"]:
            conn.execute(
                "UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id)
            )
            _log_activity(conn, task_id, f"Prioridad cambiada a {priority}")
        if assignee is not None and assignee != row["assignee"]:
            conn.execute(
                "UPDATE tasks SET assignee = ? WHERE id = ?", (assignee, task_id)
            )
            if assignee:
                _log_activity(conn, task_id, f"Responsable asignado a {assignee}")
            else:
                _log_activity(conn, task_id, "Responsable quitado")
        if tags is not None:
            current_tags = _tags_of(conn, task_id)
            _set_tags(conn, task_id, tags)
            _log_set_changes(
                conn,
                task_id,
                [(name.lower(), name) for name in current_tags],
                [(name.lower(), name) for name in tags],
                "Etiqueta eliminada: {}",
                "Etiqueta agregada: {}",
            )
        if normalized_links is not None:
            current_links = _links_of(conn, task_id)
            _set_links(conn, task_id, normalized_links)
            _log_set_changes(
                conn,
                task_id,
                [
                    (link["url"].lower(), link["label"] or link["url"])
                    for link in current_links
                ],
                [(url.lower(), label or url) for url, label in normalized_links],
                "Enlace eliminado: {}",
                "Enlace agregado: {}",
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
        if status == row["status"]:
            _log_activity(conn, task_id, f"Reordenada en {status}")
        else:
            _log_activity(conn, task_id, f"Movida a {status}")
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
        _log_activity(conn, task_id, "Tarea eliminada")
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
        _log_activity(conn, task_id, "Tarea restaurada")
    return get_task(task_id)


def create_subtask(task_id: int, title: str, done: bool = False) -> Optional[dict]:
    with connection() as conn:
        row = _active_row(conn, task_id)
        if row is None:
            return None
        total = conn.execute(
            "SELECT COUNT(*) AS total FROM subtasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()["total"]
        if total >= MAX_SUBTASKS_PER_TASK:
            raise SubtaskLimitError(MAX_SUBTASKS_PER_TASK)
        conn.execute(
            "INSERT INTO subtasks (task_id, title, done, created_at) "
            "VALUES (?, ?, ?, ?)",
            (task_id, title, 1 if done else 0, _now_iso()),
        )
        _log_activity(conn, task_id, f"Subtarea agregada: {title}")
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
        current_title = row["title"]
        if title is not None:
            conn.execute(
                "UPDATE subtasks SET title = ? WHERE id = ?", (title, subtask_id)
            )
            _log_activity(conn, task_id, "Subtarea renombrada")
            current_title = title
        if done is not None:
            conn.execute(
                "UPDATE subtasks SET done = ? WHERE id = ?",
                (1 if done else 0, subtask_id),
            )
            if done:
                _log_activity(conn, task_id, f"Subtarea completada: {current_title}")
            else:
                _log_activity(conn, task_id, f"Subtarea reabierta: {current_title}")
            if not done and _active_row(conn, task_id)["status"] == DONE_STATUS:
                _apply_move(conn, task_id, DONE_STATUS, REOPEN_STATUS, None)
    return get_task(task_id)


def delete_subtask(subtask_id: int) -> Optional[dict]:
    with connection() as conn:
        row = conn.execute(
            "SELECT task_id, title FROM subtasks WHERE id = ?", (subtask_id,)
        ).fetchone()
        if row is None or _active_row(conn, row["task_id"]) is None:
            return None
        task_id = row["task_id"]
        conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
        _log_activity(conn, task_id, f"Subtarea eliminada: {row['title']}")
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
        _log_activity(conn, task_id, f"Adjunto agregado: {filename}")
    return get_task(task_id)


def get_attachment(task_id: int, attachment_id: int) -> Optional[dict]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        row = conn.execute(
            "SELECT * FROM attachments WHERE id = ? AND task_id = ?",
            (attachment_id, task_id),
        ).fetchone()
        return _row_to_dict(row) if row is not None else None


def delete_attachment(task_id: int, attachment_id: int) -> Optional[tuple]:
    with connection() as conn:
        if _active_row(conn, task_id) is None:
            return None
        row = conn.execute(
            "SELECT stored_name, filename FROM attachments "
            "WHERE id = ? AND task_id = ?",
            (attachment_id, task_id),
        ).fetchone()
        if row is None:
            return None
        conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        _log_activity(conn, task_id, f"Adjunto eliminado: {row['filename']}")
        stored_name = row["stored_name"]
    return get_task(task_id), stored_name


def list_tag_names() -> list[str]:
    """Todas las etiquetas existentes, ordenadas alfabéticamente."""
    with connection() as conn:
        rows = conn.execute("SELECT name FROM tags ORDER BY name ASC").fetchall()
        return [row["name"] for row in rows]
