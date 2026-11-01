"""Pruebas de integración del flujo de tareas enriquecidas.

Ejercitan de punta a punta la interacción entre los routers HTTP, los
schemas de validación, el repositorio y la base SQLite, usando el
``TestClient`` de FastAPI sobre una base temporal.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("KANBAN_DB_PATH", str(tmp_path / "tasks.db"))
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def storage_path(tmp_path):
    return tmp_path / "storage"


def test_cp_in_01_alta_enriquecida_y_persistencia(client):
    payload = {
        "title": "  Lanzamiento 1.0  ",
        "description": "Cierre de versión",
        "priority": "Alta",
        "assignee": "Ana",
        "tags": ["bug", "Bug", "release"],
        "subtasks": [{"title": "Deploy"}, "Documentar"],
        "links": [{"url": "https://docs.example.com", "label": "Docs"}],
    }

    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Lanzamiento 1.0"
    assert created["priority"] == "Alta"
    assert created["assignee"] == "Ana"
    assert created["status"] == "Pendiente"
    assert [item["title"] for item in created["subtasks"]] == [
        "Deploy",
        "Documentar",
    ]
    assert created["subtask_total"] == 2
    assert created["tags"] == ["bug", "release"]
    assert created["links"][0]["label"] == "Docs"

    listed = client.get("/api/tasks").json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]
    assert listed[0]["subtask_total"] == 2
    assert client.get("/api/tags").json() == ["bug", "release"]


def test_cp_in_02_adjunto_persistencia_y_descarga(client, storage_path):
    task = client.post("/api/tasks", json={"title": "Con adjunto"}).json()
    content = b"reporte de pruebas"

    upload = client.post(
        f"/api/tasks/{task['id']}/attachments",
        files={"file": ("notas.txt", content, "text/plain")},
    )
    assert upload.status_code == 201
    attachment = upload.json()["attachments"][0]
    assert attachment["filename"] == "notas.txt"
    assert attachment["size_bytes"] == len(content)

    stored = list(storage_path.iterdir())
    assert len(stored) == 1

    download = client.get(
        f"/api/tasks/{task['id']}/attachments/{attachment['id']}"
    )
    assert download.status_code == 200
    assert download.content == content
    assert "notas.txt" in download.headers["content-disposition"]

    listed = client.get("/api/tasks").json()
    assert listed[0]["attachments"][0]["id"] == attachment["id"]


def test_cp_in_03_flujo_de_estados_con_regla_de_negocio(client):
    task = client.post("/api/tasks", json={"title": "Flujo"}).json()
    task_id = task["id"]
    subtask = client.post(
        f"/api/tasks/{task_id}/subtasks", json={"title": "Paso 1"}
    ).json()
    subtask_id = subtask["subtasks"][0]["id"]

    moving = client.patch(
        f"/api/tasks/{task_id}/move", json={"status": "En curso"}
    )
    assert moving.status_code == 200
    assert moving.json()["status"] == "En curso"

    blocked = client.patch(
        f"/api/tasks/{task_id}/move", json={"status": "Terminada"}
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"] == (
        "No se puede finalizar: la tarea tiene 1 subtarea pendiente"
    )
    assert client.get("/api/tasks").json()[0]["status"] == "En curso"

    done = client.patch(f"/api/subtasks/{subtask_id}", json={"done": True})
    assert done.status_code == 200
    assert done.json()["subtask_done"] == 1

    finished = client.patch(
        f"/api/tasks/{task_id}/move", json={"status": "Terminada"}
    )
    assert finished.status_code == 200
    assert finished.json()["status"] == "Terminada"


def test_cp_in_04_reapertura_automatica_al_agregar_pendiente(client):
    task = client.post("/api/tasks", json={"title": "Terminada"}).json()
    task_id = task["id"]

    closed = client.patch(
        f"/api/tasks/{task_id}/move", json={"status": "Terminada"}
    )
    assert closed.status_code == 200
    assert client.get("/api/tasks").json()[0]["status"] == "Terminada"

    reopened = client.post(
        f"/api/tasks/{task_id}/subtasks", json={"title": "Nueva"}
    )
    assert reopened.status_code == 201
    assert reopened.json()["status"] == "En curso"
    assert client.get("/api/tasks").json()[0]["status"] == "En curso"


def test_cp_in_05_lectura_con_filtros_y_orden(client):
    alta = client.post(
        "/api/tasks",
        json={"title": "Alfa alta", "priority": "Alta", "tags": ["backend"]},
    ).json()
    media = client.post(
        "/api/tasks",
        json={"title": "Beta media", "description": "revisar despliegue"},
    ).json()
    baja = client.post(
        "/api/tasks", json={"title": "Gamma baja", "priority": "Baja"}
    ).json()

    updated = client.put(
        f"/api/tasks/{baja['id']}",
        json={"title": "Gamma baja", "due_date": "2020-01-01"},
    )
    assert updated.status_code == 200
    assert updated.json()["overdue"] is True

    by_priority = client.get("/api/tasks", params={"sort": "priority"}).json()
    assert [task["title"] for task in by_priority] == [
        "Alfa alta",
        "Beta media",
        "Gamma baja",
    ]

    by_tag = client.get("/api/tasks", params={"tag": "backend"}).json()
    assert [task["id"] for task in by_tag] == [alta["id"]]

    overdue = client.get("/api/tasks", params={"overdue": True}).json()
    assert [task["id"] for task in overdue] == [baja["id"]]

    search = client.get("/api/tasks", params={"q": "despliegue"}).json()
    assert [task["id"] for task in search] == [media["id"]]

    by_due = client.get("/api/tasks", params={"sort": "due"}).json()
    assert by_due[0]["id"] == baja["id"]


def test_cp_in_06_historial_de_actividad(client):
    task = client.post("/api/tasks", json={"title": "Historial"}).json()
    task_id = task["id"]
    client.post(f"/api/tasks/{task_id}/subtasks", json={"title": "Paso"})
    client.patch(f"/api/tasks/{task_id}/move", json={"status": "En curso"})

    reread = client.get("/api/tasks").json()[0]
    actions = [entry["action"] for entry in reread["activity"]]
    assert actions[0] == "Movida a En curso"
    assert actions[1] == "Subtarea agregada: Paso"
    assert actions[2] == "Tarea creada"
