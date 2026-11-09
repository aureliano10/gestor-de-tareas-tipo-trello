import os
from pathlib import Path

from .database import get_storage_path


def using_blob() -> bool:
    """Indica si los adjuntos se guardan en Vercel Blob o en disco local."""
    mode = os.environ.get("KANBAN_STORAGE", "").strip().lower()
    if mode == "local":
        return False
    if mode == "blob":
        return True
    return bool(
        os.environ.get("BLOB_READ_WRITE_TOKEN")
        or os.environ.get("VERCEL_BLOB_READ_WRITE_TOKEN")
        or (os.environ.get("BLOB_STORE_ID") and os.environ.get("VERCEL"))
    )


def blob_pathname(task_id: int, stored_name: str) -> str:
    return f"tasks/{task_id}/{stored_name}"


def local_path(stored_name: str) -> Path:
    return get_storage_path() / stored_name


def ensure_storage_ready() -> None:
    if not using_blob():
        get_storage_path().mkdir(parents=True, exist_ok=True)


async def save_attachment(
    task_id: int,
    stored_name: str,
    content: bytes,
    content_type: str,
) -> None:
    if using_blob():
        from vercel import blob

        await blob.put_blob(
            blob_pathname(task_id, stored_name),
            content,
            access="private",
            content_type=content_type,
            add_random_suffix=False,
            allow_overwrite=False,
        )
        return

    ensure_storage_ready()
    local_path(stored_name).write_bytes(content)


async def delete_attachment(task_id: int, stored_name: str) -> None:
    if using_blob():
        from vercel import blob

        try:
            await blob.delete_blob(blob_pathname(task_id, stored_name))
        except Exception as exc:
            if "not found" not in str(exc).lower():
                raise
        return

    local_path(stored_name).unlink(missing_ok=True)
