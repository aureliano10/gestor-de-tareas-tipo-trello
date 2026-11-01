"""Pruebas unitarias de los helpers de normalización y de las reglas
de negocio del repositorio."""

from __future__ import annotations

import pytest

from app import repository
from app.database import connection
from app.repository import _normalize_links, _resolve_tag_id, _set_tags
from app.schemas import DUPLICATE_LINK_MESSAGE, LinkCreate


def test_cp_un_10_resolve_tag_id_reutiliza_sin_distinguir_mayusculas(unit_db):
    with connection() as conn:
        first = _resolve_tag_id(conn, "Bug")
        same = _resolve_tag_id(conn, "bUg")
        other = _resolve_tag_id(conn, "Mejora")
    assert first == same
    assert other != first


def test_cp_un_11_set_tags_deduplica_y_limita(unit_db):
    task = repository.create_task("Con etiquetas")
    with connection() as conn:
        _set_tags(conn, task["id"], ["uno", "dos", "uno"])
    assert repository.get_task(task["id"])["tags"] == ["dos", "uno"]

    with pytest.raises(repository.TagLimitError):
        with connection() as conn:
            _set_tags(conn, task["id"], [f"t{i}" for i in range(6)])

    assert repository.get_task(task["id"])["tags"] == ["dos", "uno"]


def test_cp_un_12_normalize_links_acepta_y_rechaza():
    pairs = _normalize_links(
        [
            {"url": "https://uno.com", "label": "Uno"},
            LinkCreate(url="https://dos.com"),
        ]
    )
    assert pairs == [("https://uno.com", "Uno"), ("https://dos.com", "")]

    with pytest.raises(ValueError, match=DUPLICATE_LINK_MESSAGE):
        _normalize_links([{"url": "https://uno.com"}, {"url": "HTTPS://UNO.COM"}])

    with pytest.raises(repository.LinkLimitError):
        _normalize_links([{"url": f"https://x{i}.com"} for i in range(6)])


def test_cp_un_13_create_task_limite_de_subtareas(unit_db):
    ok = repository.create_task(
        "Veinte subtareas",
        subtasks=[{"title": f"S{i}"} for i in range(20)],
    )
    assert len(ok["subtasks"]) == 20

    with pytest.raises(repository.SubtaskLimitError):
        repository.create_task(
            "Veintiuna subtareas",
            subtasks=[{"title": f"S{i}"} for i in range(21)],
        )


def test_cp_un_14_move_task_bloquea_con_subtareas_pendientes(unit_db):
    blocked = repository.create_task("Con pendiente")
    repository.create_subtask(blocked["id"], "Paso", done=False)

    with pytest.raises(repository.PendingSubtasksError) as error:
        repository.move_task(blocked["id"], "Terminada")
    assert error.value.pending == 1
    assert repository.get_task(blocked["id"])["status"] == "Pendiente"

    ready = repository.create_task("Sin pendientes")
    repository.create_subtask(ready["id"], "Hecho", done=True)
    finished = repository.move_task(ready["id"], "Terminada")
    assert finished["status"] == "Terminada"


def test_cp_un_15_create_attachment_limite(unit_db):
    task = repository.create_task("Con adjuntos")
    for index in range(3):
        repository.create_attachment(
            task["id"], f"f{index}.txt", f"s{index}.txt", "text/plain", 10
        )
    assert len(repository.get_task(task["id"])["attachments"]) == 3

    with pytest.raises(repository.AttachmentLimitError):
        repository.create_attachment(
            task["id"], "f4.txt", "s4.txt", "text/plain", 10
        )
    assert len(repository.get_task(task["id"])["attachments"]) == 3
