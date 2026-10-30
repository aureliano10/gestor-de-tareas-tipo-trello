from fastapi import APIRouter, HTTPException, Response, status

from .. import repository, schemas

router = APIRouter(prefix="/api", tags=["subtasks"])

SUBTASK_NOT_FOUND = "Subtarea no encontrada"
TASK_NOT_FOUND = "Tarea no encontrada"


@router.post(
    "/tasks/{task_id}/subtasks",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_subtask(task_id: int, payload: schemas.SubtaskCreate):
    task = repository.create_subtask(task_id, payload.title, payload.done)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
        )
    return task


@router.patch("/subtasks/{subtask_id}", response_model=schemas.TaskOut)
def update_subtask(subtask_id: int, payload: schemas.SubtaskUpdate):
    task = repository.update_subtask(subtask_id, payload.title, payload.done)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=SUBTASK_NOT_FOUND
        )
    return task


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask(subtask_id: int):
    if repository.delete_subtask(subtask_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=SUBTASK_NOT_FOUND
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
