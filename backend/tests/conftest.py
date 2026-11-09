"""Configuración común de las pruebas de las etapas 8 y 9.

Agrega el directorio ``backend`` al ``sys.path`` para poder importar el
paquete ``app`` y expone una base SQLite temporal aislada por prueba.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def unit_db(tmp_path, monkeypatch):
    """Base SQLite y almacenamiento temporales ya inicializados."""
    monkeypatch.setenv("KANBAN_DB_PATH", str(tmp_path / "unit.db"))
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("KANBAN_STORAGE", "local")
    monkeypatch.delenv("TURSO_DATABASE_URL", raising=False)
    monkeypatch.delenv("TURSO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)
    monkeypatch.delenv("VERCEL_BLOB_READ_WRITE_TOKEN", raising=False)
    monkeypatch.delenv("BLOB_STORE_ID", raising=False)

    from app.database import init_db

    init_db()
    return tmp_path
