from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "evidencias" / "etapa_6"
BASE_URL = "http://127.0.0.1:8000"
SERVER_DB_PATH = Path(os.environ.get("KANBAN_SERVER_DB", "/tmp/kanban_etapa6.db"))
SERVER_STORAGE_PATH = Path(
    os.environ.get("KANBAN_SERVER_STORAGE", "/tmp/kanban_etapa6_storage")
)
TIMEOUT = 60.0


def api(
    method: str,
    path: str,
    json_body: dict | None = None,
    files: dict | None = None,
) -> httpx.Response:
    with httpx.Client(base_url=BASE_URL, timeout=TIMEOUT) as client:
        return client.request(method, path, json=json_body, files=files)


def reset_server_db() -> None:
    """Deja la base del servidor sin tareas, subtareas, adjuntos ni archivos."""
    if not SERVER_DB_PATH.exists():
        raise FileNotFoundError(
            f"No existe la base del servidor: {SERVER_DB_PATH}. "
            "Iniciá el backend antes de ejecutar los casos."
        )
    with sqlite3.connect(SERVER_DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM attachments")
        conn.execute("DELETE FROM subtasks")
        conn.execute("DELETE FROM tasks")
        conn.commit()
    if SERVER_STORAGE_PATH.exists():
        for item in SERVER_STORAGE_PATH.iterdir():
            if item.is_file():
                item.unlink()


def list_tasks() -> list[dict]:
    response = api("GET", "/api/tasks")
    response.raise_for_status()
    return response.json()


def create_task(title: str, description: str = "", due_date: str | None = None) -> dict:
    payload: dict[str, Any] = {"title": title, "description": description}
    if due_date is not None:
        payload["due_date"] = due_date
    response = api("POST", "/api/tasks", payload)
    response.raise_for_status()
    return response.json()


def upload(
    task_id: int, filename: str, content: bytes, content_type: str = "text/plain"
) -> httpx.Response:
    return api(
        "POST",
        f"/api/tasks/{task_id}/attachments",
        files={"file": (filename, content, content_type)},
    )


def date_offset(days: int) -> str:
    """Fecha en formato ISO desplazada respecto de hoy."""
    return (date.today() + timedelta(days=days)).isoformat()


def error_detail(body: Any) -> str:
    """Extrae el mensaje legible de una respuesta de error de FastAPI."""
    if not isinstance(body, dict):
        return ""
    detail = body.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail and isinstance(detail[0], dict):
        return detail[0].get("msg", "")
    return ""


def json_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:  # noqa: BLE001
        return response.text


def make_result(
    case_id: str,
    checks: dict[str, bool],
    obtained: str,
    observations: str,
    detail: Any = None,
) -> dict:
    passed = all(checks.values())
    failed_checks = [name for name, ok in checks.items() if not ok]
    observation_text = observations
    if failed_checks:
        observation_text = (
            f"{observations} Verificaciones fallidas: {', '.join(failed_checks)}."
        )
    return {
        "id": case_id,
        "passed": passed,
        "resultado_obtenido": obtained,
        "observaciones": observation_text,
        "detalle": detail,
    }


def save_json(filename: str, data: Any) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def short(value: Any, limit: int = 400) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else f"{text[:limit]}..."


def ensure_server() -> None:
    try:
        response = api("GET", "/api/health")
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"No se pudo contactar la API en {BASE_URL}: {exc}") from exc
