# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 29/10/2026

# Etapa 6 - Ejecución de pruebas

## Objetivo de la etapa

Ejecutar los 25 casos de prueba diseñados en la Etapa 5 sobre el sistema desarrollado, registrar los resultados obtenidos, verificar el cumplimiento de los requisitos RF1 a RF4 y analizar si las fallas, en caso de existir, corresponden a defectos del sistema.

## Alcance

Se ejecutaron los 25 casos del diseño:

- 15 casos de caja negra sobre la API.
- 5 casos de caja negra sobre la interfaz.
- 5 casos de caja blanca: 3 sobre unidades del backend y 2 sobre unidades del frontend.

La ejecución incluyó pruebas normales, con datos inválidos, con valores límite y con situaciones excepcionales, tal como requiere la consigna:

- **Normales:** alta, listado, movimiento y eliminación de tareas con datos válidos.
- **Datos inválidos:** títulos vacíos o con solo espacios, títulos de más de 100 caracteres, estados no permitidos e identificadores no numéricos.
- **Valores límite:** título de 1 carácter, de 100 caracteres y de 101 caracteres.
- **Situaciones excepcionales:** actualización o eliminación de una tarea inexistente, error HTTP 500 simulado en la API, arrastre dentro de la misma columna y arrastre con identificadores inválidos.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| FastAPI | 0.136.3 |
| Uvicorn | 0.49.0 |
| Pydantic | 2.13.4 |
| SQLite | 3.45.1 |
| httpx | 0.28.1 |
| Node.js | v24.14.1 |
| npm | 11.11.0 |
| Google Chrome | 151.0.7922.75 |
| Playwright | 1.64.1, con `channel="chrome"` y modo headless |
| Backend | `http://127.0.0.1:8000` |
| Frontend | `http://127.0.0.1:5173` con Vite |

La base de datos de la API se configuró con `KANBAN_DB_PATH=/tmp/kanban_etapa6.db` para no afectar datos del proyecto. Los casos de caja blanca del backend usaron `KANBAN_DB_PATH=/tmp/kanban_etapa6_wb.db`. Antes de cada caso se eliminaron las filas de la tabla `tasks` para garantizar aislamiento.

## Estrategia de ejecución

La ejecución se automatizó con scripts reproducibles ubicados en `scripts/etapa_6/`:

| Script | Función |
|--------|---------|
| `ejecutar_api.py` | Ejecuta los 15 casos de API con httpx y registra estados HTTP, cuerpos y persistencia. |
| `ejecutar_ui.py` | Ejecuta los 5 casos de interfaz con Playwright sobre Chrome del sistema y guarda capturas. |
| `ejecutar_caja_blanca.py` | Ejecuta los 3 casos de backend por invocación directa y los 2 de frontend sobre la interfaz real. |
| `consolidar.py` | Actualiza los resultados y estados en `Etapa_5.md`, y genera el resumen JSON. |
| `common.py` y `ui_helpers.py` | Funciones compartidas de API, base de datos, Playwright, arrastre y capturas. |

Criterios de aprobación:

- **API:** se verificaron el código HTTP, el cuerpo de la respuesta, el estado persistido y el listado posterior.
- **Interfaz:** se verificaron los elementos visibles, los contadores, los mensajes de error, las peticiones emitidas y la persistencia después de recargar la página.
- **Caja blanca:** se verificaron los valores devueltos, las excepciones y las ramas de decisión alcanzables.

Los resultados se registraron en archivos JSON, en un log de ejecución y en capturas de pantalla. Luego se trasladaron a las fichas de la Etapa 5 y al archivo `casos_de_prueba.csv`.

## Resultados generales

| Grupo | Casos | Aprobados | Fallidos | Resultado |
|-------|-------|-----------|----------|-----------|
| API | 15 | 15 | 0 | 100% aprobado |
| Interfaz | 5 | 5 | 0 | 100% aprobado |
| Caja blanca | 5 | 5 | 0 | 100% aprobado |
| **Total** | **25** | **25** | **0** | **100% aprobado** |

### Resultados por funcionalidad

| Funcionalidad | Casos | Aprobados | Fallidos |
|---------------|-------|-----------|----------|
| Crear tarea | 12 | 12 | 0 |
| Mover tarea | 8 | 8 | 0 |
| Eliminar tarea | 4 | 4 | 0 |
| Listar tareas y persistencia | 1 | 1 | 0 |
| **Total** | **25** | **25** | **0** |

