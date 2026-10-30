from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "evidencias" / "etapa_6"
BASE_URL = "http://127.0.0.1:8000"
SERVER_DB_PATH = Path(os.environ.get("KANBAN_SERVER_DB", "/tmp/kanban_etapa6.db"))

FORBIDDEN_TASK_KEYS = {"id", "title", "status", "created_at"}


def api(method: str, path: str, json_body: dict | None = None) -> httpx.Response:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        return client.request(method, path, json=json_body)


def reset_server_db() -> None:
    if not SERVER_DB_PATH.exists():
        raise FileNotFoundError(
            f"No existe la base del servidor: {SERVER_DB_PATH}. "
            "Iniciá el backend antes de ejecutar los casos."
        )
    with sqlite3.connect(SERVER_DB_PATH) as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()


def create_task(title: str) -> dict:
    response = api("POST", "/api/tasks", {"title": title})
    response.raise_for_status()
    return response.json()


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
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def short(value: Any, limit: int = 400) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else f"{text[:limit]}..."


def ensure_server() -> None:
    try:
        response = api("GET", "/api/health")
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"No se pudo contactar la API en {BASE_URL}: {exc}"
        ) from exc
