"""Pruebas unitarias del esquema y la migración de la base de datos."""

from __future__ import annotations

import sqlite3

import pytest

from app.database import (
    REQUIRED_TASK_COLUMNS,
    _needs_migration,
    connection,
    get_connection,
    get_db_path,
    init_db,
)

EXPECTED_TABLES = {
    "tasks",
    "subtasks",
    "attachments",
    "tags",
    "task_tags",
    "links",
    "activity",
}


def _table_names(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    return {row[0] for row in rows}


def _columns(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def test_cp_un_16_init_db_crea_todas_las_tablas(unit_db):
    assert EXPECTED_TABLES <= _table_names(get_db_path())


def test_cp_un_17_init_db_migra_tabla_legacy(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy.db"
    monkeypatch.setenv("KANBAN_DB_PATH", str(db_path))
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, "
            "status TEXT NOT NULL DEFAULT 'Pendiente', "
            "created_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO tasks (title, created_at) "
            "VALUES ('Tarea previa', '2026-01-01T00:00:00')"
        )
        conn.commit()

    probe = get_connection()
    try:
        assert _needs_migration(probe) is True
    finally:
        probe.close()

    init_db()

    with connection() as conn:
        columns = _columns(conn, "tasks")
        preserved = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks"
        ).fetchone()["total"]

    assert REQUIRED_TASK_COLUMNS <= columns
    assert preserved == 1
    assert EXPECTED_TABLES <= _table_names(db_path)


def test_cp_un_18_connection_revierte_ante_error(unit_db):
    with pytest.raises(RuntimeError):
        with connection() as conn:
            conn.execute(
                "INSERT INTO tasks (title, created_at) VALUES (?, ?)",
                ("Temporal", "2026-01-01T00:00:00"),
            )
            raise RuntimeError("Fallo simulado")

    with connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks"
        ).fetchone()["total"]
    assert total == 0