### Resultados por requisito

| Requisito | Casos asociados | Resultado |
|-----------|-----------------|-----------|
| RF1: registrar una tarea | CP-CRE-01 a CP-CRE-08, CP-LIS-01, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-04 | Aprobado |
| RF2: estado inicial Pendiente | CP-CRE-01, CP-CRE-02, CP-CRE-03, CP-CRE-07, CP-CRE-08, CP-LIS-01, CP-UI-01 | Aprobado |
| RF3: actualizar el estado | CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-05 | Aprobado |
| RF4: eliminar una tarea | CP-ELI-01, CP-ELI-02, CP-UI-05, CP-CB-03 | Aprobado |
| Título obligatorio, no vacío y de hasta 100 caracteres | CP-CRE-02 a CP-CRE-08, CP-UI-02, CP-CB-01, CP-CB-04 | Aprobado |
| Persistencia de los cambios | CP-LIS-01, CP-UI-01, CP-UI-03, CP-UI-05, CP-CB-02, CP-CB-03 | Aprobado |

## Resultados por caso

| ID | Capa | Resultado obtenido | Estado |
|----|------|--------------------|--------|
| CP-CRE-01 | API | HTTP 201; tarea creada con estado "Pendiente" y presente en el listado. | Aprobado |
| CP-CRE-02 | API | HTTP 201; título "A" aceptado con estado "Pendiente". | Aprobado |
| CP-CRE-03 | API | HTTP 201; título de 100 caracteres aceptado. | Aprobado |
| CP-CRE-04 | API | HTTP 422; título de 101 caracteres rechazado y listado vacío. | Aprobado |
| CP-CRE-05 | API | HTTP 422; título vacío rechazado y listado vacío. | Aprobado |
| CP-CRE-06 | API | HTTP 422; título con solo espacios rechazado y listado vacío. | Aprobado |
| CP-CRE-07 | API | HTTP 201; espacios externos recortados y título persistido como "Revisar pruebas". | Aprobado |
| CP-CRE-08 | API | HTTP 201; acentos, eñe y símbolos preservados sin alteraciones. | Aprobado |
| CP-MOV-01 | API | PATCH 200 a "En curso" y a "Terminada"; estado final persistido. | Aprobado |
| CP-MOV-02 | API | PATCH 422 con estado "Finalizada"; la tarea permaneció en "Pendiente". | Aprobado |
| CP-MOV-03 | API | PATCH 404 con mensaje "Tarea no encontrada". | Aprobado |
| CP-MOV-04 | API | PATCH 422 por identificador no numérico. | Aprobado |
| CP-ELI-01 | API | DELETE 204 sin cuerpo; tarea ausente del listado. | Aprobado |
| CP-ELI-02 | API | DELETE 404 con mensaje "Tarea no encontrada". | Aprobado |
| CP-LIS-01 | API | GET 200 con listado vacío y con dos tareas ordenadas por id. | Aprobado |
| CP-UI-01 | Interfaz | Alta visible, campo limpio, contador en 1 y persistencia tras recargar. | Aprobado |
| CP-UI-02 | Interfaz | Error de validación visible; sin petición POST y sin tarjeta creada. | Aprobado |
| CP-UI-03 | Interfaz | Arrastre a "En curso" con un PATCH; persistencia tras recargar. | Aprobado |
| CP-UI-04 | Interfaz | Arrastre dentro de la misma columna sin PATCH; tarjeta sin cambios. | Aprobado |
| CP-UI-05 | Interfaz | Eliminación con un DELETE; sin tarjeta tras recargar. | Aprobado |
| CP-CB-01 | Backend (unidad) | Título válido normalizado; vacío, solo espacios y 101 caracteres rechazados. | Aprobado |
| CP-CB-02 | Backend (unidad) | Actualización existente devuelve "En curso"; id inexistente devuelve None. | Aprobado |
| CP-CB-03 | Backend (unidad) | Primera eliminación devuelve True; segunda e inexistente devuelven False. | Aprobado |
| CP-CB-04 | Frontend (unidad) | Ramas de vacío, espacios, 101 caracteres, error de API y alta válida cubiertas. | Aprobado |
| CP-CB-05 | Frontend (unidad) | Misma columna: 0 PATCH; movimiento válido: 1 PATCH; ids inválidos: sin PATCH. | Aprobado |

