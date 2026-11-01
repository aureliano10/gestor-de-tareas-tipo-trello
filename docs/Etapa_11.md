# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 11 - Automatización

## Objetivo de la etapa

Seleccionar pruebas del sistema que puedan automatizarse, automatizar como mínimo tres casos de prueba y documentar la herramienta utilizada, el motivo de su elección, las pruebas automatizadas, el procedimiento de ejecución, los resultados obtenidos y las ventajas y limitaciones encontradas. En este trabajo la automatización se construyó de forma incremental a lo largo de las etapas 8, 9 y 10, de modo que esta etapa consolida y documenta el marco ya existente.

## Herramientas utilizadas

| Herramienta | Uso en el proyecto | Versión | Motivo de la elección |
|-------------|--------------------|---------|------------------------|
| **pytest** | Pruebas unitarias (Etapa 8) y de integración (Etapa 9). | 9.2.0 | Es el marco de pruebas estándar de facto en Python, equivalente a JUnit para Java. Permite aserciones con `assert` plano, descubrimiento automático de archivos `test_*.py`, parametrización, fixtures reutilizables, reportes detallados y salida JUnit XML. Ya estaba disponible en el entorno virtual del proyecto. |
| **pytest** + `TestClient` de FastAPI | Pruebas de integración del stack HTTP completo sin servidor externo. | 9.2.0 / FastAPI 0.136.3 | El `TestClient` levanta la aplicación ASGI en proceso y dispara el ciclo de vida (`init_db`), lo que permite ejercitar routers → schemas → repository → SQLite con el mismo código que corre en producción, sin depender de un proceso separado. |
| **httpx** | Ejecución de los 62 casos de API contra el backend real. | 0.28.1 | Es un cliente HTTP moderno y síncrono, con timeout configurable, envío de JSON y de archivos multipart, ideal para verificar códigos de estado, cuerpos y cabeceras de una API REST en ejecución. |
| **Playwright** | Ejecución de los 11 casos de interfaz sobre Chrome real. | 1.64.1 | Permite automatizar un navegador real en modo headless, interactuar con el DOM (arrastrar y soltar, clic, carga de archivos), capturar las peticiones de red y tomar capturas de pantalla, todo lo necesario para probar la interfaz React sin instrumentarla. |
| **Runner propio de caja blanca** | Ejecución de los 7 casos de caja blanca. | Python 3.12.3 | Combina la invocación directa de unidades del backend (para aislar ramas de decisión) con la ejecución real del frontend con Playwright, unificando las dos técnicas en un único script reproducible. |
| **ruff** | Verificación de estilo del código de pruebas. | 0.17.3 | Análisis estático rápido que mantiene el código de la suite y del backend con un estilo uniforme y sin avisos, como paso previo a cada commit. |

## Marco de automatización

La automatización se organiza en tres capas de scripts reproducibles, todos en formato Python y ejecutables desde la raíz del repositorio:

| Capa | Ubicación | Alcance | Casos |
|------|-----------|---------|-------|
| Pruebas automatizadas con pytest | `backend/tests/` | Unitarias e integración del backend. | 18 + 6 |
| Suite de sistema | `scripts/etapa_6/` | API (`httpx`), interfaz (`Playwright`) y caja blanca. | 62 + 11 + 7 |
| Runners de evidencias | `scripts/etapa_8/` y `scripts/etapa_9/` | Ejecutan pytest, guardan el log y arman el JSON de resultados. | — |

Elementos comunes:

- **Aislamiento por prueba:** cada prueba configura variables de entorno (`KANBAN_DB_PATH`, `KANBAN_STORAGE_PATH`) que apuntan a rutas temporales, de modo que no se afectan los datos del proyecto.
- **Resultados en formato estructurado:** los runners guardan la salida completa en texto y un JSON con el estado de cada caso, lo que permite trazarlos en la documentación.
- **Reejecutables:** cualquier integrante puede repetir la corrida con un comando y obtener los mismos archivos de evidencia.

## Pruebas automatizadas

A continuación se presentan en detalle cinco casos automatizados concretos, que cubren las cuatro herramientas (pytest unitario, pytest de integración, httpx y Playwright).

### Caso 1 - CP-UN-02: valores límite de `clean_title` (pytest, unitaria)

**Objetivo:** verificar los límites de longitud y las clases inválidas de la función de validación del título.

**Código** (`backend/tests/test_unit_schemas.py`):

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

**Resultado obtenido:** aprobado; 1 y 100 caracteres aceptados; 101, vacío y solo espacios rechazados con el mensaje esperado.

### Caso 2 - CP-IN-03: flujo de estados con regla de negocio (pytest + `TestClient`, integración)

**Objetivo:** verificar la interacción entre el router de tareas, el repositorio y SQLite en las transiciones de estado y el bloqueo de finalización.

**Código** (`backend/tests/test_integration_flow.py`):

```python
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
```

**Resultado obtenido:** aprobado; la finalización con una subtarea pendiente respondió 409 conservando "En curso" y, tras completar la subtarea, finalizó con 200.

### Caso 3 - CP-CRE-01: alta de tarea contra el backend real (httpx, API)

