import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse

from .. import repository, schemas
from ..database import get_storage_path
from ..schemas import ALLOWED_ATTACHMENT_EXTENSIONS, MAX_ATTACHMENT_SIZE

router = APIRouter(prefix="/api/tasks", tags=["attachments"])

TASK_NOT_FOUND = "Tarea no encontrada"
ATTACHMENT_NOT_FOUND = "Archivo adjunto no encontrado"


@router.post(
    "/{task_id}/attachments",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(task_id: int, file: Annotated[UploadFile, File()]):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no permitido. Se aceptan: "
            + ", ".join(ALLOWED_ATTACHMENT_EXTENSIONS),
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El archivo está vacío",
        )
    if len(content) > MAX_ATTACHMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="El archivo supera el tamaño máximo de 4 MB",
        )

    stored_name = f"{uuid.uuid4().hex}{extension}"
    destination = get_storage_path() / stored_name
    destination.write_bytes(content)

    try:
        task = repository.create_attachment(
            task_id,
            filename,
            stored_name,
            file.content_type or "application/octet-stream",
            len(content),
        )
    except repository.AttachmentLimitError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    if task is None:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
        )
    return task


@router.get("/{task_id}/attachments/{attachment_id}")
def download_attachment(task_id: int, attachment_id: int):
    attachment = repository.get_attachment(task_id, attachment_id)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )
    path = get_storage_path() / attachment["stored_name"]
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )
    return FileResponse(
        path,
        media_type=attachment["content_type"],
        filename=attachment["filename"],
    )


@router.delete(
    "/{task_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attachment(task_id: int, attachment_id: int):
    result = repository.delete_attachment(task_id, attachment_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )
    _, stored_name = result
    (get_storage_path() / stored_name).unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