## Análisis de los resultados

No se produjeron fallas: los 25 casos obtuvieron el resultado esperado. En consecuencia, no se identificaron defectos funcionales y no se generaron identificadores `DEF-XX` para la Etapa 7.

Observaciones relevantes:

- **Validación del título:** la API rechazó correctamente los títulos vacíos, los compuestos solo por espacios y los de más de 100 caracteres. También normalizó los espacios externos y conservó caracteres acentuados y símbolos.
- **Estado inicial:** todas las tareas nuevas se crearon con estado "Pendiente", tanto por API como por interfaz.
- **Transiciones de estado:** se aceptaron únicamente los estados "Pendiente", "En curso" y "Terminada"; los valores fuera del conjunto fueron rechazados con HTTP 422.
- **Casos excepcionales:** las operaciones sobre identificadores inexistentes devolvieron HTTP 404; el identificador no numérico devolvió HTTP 422; el error HTTP 500 simulado en la API se mostró en la interfaz sin crear la tarjeta.
- **Persistencia:** las tareas y sus cambios se mantuvieron después de recargar la página y de volver a consultar la API.
- **Caja blanca:** se cubrieron las decisiones alcanzables de `validate_title`, `update_task_status` y `delete_task`, y las ramas de `handleSubmit` y `handleDrop`.

La rama `value is None` de `validate_title` no es alcanzable a través de Pydantic, porque el tipo `str` se valida antes de ejecutar el validador. Se mantiene documentada como defensa interna y no se considera un defecto.

Los casos CP-CB-04 y CP-CB-05 se diseñaron para aislar componentes del frontend, pero se ejecutaron sobre la interfaz real con Playwright. Esta adaptación permitió cubrir las mismas ramas de decisión y condiciones de `handleSubmit` y `handleDrop`, con la ventaja de verificar además la integración con la API. La diferencia se registra como una decisión de ejecución, no como un defecto.

## Defectos detectados

No se detectaron defectos durante la ejecución. El registro de defectos de la Etapa 7 quedará sin entradas `DEF-XX` originadas en esta etapa.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Log completo de ejecución | `docs/evidencias/etapa_6/ejecucion.log` |
| Resultados de los 15 casos de API | `docs/evidencias/etapa_6/resultados_api.json` |
| Resultados de los 5 casos de interfaz | `docs/evidencias/etapa_6/resultados_ui.json` |
| Resultados de los 5 casos de caja blanca | `docs/evidencias/etapa_6/resultados_caja_blanca.json` |
| Resumen consolidado | `docs/evidencias/etapa_6/resumen_resultados.json` |
| Capturas de interfaz | `docs/evidencias/etapa_6/screenshots/CP-UI-01.png` a `CP-UI-05.png` |
| Capturas de caja blanca de frontend | `docs/evidencias/etapa_6/screenshots/CP-CB-04.png` y `CP-CB-05.png` |
| Casos actualizados con resultados | `docs/Etapa_5.md` y `docs/casos_de_prueba.csv` |
| Scripts de ejecución | `scripts/etapa_6/` |

## Reproducibilidad

Los pasos generales para repetir la ejecución son:

1. Iniciar el backend con una base temporal: `KANBAN_DB_PATH=/tmp/kanban_etapa6.db .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` desde `backend/`.
2. Iniciar el frontend: `npm run dev` desde `frontend/`.
3. Ejecutar `scripts/etapa_6/ejecutar_api.py`, `scripts/etapa_6/ejecutar_ui.py` y `scripts/etapa_6/ejecutar_caja_blanca.py`.
4. Ejecutar `scripts/etapa_6/consolidar.py` y regenerar el CSV con `docs/casos_md_to_csv.py`.

## Conclusión de la etapa

Los 25 casos de prueba se ejecutaron correctamente y arrojaron un 100% de aprobación. El sistema cumple los requisitos RF1 a RF4, las restricciones de título y estado, y la persistencia de los cambios. No se detectaron defectos, por lo que la Etapa 7 se documentará sin defectos abiertos provenientes de la ejecución.

## Próxima etapa

La Etapa 7 consistirá en el registro y seguimiento de defectos. Como no se detectaron defectos en la ejecución, se dejará constancia del registro vacío y de las observaciones sobre la rama no alcanzable y la adaptación de los casos de caja blanca del frontend.