**Objetivo:** verificar el alta típica y la forma completa de la respuesta de la API en ejecución.

**Código** (`scripts/etapa_6/ejecutar_api.py`, fragmento):

```python
def cp_cre_01() -> dict:
    reset_server_db()
    response, body = post({"title": "Preparar informe"})
    tasks = list_tasks()
    appears = isinstance(body, dict) and any(
        item["id"] == body.get("id") for item in tasks
    )
    checks = {
        "HTTP 201": response.status_code == 201,
        "id entero": isinstance(body.get("id"), int),
        "título correcto": body.get("title") == "Preparar informe",
        "descripción vacía": body.get("description") == "",
        "estado Pendiente": body.get("status") == "Pendiente",
        "position 0": body.get("position") == 0,
        "overdue falso": body.get("overdue") is False,
        "aparece en el listado": appears,
    }
    obtained = (
        f"HTTP 201; tarea #{body.get('id')} creada en estado Pendiente, "
        f"position 0 y overdue falso, presente en el listado"
    )
    return make_result("CP-CRE-01", checks, obtained, "Alta típica.", body)
```

**Resultado obtenido:** aprobado; HTTP 201, tarea creada en estado "Pendiente", con posición 0 y `overdue` falso, presente en el listado.

### Caso 4 - CP-UI-01: alta desde la interfaz (Playwright, UI)

**Objetivo:** verificar el alta a través del formulario real del tablero y la persistencia tras recargar la página.

**Código** (`scripts/etapa_6/ejecutar_ui.py`, fragmento):

```python
def ui_01(page, _prepared) -> dict:
    title = "Tarea desde interfaz"
    page.fill(FORM_TITLE, title)
    page.click(FORM_SUBMIT)
    task_in(page, "Pendiente", title).wait_for(timeout=10000)

    visible = task_in(page, "Pendiente", title).count() == 1
    input_value = page.input_value(FORM_TITLE)
    summary = page.inner_text('[data-testid="task-count"]').strip()
    pending_count = column_count(page, "Pendiente")

    reload_board(page)
    persisted = task_in(page, "Pendiente", title).count() == 1

    checks = {
        "tarjeta visible en Pendiente": visible,
        "el campo de título queda vacío": input_value == "",
        "el resumen general muestra 1 tarea": summary == "1 tarea",
        "el contador de Pendiente muestra 1": pending_count == "1",
        "la tarea persiste tras recargar": persisted,
    }
    return make_result("CP-UI-01", checks, obtained, "Alta desde el formulario.")
```

**Resultado obtenido:** aprobado; la tarjeta quedó visible en "Pendiente", el campo se limpió, el resumen mostró "1 tarea" y la tarea persistió al recargar.

### Caso 5 - CP-CB-07: decisiones de arrastre en la interfaz (Playwright, caja blanca)

**Objetivo:** cubrir las ramas de decisión de `handleDrop` y de la función de índice de destino (misma columna, columna distinta e identificadores inválidos).

**Código** (`scripts/etapa_6/ejecutar_caja_blanca.py`, fragmento):

```python
    drag_task(page, prepared["beta"]["id"], "Pendiente", client_y=0)
    reordered = wait_titles(page, "Pendiente", ["Beta", "Alfa"], timeout=10.0)
    same_column_bodies = request_bodies(patches)

    drag_task(page, prepared["alfa"]["id"], "En curso", client_y=0)
    task_in(page, "En curso", "Alfa").wait_for(timeout=10000)
    moved_bodies = request_bodies(patches)

    drop_raw(page, "abc", "Terminada")
    drop_raw(page, "0", "Terminada")
    page.wait_for_timeout(500)
    total_patches = len(patches)
```

**Resultado obtenido:** aprobado; el reordenamiento en la misma columna emitió un `PATCH` con posición 0 y reordenó, el movimiento de columna emitió el `PATCH` con el estado destino y los identificadores inválidos no emitieron ninguna petición.

## Procedimiento de ejecución

Las pruebas unitarias y de integración son autocontenidas y no requieren servidor. Los comandos, desde la raíz del repositorio:

1. **Pruebas unitarias (pytest):**
   `.venv/bin/python -m pytest backend/tests/test_unit_schemas.py backend/tests/test_unit_repository.py backend/tests/test_unit_database.py -v`
2. **Pruebas de integración (pytest + `TestClient`):**
   `.venv/bin/python -m pytest backend/tests/test_integration_flow.py -v`
3. **Regenerar las evidencias de ambas:**
   `.venv/bin/python scripts/etapa_8/ejecutar_pytest.py` y
   `.venv/bin/python scripts/etapa_9/ejecutar_pytest.py`
