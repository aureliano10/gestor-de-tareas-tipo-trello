# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 8 - Pruebas unitarias

## Objetivo de la etapa

Implementar pruebas unitarias automatizadas sobre las principales funciones del sistema, seleccionando al menos tres funciones o métodos con lógica verificable, y comprobar su funcionamiento de forma aislada. Se presentan el código de las pruebas, los casos evaluados, los resultados y las evidencias de ejecución.

## Herramienta elegida

Se utilizó **pytest 9.2.0** como herramienta de pruebas unitarias para el backend en Python.

| Alternativa | Motivo de la elección |
|-------------|-----------------------|
| **pytest** | Es el marco de pruebas estándar de facto en el ecosistema Python, equivalente al JUnit exigido para Java. Ofrece aserciones con `assert` plano, descubrimiento automático de los archivos `test_*.py`, ejecución parametrizable, un sistema de fixtures reutilizable y reportes detallados. Ya se encuentra instalado en el entorno virtual del proyecto junto con `httpx` y `playwright`. |
| unittest | Es la biblioteca estándar, pero requiere más código repetitivo (`TestCase`, `self.assertEqual`) y no aporta ventajas frente a pytest en este proyecto. |

pytest es la herramienta equivalente indicada por la consigna para un desarrollo en Python.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| pytest | 9.2.0 |
| Pydantic | 2.13.4 |
| FastAPI | 0.136.3 |
| SQLite | 3.45.1 |
| ruff | 0.17.3 |
| Entorno | `.venv` del repositorio |

Las pruebas son autocontenidas: cada una configura una base SQLite y un almacenamiento temporales con las variables de entorno `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH`, y luego inicializa el esquema con `init_db()`. De esta manera no se afecta la base real del servidor en el puerto 8000 ni los datos del proyecto.

## Funciones seleccionadas

Se seleccionaron funciones de las tres capas con lógica verificable de forma aislada.

| Función o método | Archivo | Capa | Lógica verificada |
|------------------|---------|------|-------------------|
| `clean_title` | `backend/app/schemas.py` | Validación | Normalización de espacios, obligatoriedad y longitud máxima de 100. |
| `clean_description` | `backend/app/schemas.py` | Validación | Campo opcional y longitud máxima de 500. |
| `clean_priority` | `backend/app/schemas.py` | Validación | Pertenencia al conjunto {Baja, Media, Alta}. |
| `clean_assignee` | `backend/app/schemas.py` | Validación | Campo opcional, normalización y longitud máxima de 60. |
| `clean_tag` | `backend/app/schemas.py` | Validación | Etiqueta no vacía y longitud máxima de 30. |
| `clean_tags` | `backend/app/schemas.py` | Validación | Deduplicación sin distinguir mayúsculas conservando el orden. |
| `clean_link_url` | `backend/app/schemas.py` | Validación | Esquema `http://`/`https://` y longitud máxima de 500. |
| `clean_link_label` | `backend/app/schemas.py` | Validación | Nombre de enlace opcional y de hasta 60 caracteres. |
| `_resolve_tag_id` | `backend/app/repository.py` | Datos | Reutilización de etiquetas existentes sin distinguir mayúsculas. |
| `_set_tags` | `backend/app/repository.py` | Datos | Asociación, deduplicación y límite de 5 etiquetas. |
| `_normalize_links` | `backend/app/repository.py` | Datos | Normalización de enlaces, rechazo de duplicados y límite de 5. |
| `create_task` | `backend/app/repository.py` | Negocio | Límite de 20 subtareas en el alta. |
| `move_task` | `backend/app/repository.py` | Negocio | Bloqueo de finalización con subtareas pendientes. |
| `create_attachment` | `backend/app/repository.py` | Negocio | Límite de 3 adjuntos por tarea. |
| `init_db` / `_needs_migration` | `backend/app/database.py` | Persistencia | Creación del esquema y migración aditiva. |
| `connection` | `backend/app/database.py` | Persistencia | Confirmación y reversión de transacciones. |

## Estrategia de pruebas unitarias

Se aplicaron las técnicas de **clases de equivalencia** y **análisis de valores límite** sobre los máximos reales del sistema:

| Dato | Valor límite | Clases de equivalencia |
|------|--------------|------------------------|
| Título | 1, 100 y 101 caracteres | Vacío, solo espacios, válido, demasiado largo, nulo. |
| Descripción | 500 y 501 caracteres | Opcional/ausente, válida, demasiado larga. |
| Responsable | 60 y 61 caracteres | Vacío, válido, demasiado largo. |
| Etiqueta | 30 y 31 caracteres | Vacía, solo espacios, válida, demasiado larga. |
| URL de enlace | 500 y 501 caracteres | Esquema http/https, esquema inválido, demasiado larga. |
| Nombre de enlace | 60 y 61 caracteres | Vacío, válido, demasiado largo. |
| Etiquetas por tarea | 5 y 6 | Dentro del límite, fuera del límite, con duplicados. |
| Enlaces por tarea | 5 y 6 | Dentro del límite, fuera del límite, con duplicados. |
| Subtareas en el alta | 20 y 21 | Dentro del límite, fuera del límite. |
| Adjuntos por tarea | 3 y 4 | Dentro del límite, fuera del límite. |

