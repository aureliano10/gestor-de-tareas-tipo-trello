import logging
import uuid
from contextlib import AsyncExitStack
from io import BytesIO
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from .. import repository, schemas, storage
from ..schemas import (
    ALLOWED_ATTACHMENT_EXTENSIONS,
    MAX_ATTACHMENT_MB,
    MAX_ATTACHMENT_SIZE,
)

router = APIRouter(prefix="/api/tasks", tags=["attachments"])
logger = logging.getLogger(__name__)

TASK_NOT_FOUND = "Tarea no encontrada"
ATTACHMENT_NOT_FOUND = "Archivo adjunto no encontrado"
ATTACHMENT_SAVE_ERROR = "No se pudo guardar el archivo adjunto"
IMAGE_PROCESS_ERROR = "No se pudo procesar la imagen. Probá con otro archivo."
TOO_LARGE_DETAIL = f"El archivo supera el tamaño máximo de {MAX_ATTACHMENT_MB} MB"

# Las imágenes se guardan en WebP para reducir el peso del adjunto.
WEBP_EXTENSIONS = (".png", ".jpg", ".jpeg")
WEBP_CONTENT_TYPE = "image/webp"


def _content_disposition(filename: str, *, inline: bool) -> str:
    disposition = "inline" if inline else "attachment"
    ascii_name = filename.encode("ascii", "ignore").decode("ascii") or "archivo"
    ascii_name = ascii_name.replace('"', "")
    return (
        f'{disposition}; filename="{ascii_name}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )


def _convert_image_to_webp(content: bytes) -> bytes:
    """Reencoda una imagen a WebP conservando la transparencia si la hay."""
    from PIL import Image

    with Image.open(BytesIO(content)) as image:
        image.load()
        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        ):
            converted = image.convert("RGBA")
        else:
            converted = image.convert("RGB")
        buffer = BytesIO()
        converted.save(buffer, format="WEBP", quality=85)
        return buffer.getvalue()


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
            detail=TOO_LARGE_DETAIL,
        )

    stored_extension = extension
    content_type = file.content_type or "application/octet-stream"

    # Las imágenes se reencodan a WebP antes de guardarlas.
    if extension in WEBP_EXTENSIONS:
        try:
            content = await run_in_threadpool(_convert_image_to_webp, content)
        except Exception as exc:
            logger.exception("No se pudo convertir la imagen a WebP")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=IMAGE_PROCESS_ERROR,
            ) from exc
        content_type = WEBP_CONTENT_TYPE
        stored_extension = ".webp"

    stored_name = f"{uuid.uuid4().hex}{stored_extension}"

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
async def download_attachment(task_id: int, attachment_id: int, download: bool = False):
    attachment = await run_in_threadpool(
        repository.get_attachment, task_id, attachment_id
    )
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND
        )

    # Por defecto se sirve inline para permitir la vista previa en el navegador;
    # con ``?download=1`` se fuerza la descarga.
    inline = not download
    disposition = _content_disposition(attachment["filename"], inline=inline)

    if storage.using_blob():
        from vercel import blob

        stack = AsyncExitStack()
        try:
            download_blob = await stack.enter_async_context(
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
            download_blob,
            media_type=download_blob.metadata.content_type
            or attachment["content_type"],
            headers={"Content-Disposition": disposition},
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
        headers={"Content-Disposition": disposition},
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