4. **Suite de sistema (requiere el backend en 8000 y el frontend en 5173).**
   Iniciar el backend de pruebas desde `backend/`:
   `KANBAN_DB_PATH=/tmp/kanban_etapa6.db KANBAN_STORAGE_PATH=/tmp/kanban_etapa6_storage ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
   Iniciar el frontend con `npm run dev` desde `frontend/` y luego ejecutar:
   `.venv/bin/python scripts/etapa_6/ejecutar_api.py`,
   `.venv/bin/python scripts/etapa_6/ejecutar_ui.py`,
   `.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py` y
   `.venv/bin/python scripts/etapa_6/consolidar.py`.

## Resultados obtenidos

| Conjunto | Herramienta | Casos | Aprobados | Fallidos | Resultado |
|----------|-------------|-------|-----------|----------|-----------|
| Pruebas unitarias | pytest | 18 | 18 | 0 | 100% aprobado |
| Pruebas de integración | pytest + `TestClient` | 6 | 6 | 0 | 100% aprobado |
| Casos de API | httpx | 62 | 62 | 0 | 100% aprobado |
| Casos de interfaz | Playwright | 11 | 11 | 0 | 100% aprobado |
| Casos de caja blanca | Runner propio | 7 | 7 | 0 | 100% aprobado |
| **Total** | — | **104** | **104** | **0** | **100% aprobado** |

Resultados literales de las corridas de esta etapa:

- Unitarias: `18 passed in 0.61s`.
- Integración: `6 passed, 1 warning in 1.30s` (el aviso es un `StarletteDeprecationWarning` del `TestClient` y no afecta el resultado).
- Suite de sistema: `API: 62/62 aprobados`, `UI: 11/11 aprobados`, `Caja blanca: 7/7 aprobados` y `Total: 80/80 aprobados, 0 fallidos`.

## Ventajas encontradas

- **Reproducibilidad total:** un comando por conjunto vuelve a ejecutar las pruebas y regenera las evidencias en formato texto y JSON.
- **Detección temprana y regresión:** las pruebas unitarias y de integración corren en menos de dos segundos y no necesitan servidor, por lo que sirven como red de seguridad ante cada cambio.
- **Cobertura de los tres planos:** la combinación de pytest, httpx y Playwright verifica la lógica pura, el contrato HTTP y el comportamiento real de la interfaz.
- **Aislamiento y limpieza:** el uso de bases y almacenamientos temporales por prueba evita interferencias entre casos y con los datos del proyecto.
- **Evidencia trazable:** cada corrida deja un JSON con el estado por caso, lo que facilita armar las matrices de trazabilidad y los informes.
- **Verificación de red e integración:** Playwright permite además interceptar y comprobar las peticiones que emite la interfaz, algo difícil de observar en pruebas manuales.

## Limitaciones encontradas

- **Dependencia del entorno para la suite de sistema:** los casos de API, interfaz y caja blanca requieren el backend en el puerto 8000 y, los de interfaz, el frontend en el 5173 y Chrome instalado; si el navegador o el entorno falla, esos casos no se ejecutan (las unitarias e integración no tienen esta dependencia).
- **Costo y velocidad de la interfaz:** las pruebas con Playwright son notablemente más lentas que las de API y sensibles a la sincronización con React (por ejemplo, la casilla de subtareas controlada, que se resuelve esperando el estado final en lugar de comprobar el clic inmediato).
- **Casos ligados al sistema real:** los scripts de la suite usan selectores `data-testid`, de modo que un cambio de esos atributos obliga a actualizar los localizadores; además, los identificadores de las tareas cambian entre corridas (el caso CP-CRE-01 reporta el `id` real del momento).
- **Datos externos al programa:** la ejecución de interfaz depende de Chrome del sistema (`channel="chrome"`), una dependencia externa al entorno virtual de Python.
- **Caja blanca del frontend:** dos casos diseñados para aislar unidades del frontend se ejecutaron sobre la interfaz real con Playwright, una decisión de ejecución que cubre las mismas ramas pero con mayor acoplamiento a la interfaz.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Log de las corridas automatizadas | `docs/evidencias/etapa_11/pytest_automation.log` |
| Salida completa de las unitarias | `docs/evidencias/etapa_11/pytest_unitarias_salida.txt` |
| Resultados de las unitarias | `docs/evidencias/etapa_11/resultados_unitarias.json` |
| Salida completa de la integración | `docs/evidencias/etapa_11/pytest_integracion_salida.txt` |
| Resultados de la integración | `docs/evidencias/etapa_11/resultados_integracion.json` |
| Código de las pruebas | `backend/tests/` y `scripts/etapa_6/` |
| Log de la suite de sistema | `docs/evidencias/etapa_10/ejecucion_sistema.log` |

## Conclusión de la etapa

Se documentó el marco de automatización construido a lo largo del trabajo y se presentaron cinco casos automatizados concretos que cubren las cuatro herramientas elegidas: pytest para las pruebas unitarias, pytest con `TestClient` para las de integración, httpx para las de API y Playwright para las de interfaz. La automatización supera ampliamente el mínimo de tres casos exigido: en total se automatizaron **104 casos**, todos aprobados (18 unitarios, 6 de integración, 62 de API, 11 de interfaz y 7 de caja blanca), con procedimientos reproducibles y evidencias reales de ejecución. Las limitaciones identificadas se concentran en la dependencia del entorno para la suite de sistema y en el costo de las pruebas de interfaz, ambas compensadas por la velocidad y la portabilidad de las pruebas unitarias y de integración.
