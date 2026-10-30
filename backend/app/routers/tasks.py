from fastapi import APIRouter, HTTPException, Response, status

from .. import repository, schemas

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks():
    return repository.list_tasks()


@router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate):
    return repository.create_task(payload.title)


@router.patch("/{task_id}/status", response_model=schemas.TaskOut)
def update_task_status(task_id: int, payload: schemas.TaskStatusUpdate):
    task = repository.update_task_status(task_id, payload.status)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if not repository.delete_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
