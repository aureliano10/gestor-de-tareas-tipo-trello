import logging
import uuid
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from .. import repository, schemas, storage
from ..schemas import ALLOWED_ATTACHMENT_EXTENSIONS, MAX_ATTACHMENT_SIZE

router = APIRouter(prefix="/api/tasks", tags=["attachments"])
logger = logging.getLogger(__name__)

TASK_NOT_FOUND = "Tarea no encontrada"
ATTACHMENT_NOT_FOUND = "Archivo adjunto no encontrado"
ATTACHMENT_SAVE_ERROR = "No se pudo guardar el archivo adjunto"


def _content_disposition(filename: str) -> str:
    ascii_name = filename.encode("ascii", "ignore").decode("ascii") or "archivo"
    ascii_name = ascii_name.replace('"', "")
    return (
        f'attachment; filename="{ascii_name}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )


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
    content_type = file.content_type or "application/octet-stream"

    try:
        await storage.save_attachment(task_id, stored_name, content, content_type)
    except Exception as exc:
        logger.exception("No se pudo guardar el adjunto en el storage")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ATTACHMENT_SAVE_ERROR,
        ) from exc

    try:
        task = await run_in_threadpool(
            repository.create_attachment,
            task_id,
            filename,
            stored_name,
            content_type,
            len(content),
        )
    except repository.AttachmentLimitError as exc:
        await storage.delete_attachment(task_id, stored_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except Exception:
        await storage.delete_attachment(task_id, stored_name)
        raise

    if task is None:
        await storage.delete_attachment(task_id, stored_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
        )
    return task


@router.get("/{task_id}/attachments/{attachment_id}")
async def download_attachment(task_id: int, attachment_id: int):
    attachment = await run_in_threadpool(
        repository.get_attachment, task_id, attachment_id
    )
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )

    if storage.using_blob():
        from vercel import blob

        stack = AsyncExitStack()
        try:
            download = await stack.enter_async_context(
                blob.stream_blob(
                    storage.blob_pathname(task_id, attachment["stored_name"]),
                    access="private",
                )
            )
        except Exception as exc:
            await stack.aclose()
            logger.exception("No se pudo descargar el adjunto desde Blob")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ATTACHMENT_NOT_FOUND,
            ) from exc

        return StreamingResponse(
            download,
            media_type=download.metadata.content_type
            or attachment["content_type"],
            headers={
                "Content-Disposition": _content_disposition(attachment["filename"])
            },
            background=BackgroundTask(stack.aclose),
        )

    path = storage.local_path(attachment["stored_name"])
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
async def delete_attachment(task_id: int, attachment_id: int):
    result = await run_in_threadpool(
        repository.delete_attachment, task_id, attachment_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )

    _, stored_name = result
    try:
        await storage.delete_attachment(task_id, stored_name)
    except Exception:
        logger.exception("No se pudo borrar el adjunto del storage")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
