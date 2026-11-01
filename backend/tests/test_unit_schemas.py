"""Pruebas unitarias de las funciones de limpieza y validación (schemas)."""

from __future__ import annotations

import pytest

from app.schemas import (
    EMPTY_TAG_MESSAGE,
    EMPTY_TITLE_MESSAGE,
    INVALID_LINK_MESSAGE,
    INVALID_PRIORITY_MESSAGE,
    TOO_LONG_ASSIGNEE_MESSAGE,
    TOO_LONG_DESCRIPTION_MESSAGE,
    TOO_LONG_LINK_LABEL_MESSAGE,
    TOO_LONG_LINK_MESSAGE,
    TOO_LONG_TAG_MESSAGE,
    TOO_LONG_TITLE_MESSAGE,
    clean_assignee,
    clean_description,
    clean_link_label,
    clean_link_url,
    clean_priority,
    clean_tag,
    clean_tags,
    clean_title,
)


def test_cp_un_01_clean_title_normalizacion():
    assert clean_title("  Revisar tablero  ") == "Revisar tablero"
    assert clean_title("Tarea") == "Tarea"


def test_cp_un_02_clean_title_limites():
    assert clean_title("a") == "a"
    assert clean_title("a" * 100) == "a" * 100
    with pytest.raises(ValueError, match=TOO_LONG_TITLE_MESSAGE):
        clean_title("a" * 101)
    with pytest.raises(ValueError, match=EMPTY_TITLE_MESSAGE):
        clean_title("")
    with pytest.raises(ValueError, match=EMPTY_TITLE_MESSAGE):
        clean_title("   ")
    with pytest.raises(ValueError, match="El título es obligatorio"):
        clean_title(None)


def test_cp_un_03_clean_description_limites():
    assert clean_description(None) == ""
    assert clean_description("   ") == ""
    assert clean_description("d" * 500) == "d" * 500
    with pytest.raises(ValueError, match=TOO_LONG_DESCRIPTION_MESSAGE):
        clean_description("d" * 501)


def test_cp_un_04_clean_priority_conjunto_permitido():
    assert clean_priority("Baja") == "Baja"
    assert clean_priority("Media") == "Media"
    assert clean_priority("Alta") == "Alta"
    for invalid in ("alta", "Urgente", ""):
        with pytest.raises(ValueError, match=INVALID_PRIORITY_MESSAGE):
            clean_priority(invalid)


def test_cp_un_05_clean_assignee_opcional_y_limites():
    assert clean_assignee("  Ana Gómez  ") == "Ana Gómez"
    assert clean_assignee("") == ""
    assert clean_assignee(None) == ""
    assert clean_assignee("a" * 60) == "a" * 60
    with pytest.raises(ValueError, match=TOO_LONG_ASSIGNEE_MESSAGE):
        clean_assignee("a" * 61)


def test_cp_un_06_clean_tag_vacia_y_limites():
    assert clean_tag("  bug  ") == "bug"
    assert clean_tag("a" * 30) == "a" * 30
    with pytest.raises(ValueError, match=EMPTY_TAG_MESSAGE):
        clean_tag("")
    with pytest.raises(ValueError, match=EMPTY_TAG_MESSAGE):
        clean_tag("     ")
    with pytest.raises(ValueError, match=TOO_LONG_TAG_MESSAGE):
        clean_tag("a" * 31)


def test_cp_un_07_clean_tags_deduplica_sin_distinguir_mayusculas():
    assert clean_tags(["Bug", "bug", "  Bug "]) == ["Bug"]
    assert clean_tags(["uno", "dos", "uno"]) == ["uno", "dos"]
    assert clean_tags([]) == []
    assert clean_tags(None) == []


def test_cp_un_08_clean_link_url_esquema_y_limites():
    assert clean_link_url("  https://ejemplo.com  ") == "https://ejemplo.com"
    assert clean_link_url("http://ejemplo.com") == "http://ejemplo.com"
    assert clean_link_url("HTTPS://EJEMPLO.COM") == "HTTPS://EJEMPLO.COM"
    url_500 = "https://" + "a" * 492
    assert len(url_500) == 500
    assert clean_link_url(url_500) == url_500
    with pytest.raises(ValueError, match=TOO_LONG_LINK_MESSAGE):
        clean_link_url(url_500 + "a")
    with pytest.raises(ValueError, match=INVALID_LINK_MESSAGE):
        clean_link_url("ftp://ejemplo.com")
    with pytest.raises(ValueError, match=INVALID_LINK_MESSAGE):
        clean_link_url("ejemplo.com")


def test_cp_un_09_clean_link_label_opcional_y_limites():
    assert clean_link_label("  Docs  ") == "Docs"
    assert clean_link_label("") == ""
    assert clean_link_label(None) == ""
    assert clean_link_label("a" * 60) == "a" * 60
    with pytest.raises(ValueError, match=TOO_LONG_LINK_LABEL_MESSAGE):
        clean_link_label("a" * 61)
