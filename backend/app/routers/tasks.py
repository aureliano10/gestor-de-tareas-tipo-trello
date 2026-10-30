from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response, status

from .. import repository, schemas

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

TASK_NOT_FOUND = "Tarea no encontrada"

TaskSort = Literal["position", "priority", "due", "created"]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND)


def _pending_message(pending: int) -> str:
    if pending == 1:
        return "No se puede finalizar: la tarea tiene 1 subtarea pendiente"
    return f"No se puede finalizar: la tarea tiene {pending} subtareas pendientes"


def _conflict(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    overdue: bool = Query(False, description="Devuelve solo tareas vencidas"),
    q: str | None = Query(None, description="Filtra por texto en título o descripción"),
    priority: str | None = Query(None, description="Filtra por prioridad exacta"),
    tag: str | None = Query(None, description="Filtra por nombre de etiqueta"),
    sort: TaskSort = "position",
):
    return repository.list_tasks(
        overdue_only=overdue,
        query=q,
        priority=priority,
        tag=tag,
        sort=sort,
    )


@router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate):
    try:
        return repository.create_task(
            payload.title,
            payload.description,
            payload.due_date,
            payload.priority,
            payload.assignee,
            payload.subtasks,
            payload.tags,
            payload.links,
        )
    except (
        repository.TagLimitError,
        repository.SubtaskLimitError,
        repository.LinkLimitError,
    ) as exc:
        raise _conflict(exc) from exc
    except ValueError as exc:
        raise _conflict(exc) from exc


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate):
    try:
        task = repository.update_task(
            task_id,
            payload.title,
            payload.description,
            payload.due_date,
            payload.priority,
            payload.assignee,
            payload.tags,
            payload.links,
        )
    except (
        repository.TagLimitError,
        repository.SubtaskLimitError,
        repository.LinkLimitError,
    ) as exc:
        raise _conflict(exc) from exc
    except ValueError as exc:
        raise _conflict(exc) from exc
    if task is None:
        raise _not_found()
    return task


@router.patch("/{task_id}/move", response_model=schemas.TaskOut)
def move_task(task_id: int, payload: schemas.TaskMove):
    try:
        task = repository.move_task(task_id, payload.status, payload.position)
    except repository.PendingSubtasksError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_pending_message(exc.pending),
        ) from exc
    if task is None:
        raise _not_found()
    return task


@router.post("/{task_id}/restore", response_model=schemas.TaskOut)
def restore_task(task_id: int):
    task = repository.restore_task(task_id)
    if task is None:
        raise _not_found()
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if not repository.delete_task(task_id):
        raise _not_found()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
