"""Pruebas del selector de base remota y del storage de adjuntos."""

from __future__ import annotations

import asyncio

import pytest

from app import database, storage


def test_using_remote_db_lee_turso(monkeypatch):
    monkeypatch.setenv("TURSO_DATABASE_URL", "libsql://demo.turso.io")
    assert database.using_remote_db() is True

    monkeypatch.delenv("TURSO_DATABASE_URL")
    assert database.using_remote_db() is False


def test_using_blob_segun_entorno(monkeypatch):
    for name in (
        "KANBAN_STORAGE",
        "BLOB_READ_WRITE_TOKEN",
        "VERCEL_BLOB_READ_WRITE_TOKEN",
        "BLOB_STORE_ID",
        "VERCEL",
    ):
        monkeypatch.delenv(name, raising=False)

    assert storage.using_blob() is False

    monkeypatch.setenv("BLOB_READ_WRITE_TOKEN", "vercel_blob_rw_store_secret")
    assert storage.using_blob() is True

    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN")
    monkeypatch.setenv("VERCEL_BLOB_READ_WRITE_TOKEN", "vercel_blob_rw_store_secret")
    assert storage.using_blob() is True

    monkeypatch.delenv("VERCEL_BLOB_READ_WRITE_TOKEN")
    monkeypatch.setenv("BLOB_STORE_ID", "store_x")
    monkeypatch.setenv("VERCEL", "1")
    assert storage.using_blob() is True

    monkeypatch.setenv("KANBAN_STORAGE", "local")
    assert storage.using_blob() is False


def test_get_connection_usa_turso(monkeypatch):
    class FakeConnection:
        def __init__(self):
            self.row_factory = None
            self.executed = []

        def execute(self, sql, params=()):
            self.executed.append(sql)

    fake = FakeConnection()
    calls = {}

    def fake_connect(url, auth_token=None):
        calls["url"] = url
        calls["auth_token"] = auth_token
        return fake

    import turso_serverless

    monkeypatch.setattr(turso_serverless, "connect", fake_connect)
    monkeypatch.setenv("TURSO_DATABASE_URL", "libsql://demo.turso.io")
    monkeypatch.setenv("TURSO_AUTH_TOKEN", "token")

    conn = database.get_connection()

    assert conn is fake
    assert calls == {"url": "libsql://demo.turso.io", "auth_token": "token"}
    assert fake.row_factory is turso_serverless.Row
    assert "PRAGMA foreign_keys = ON" in fake.executed


def test_init_db_falla_en_vercel_sin_turso(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "_ON_VERCEL", True)
    monkeypatch.delenv("TURSO_DATABASE_URL", raising=False)
    monkeypatch.delenv("KANBAN_ALLOW_EPHEMERAL", raising=False)
    monkeypatch.setenv("KANBAN_STORAGE", "local")
    monkeypatch.setenv("KANBAN_DB_PATH", str(tmp_path / "tasks.db"))
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))

    with pytest.raises(RuntimeError, match="TURSO_DATABASE_URL"):
        database.init_db()


def test_save_y_delete_attachment_en_blob(monkeypatch):
    monkeypatch.setenv("KANBAN_STORAGE", "blob")

    from vercel import blob

    calls = {}

    async def fake_put_blob(pathname, body, **kwargs):
        calls["put"] = (pathname, body, kwargs)

    async def fake_delete_blob(pathname):
        calls["delete"] = pathname

    monkeypatch.setattr(blob, "put_blob", fake_put_blob)
    monkeypatch.setattr(blob, "delete_blob", fake_delete_blob)

    asyncio.run(
        storage.save_attachment(7, "abc.txt", b"hola", "text/plain")
    )
    asyncio.run(storage.delete_attachment(7, "abc.txt"))

    pathname, body, kwargs = calls["put"]
    assert pathname == "tasks/7/abc.txt"
    assert body == b"hola"
    assert kwargs["access"] == "private"
    assert kwargs["content_type"] == "text/plain"
    assert calls["delete"] == "tasks/7/abc.txt"


def test_save_y_delete_attachment_local(monkeypatch, tmp_path):
    monkeypatch.setenv("KANBAN_STORAGE", "local")
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))

    asyncio.run(storage.save_attachment(1, "x.txt", b"data", "text/plain"))
    target = tmp_path / "storage" / "x.txt"
    assert target.read_bytes() == b"data"

    asyncio.run(storage.delete_attachment(1, "x.txt"))
    assert not target.exists()