Cada función se probó por invocación directa, sin pasar por la interfaz ni por el servidor HTTP, verificando tanto los valores devueltos como las excepciones esperadas. La base de datos se aisló con la fixture `unit_db`, que crea rutas temporales por prueba.

## Casos evaluados

| ID | Función | Datos de entrada | Resultado esperado | Resultado obtenido | Estado |
|----|---------|------------------|--------------------|--------------------|--------|
| CP-UN-01 | `clean_title` | `"  Revisar tablero  "`, `"Tarea"` | Recorta los espacios externos y conserva el texto. | `"Revisar tablero"`, `"Tarea"`. | Aprobado |
| CP-UN-02 | `clean_title` | `"a"`, `"a"x100`, `"a"x101`, `""`, `"   "`, `None` | 1 y 100 válidos; 101, vacío y solo espacios lanzan `ValueError`; `None` lanza el mensaje de obligatoriedad. | Limites válidos aceptados; 101, vacío y solo espacios rechazados; `None` lanzó "El título es obligatorio". | Aprobado |
| CP-UN-03 | `clean_description` | `None`, `"   "`, `"d"x500`, `"d"x501` | `None` y espacios devuelven `""`; 500 válido; 501 lanza `ValueError`. | `""` para ausente/espacios; 500 aceptado; 501 rechazado. | Aprobado |
| CP-UN-04 | `clean_priority` | `"Baja"`, `"Media"`, `"Alta"`, `"alta"`, `"Urgente"`, `""` | Los tres valores válidos pasan; el resto lanza `ValueError`. | Válidos aceptados; `"alta"`, `"Urgente"` y `""` rechazados. | Aprobado |
| CP-UN-05 | `clean_assignee` | `"  Ana Gómez  "`, `""`, `None`, `"a"x60`, `"a"x61` | Recorta; vacío y `None` devuelven `""`; 60 válido; 61 lanza `ValueError`. | `"Ana Gómez"`, `""`, `""`; 60 aceptado; 61 rechazado. | Aprobado |
| CP-UN-06 | `clean_tag` | `"  bug  "`, `"a"x30`, `""`, `"     "`, `"a"x31` | Recorta; 30 válido; vacía y solo espacios lanzan `ValueError`; 31 lanza `ValueError`. | `"bug"`; 30 aceptado; vacía y solo espacios rechazadas; 31 rechazado. | Aprobado |
| CP-UN-07 | `clean_tags` | `["Bug","bug","  Bug "]`, `["uno","dos","uno"]`, `[]`, `None` | Deduplica sin distinguir mayúsculas conservando la primera grafía y el orden. | `["Bug"]`, `["uno","dos"]`, `[]`, `[]`. | Aprobado |
| CP-UN-08 | `clean_link_url` | `"  https://ejemplo.com  "`, `http://`, `HTTPS://`, url de 500, de 501, `"ftp://..."`, `"ejemplo.com"` | Recorta; acepta http/https en cualquier caso; 500 válido; 501 y esquema inválido lanzan `ValueError`. | Recorte y esquemas válidos aceptados; 500 aceptada; 501, `ftp://` y url sin esquema rechazadas. | Aprobado |
| CP-UN-09 | `clean_link_label` | `"  Docs  "`, `""`, `None`, `"a"x60`, `"a"x61` | Recorta; vacío y `None` devuelven `""`; 60 válido; 61 lanza `ValueError`. | `"Docs"`, `""`, `""`; 60 aceptado; 61 rechazado. | Aprobado |
| CP-UN-10 | `_resolve_tag_id` | `"Bug"`, `"bUg"`, `"Mejora"` | Devuelve el mismo id para `"Bug"` y `"bUg"`, y uno distinto para una etiqueta nueva. | `first == same` y `other != first`. | Aprobado |
| CP-UN-11 | `_set_tags` | `["uno","dos","uno"]` y 6 etiquetas | Deduplica a `{uno, dos}`; con 6 lanza `TagLimitError` sin alterar la tarea. | `["dos","uno"]`; 6 etiquetas lanzó `TagLimitError` y la tarea conservó `["dos","uno"]`. | Aprobado |
| CP-UN-12 | `_normalize_links` | dict + `LinkCreate`; duplicado con distinta caja; 6 enlaces | Devuelve pares `(url, label)`; el duplicado lanza `ValueError`; 6 lanza `LinkLimitError`. | `[("https://uno.com","Uno"),("https://dos.com","")]`; duplicado y 6 enlaces rechazados. | Aprobado |
| CP-UN-13 | `create_task` | 20 subtareas; 21 subtareas | 20 válidas; 21 lanza `SubtaskLimitError`. | `subtasks` con 20 elementos; 21 rechazadas. | Aprobado |
| CP-UN-14 | `move_task` | Tarea con subtarea pendiente a Terminada; tarea con subtarea completada a Terminada | Bloqueo con `PendingSubtasksError` (`pending=1`) conservando "Pendiente"; con todo completado pasa a "Terminada". | Error con `pending=1` y estado "Pendiente"; finalización permitida a "Terminada". | Aprobado |
| CP-UN-15 | `create_attachment` | 3 altas válidas; cuarta alta | Acumula 1, 2 y 3; la cuarta lanza `AttachmentLimitError` conservando 3. | 3 adjuntos; cuarta rechazada; 3 adjuntos finales. | Aprobado |
| CP-UN-16 | `init_db` | Base temporal nueva | Crea las siete tablas del esquema. | Las siete tablas (`tasks`, `subtasks`, `attachments`, `tags`, `task_tags`, `links`, `activity`) presentes. | Aprobado |
| CP-UN-17 | `init_db` / `_needs_migration` | Tabla `tasks` incompleta con una fila | Detecta las columnas faltantes y las agrega de forma aditiva sin recrear la tabla ni perder filas. | `_needs_migration` verdadero; columnas agregadas; fila preservada; tablas creadas. | Aprobado |
| CP-UN-18 | `connection` | `INSERT` seguido de `RuntimeError` dentro del contexto | Revierte la transacción y no persiste la fila. | El conteo de tareas quedó en 0. | Aprobado |

## Código de las pruebas

Las pruebas se ubican en `backend/tests/`: `test_unit_schemas.py`, `test_unit_repository.py` y `test_unit_database.py`, con la fixture compartida en `conftest.py`.

Aislamiento de la base y del almacenamiento por prueba (`conftest.py`):

```python
@pytest.fixture
def unit_db(tmp_path, monkeypatch):
    """Base SQLite y almacenamiento temporales ya inicializados."""
    monkeypatch.setenv("KANBAN_DB_PATH", str(tmp_path / "unit.db"))
    monkeypatch.setenv("KANBAN_STORAGE_PATH", str(tmp_path / "storage"))

    from app.database import init_db

    init_db()
    return tmp_path
```

Valores límite de longitud del título (`test_unit_schemas.py`):

```python
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
```

Normalización de enlaces y rechazo de duplicados (`test_unit_repository.py`):

```python
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
```

Migración aditiva del esquema (`test_unit_database.py`):

```python
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
```

## Resumen de resultados

| Métrica | Valor |
|---------|-------|
| Funciones o métodos con pruebas | 16 |
| Casos de prueba | 18 |
| Pasados | 18 |
| Fallados | 0 |
| Resultado | 100% aprobado |

Resultado de la corrida: `18 passed in 0.48s`.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Código de las pruebas | `backend/tests/conftest.py`, `backend/tests/test_unit_schemas.py`, `backend/tests/test_unit_repository.py`, `backend/tests/test_unit_database.py` |
| Salida completa de pytest | `docs/evidencias/etapa_8/pytest_salida.txt` |
| Casos evaluados y su estado | `docs/evidencias/etapa_8/resultados_unitarias.json` |
| Script de ejecución | `scripts/etapa_8/ejecutar_pytest.py` |

## Reproducibilidad

Desde la raíz del repositorio:

1. Ejecutar las pruebas: `.venv/bin/python -m pytest backend/tests/test_unit_schemas.py backend/tests/test_unit_repository.py backend/tests/test_unit_database.py -v`.
2. Regenerar las evidencias: `.venv/bin/python scripts/etapa_8/ejecutar_pytest.py`.

No se requiere ningún servidor en ejecución: las pruebas crean su propia base temporal.

## Conclusión de la etapa

Se implementaron 18 pruebas unitarias automatizadas con pytest sobre 16 funciones o métodos de las capas de validación, acceso a datos y persistencia. Los 18 casos se ejecutaron y aprobaron, cubriendo clases de equivalencia y valores límite de los máximos reales del sistema. Las pruebas quedan disponibles como una suite reproducible integrada en `backend/tests/`.

## Próxima etapa

La Etapa 9 consistirá en las pruebas de integración sobre funcionalidades que involucren la interacción entre dos o más componentes del sistema.
