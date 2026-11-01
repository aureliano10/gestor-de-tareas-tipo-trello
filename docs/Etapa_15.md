# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

# Etapa 15 - Informe técnico final

## 1. Portada

**Título del trabajo:** Tablero de Tareas Kanban — Informe técnico final de verificación y validación.

**Materia:** Verificación y Validación de Software.

**Curso:** 3° Año "TSDS".

**Institución:** Instituto de Educación Superior (Tecnicatura Superior en Desarrollo de Software).

**Fecha de entrega:** 01/11/2026.

**Repositorio:** proyecto `final_aimar` (backend FastAPI + SQLite y frontend React + Vite), gestionado con Git.

Este documento integra y resume el proceso completo de la Actividad Integradora: el análisis del problema y los requisitos (Etapa 1), el diseño y la planificación (Etapa 2), el desarrollo (Etapa 3), la verificación (Etapa 4), el diseño y la ejecución de pruebas (Etapas 5 y 6), el registro y seguimiento de defectos (Etapa 7), las pruebas unitarias, de integración y de sistema (Etapas 8, 9 y 10), la automatización (Etapa 11), el TDD y la refactorización (Etapa 12), las pruebas de regresión (Etapa 13) y la revisión de artefactos no código (Etapa 14).

## 2. Integrantes

| Integrante | Rol principal |
|------------|---------------|
| Aureliano Eichhorn | Diseño de la base de datos (SQLite), desarrollo de la API REST (FastAPI) con reglas de negocio, validaciones y manejo de errores, y scripts de ejecución de pruebas sobre la API. |
| Nicolás Delfino | Desarrollo de la interfaz gráfica (React), conexión con la API, interacciones del tablero (arrastre, edición, checklist, adjuntos y deshacer) y pruebas de interfaz. |

Ambos integrantes revisaron el código del otro antes de darlo por terminado y diseñaron y revisaron juntos los casos de prueba.

> Nota: los nombres figuran en `docs/Etapa_1.md` y `docs/Etapa_2.md`. Si el grupo cambia su conformación, debe actualizarlos antes de la entrega definitiva.

## 3. Descripción del problema

El equipo de trabajo necesitaba una herramienta para **organizar, gestionar y hacer seguimiento visual** del estado de distintas tareas mediante un tablero ágil e intuitivo (estilo Kanban), donde además de mover una actividad entre estados se pudiera detallar su contenido, controlar su avance y conservar la documentación asociada.

**Usuarios del sistema:** estudiantes, profesionales independientes y equipos pequeños que necesiten organizar su flujo de trabajo diario.

**Necesidades detectadas:** registrar y editar actividades, hacer seguimiento del avance mediante un checklist, asociar documentación (archivos y enlaces), clasificar las tareas (prioridad, responsable, etiquetas), conservar un historial de cambios y encontrar las tareas rápido (búsqueda, filtros y orden). Ver `docs/Etapa_1.md`.

## 4. Objetivos

**Objetivo general.** Desarrollar un pequeño sistema gestor de tareas tipo Kanban que permita registrar y editar actividades, hacer seguimiento de su avance mediante un checklist, asociarles documentación y cambiar su estado desplazándolas entre columnas.

**Objetivos específicos:**

1. Implementar las funcionalidades definidas en la Etapa 1 y los requisitos funcionales RF1 a RF23.
2. Aplicar una estrategia de verificación y validación que cubra caja negra, caja blanca, pruebas unitarias, de integración y de sistema.
3. Automatizar la batería de pruebas y dejar evidencias reproducibles de cada ejecución.
4. Detectar, registrar y corregir los defectos del sistema y de los artefactos.
5. Determinar, con evidencia, si el producto satisface las necesidades planteadas al inicio.

## 5. Requisitos

La especificación incluye 23 requisitos funcionales y un conjunto de restricciones, definidos en `docs/Etapa_1.md` y ampliados en `docs/Etapa_2.md`.

**Requisitos funcionales (RF1 a RF23):** registrar tarea (RF1), estado inicial "Pendiente" (RF2), actualizar estado (RF3), reordenar dentro de la columna (RF4), editar tarea (RF5), registrar subtareas (RF6), marcar/desmarcar subtareas (RF7), eliminar subtareas (RF8), impedir finalizar con subtareas pendientes (RF9), fecha límite y vencimiento (RF10), adjuntar archivos (RF11), descargar adjuntos (RF12), eliminar adjuntos (RF13), eliminar tarea (RF14), recuperar tarea (RF15), prioridad (RF16), responsable (RF17), etiquetas (RF18), enlaces (RF19), historial de actividad (RF20), búsqueda y filtros (RF21), orden del listado (RF22) y alta enriquecida (RF23).

**Restricciones principales:**

| Aspecto | Restricción |
|---------|-------------|
| Título | Obligatorio, no vacío ni solo espacios; máximo 100 caracteres. |
| Descripción | Máximo 500 caracteres; opcional. |
| Estados | Solo `Pendiente`, `En curso` o `Terminada`. |
| Finalización | Una tarea no puede pasar a `Terminada` con subtareas pendientes. |
| Fecha límite | No puede ser anterior a hoy al crear; al editar sí se admite una fecha pasada. |
| Adjuntos | Hasta 3 por tarea, de 5 MB como máximo, extensiones `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.docx`. |
| Prioridad | `Baja`, `Media` o `Alta`; por defecto `Media`. |
| Responsable | Opcional; máximo 60 caracteres. |
| Etiquetas | Hasta 5 por tarea, de hasta 30 caracteres, reutilizables y sin distinguir mayúsculas. |
| Enlaces | Hasta 5 por tarea; URL `http://` o `https://` de hasta 500 caracteres, sin duplicados, nombre opcional de hasta 60. |
| Subtareas en el alta | Hasta 20. |
| Historial | Automático; devuelve las últimas 20 acciones, de la más reciente a la más antigua. |

## 6. Descripción del sistema

El sistema es un **tablero Kanban** con tres columnas fijas (`Pendiente`, `En curso`, `Terminada`). Cada tarea se representa con una tarjeta arrastrable entre columnas y reordenable dentro de la misma columna; al abrir su detalle se editan sus datos, se gestiona el checklist de subtareas y se administran los adjuntos.

**Arquitectura.** Dos aplicaciones independientes comunicadas por HTTP:

- **Backend (API REST)** con Python y FastAPI: expone los endpoints de tareas, subtareas, adjuntos y etiquetas, aplica validaciones y reglas de negocio, y persiste en SQLite y en disco.
- **Frontend (interfaz)** con React: consume la API mediante `fetch` y presenta el tablero.

Dentro del backend, el código se organiza en capas con una única dirección de dependencia: `routers` (HTTP) → `schemas` (validación) → `repository` (reglas de negocio y datos) → `database` (conexión y esquema). La comunicación frontend–backend se resuelve con un proxy de desarrollo de Vite hacia `/api` y CORS habilitado para el origen del frontend. Ver `docs/Etapa_3.md`.

**Modelo de datos (SQLite).** Siete tablas: `tasks` (con `priority`, `assignee`, `due_date`, `position`, `deleted_at`), `subtasks`, `attachments`, `tags`, `task_tags` (clave primaria compuesta), `links` y `activity`. Todas las relaciones hacia `tasks` usan `ON DELETE CASCADE`. El estado `overdue` no se almacena: se calcula en cada respuesta. La base aplica restricciones `CHECK` como última barrera de integridad.

**API principal:** `GET /api/health`, `GET /api/tasks` (con filtros `q`, `priority`, `tag`, `overdue` y orden `sort`), `POST /api/tasks`, `PUT /api/tasks/{id}`, `PATCH /api/tasks/{id}/move`, `DELETE /api/tasks/{id}`, `POST /api/tasks/{id}/restore`, `GET /api/tags`, endpoints de subtareas y de adjuntos. Ver el detalle completo en `docs/Etapa_3.md` y `README.md`.

**Manejo de errores:** HTTP 422 para datos inválidos, 404 para recursos inexistentes, 409 para reglas de negocio (límites y bloqueo de finalización), 413 para adjuntos grandes y 415 para extensiones no permitidas.

## 7. Tecnologías utilizadas

| Capa | Tecnología | Uso |
|------|-----------|-----|
| Frontend | React 19 + JavaScript + CSS (Vite 8) | Interfaz del tablero y comunicación con la API. |
| Backend | Python 3.12, FastAPI 0.136.3, Pydantic 2.13.4 | API REST, validaciones y reglas de negocio. |
| Base de datos | SQLite 3.45.1 | Persistencia, con restricciones `CHECK` y claves foráneas en cascada. |
| Servidor | Uvicorn 0.49.0 | Servidor ASGI para el desarrollo. |
| Pruebas | pytest 9.2.0, httpx 0.28.1, Playwright 1.64.1 | Unitarias, integración, API y interfaz. |
| Análisis estático | Ruff 0.17.3, ESLint 9.39.5, `compileall` | Calidad y estilo del backend y del frontend. |
| Empaquetado | Vite build 8.3.5, `npm`, `pip` | Compilación y dependencias. |
| Entorno | Visual Studio Code, Linux Mint 22.3, Node.js v24.14.1, Google Chrome 151 | Desarrollo y ejecución. |
| Control de versiones | Git (repositorio local + GitHub) | Trazabilidad de los avances. |

## 8. Planificación

**Responsabilidades.** Aureliano Eichhorn: base de datos, API REST, reglas de negocio y scripts de prueba de API. Nicolás Delfino: interfaz React, interacciones del tablero y pruebas de interfaz. El diseño de casos de prueba y las revisiones cruzadas de código se hicieron en conjunto.

**Organización.** El trabajo se dividió por capas (backend y frontend) con revisión cruzada. La documentación de cada etapa se cierra con un commit identificable, lo que permite trazar los avances. **Desviación registrada:** la Etapa 2 preveía ramas separadas por integrante, pero el trabajo se realizó sobre `main` con una convención de commits por etapa (hallazgo VER-08, aceptado y documentado en `docs/Etapa_4.md`).

**Tecnologías y entorno.** Definidas en la Sección 7.

**Repositorio.** Git local con remoto en GitHub; `main` como rama de trabajo.

**Estrategia de pruebas (planificada en Etapa 2).** Estrategia **de abajo hacia arriba**: primero la API (lógica y persistencia de forma aislada) y luego la interfaz, complementando con análisis estático y revisión del manejo de errores. Tipos previstos: unitarias, integración, caja blanca, caja negra y sistema. Herramientas previstas: Ruff, `compileall`, ESLint, Vite build, httpx y Playwright.

## 9. Desarrollo

Se implementaron las **15 funcionalidades** definidas en la Etapa 2, agrupadas en 8 funcionalidades base (Etapa 3) y ampliadas con prioridad, responsable, etiquetas, enlaces, historial de actividad, búsqueda/filtros/orden y alta enriquecida. Todas operan tanto en la API como en la interfaz.

**Decisiones de diseño relevantes:**

- **Capas con una sola dirección de dependencia** (`routers → schemas → repository → database`) para aislar responsabilidades y poder probar cada parte por separado.
- **El backend es la fuente de verdad** de las validaciones (la API puede usarse sin interfaz); el frontend valida antes de enviar para dar respuesta inmediata y la base aplica `CHECK` como última barrera.
- **Borrado lógico** (`deleted_at`) para permitir el "deshacer" en la restauración.
- **`overdue` calculado**, nunca almacenado, comparando la fecha límite con la actual y verificando que la tarea no esté terminada.
- **Migración aditiva** del esquema (`ALTER TABLE ... ADD COLUMN` y `CREATE TABLE IF NOT EXISTS`), sin recrear tablas ni romper claves foráneas.
- **Cambios internos sin tocar la API pública ni el modelo de datos** en TDD/refactorización (Etapa 12).

**Control de versiones.** Git con commits por etapa sobre `main`. La secuencia de entregables es trazable: estructura inicial, backend, frontend, documentación (Etapa 3) y luego un commit por etapa de verificación, defectos, pruebas y automatización. Ver `docs/Etapa_3.md`.

**Evidencia de funcionamiento (Etapa 3):** creación, edición, movimiento, checklist, adjuntos, eliminación/restauración y errores previstos verificados contra la API en ejecución, además de la compilación del frontend (`vite build`).

## 10. Estrategia de verificación y validación

La estrategia distingue **verificación** (¿se está construyendo bien el producto?) de **validación** (¿se construyó el producto correcto?).

**Verificación (durante el desarrollo).** Revisión de requisitos, coherencia entre diseño e implementación, revisión de código del backend y del frontend, revisión de documentación y **análisis estático** (Ruff, `compileall`, ESLint, Vite build). Se detallaron en `docs/Etapa_4.md` con 10 hallazgos (VER-01 a VER-10); 9 corregidos y 1 aceptado (desviación de ramas). Entre las correcciones: restricciones `CHECK` en la base, reapertura automática de tareas, eliminación de duplicaciones de límites, comportamiento de la tecla Escape y de la etiqueta de vencimiento, y actualización de la documentación.

**Validación (al finalizar el desarrollo).** Evaluación del sistema de punta a punta simulando escenarios de uso real, con backend y frontend en funcionamiento conjunto, para comprobar el objetivo de ser una herramienta "ágil e intuitiva" para el seguimiento visual de actividades (`docs/Etapa_10.md`).

**Niveles aplicados:** caja negra (clases de equivalencia y valores límite), caja blanca (instrucciones, decisiones, condiciones y caminos), unitarias, integración, sistema, regresión y revisión de artefactos no código. La estrategia general es **bottom-up**: la base (unidades) se verifica antes que la integración y el sistema.

## 11. Casos de prueba

El diseño de casos está documentado en `docs/Etapa_5.md` y volcado en `docs/casos_de_prueba.csv`. Se diseñaron, en total, **80 casos de sistema** (62 de API + 11 de interfaz + 7 de caja blanca), más **18 casos unitarios** (Etapa 8), **6 casos de integración** (Etapa 9) y **1 caso** de TDD (Etapa 12, `CP-UN-19`).

| Conjunto | Cantidad | Documento |
|----------|----------|-----------|
| Casos de sistema (API + UI + caja blanca) | 80 | `docs/Etapa_5.md` |
| Casos unitarios (pytest) | 18 | `docs/Etapa_8.md` |
| Casos de integración (pytest + TestClient) | 6 | `docs/Etapa_9.md` |
| Caso de TDD (`CP-UN-19`) | 1 | `docs/Etapa_12.md` |
| **Total backend automatizado (unitarias + integración + TDD)** | **25** | — |

> \* El caso de TDD se suma a los 18 unitarios y da 19 unitarios en el total backend.

**Metodología de las fichas.** Cada caso se documenta con una ficha uniforme de campos:

| Campo | Contenido |
|-------|-----------|
| ID | Identificador único (p. ej. `CP-CRE-01`, `CP-UN-02`, `CP-IN-03`). |
| Funcionalidad | Funcionalidad evaluada. |
| Objetivo | Qué se quiere comprobar. |
| Precondiciones | Estado previo necesario. |
| Datos de entrada | Valores concretos usados. |
| Procedimiento | Pasos deterministas a ejecutar. |
| Resultado esperado | Comportamiento correcto según los requisitos. |
| Resultado obtenido | Lo observado en la ejecución. |
| Estado | Aprobado / Fallido. |
| Observaciones y técnica | Técnica aplicada y notas. |

Cada caso evalúa una sola situación y tiene un identificador único. Los datos válidos e inválidos se derivan de los requisitos y restricciones de la Etapa 1.

## 12. Pruebas de caja negra

Se aplicaron **clases de equivalencia** y **análisis de valores límite**, sobre datos válidos, inválidos y de borde, tanto en la API como en la interfaz. Detalle en `docs/Etapa_5.md` (diseño) y `docs/Etapa_6.md` (ejecución).

**Clases de equivalencia (muestra).** Título: válido (1–100 caracteres tras normalizar), vacío, solo espacios y >100; descripción: hasta 500 y >500; fecha: hoy o posterior y anterior a hoy (rechazada al crear, admitida al editar); estado: dentro/fuera del conjunto permitido; posición: ≥0 y negativa; identificador: existente, inexistente y no numérico; adjunto: extensión permitida/no, tamaño ≤5 MB/>5 MB y cantidad ≤3/>3; prioridad, responsable, etiqueta, enlace y criterio de orden: clase válida e inválida.

**Valores límite (muestra).** Título de 1, 100 y 101 caracteres; descripción de 500 y 501; fecha de hoy y de ayer; posición 0 y −1; adjunto de 5 MB y 5 MB + 1 byte; 3 y 4 adjuntos; responsable de 60 y 61; 5 y 6 etiquetas; 5 y 6 enlaces; 20 y 21 subtareas en el alta; 20 entradas de historial.

**Ejemplos de resultados obtenidos (`docs/Etapa_6.md`):**

| Caso | Resultado |
|------|-----------|
| `CP-CRE-03` Título de 100 caracteres | HTTP 201 (aceptado). |
| `CP-CRE-04` Título de 101 caracteres | HTTP 422 (rechazado). |
| `CP-CRE-05`/`CP-CRE-06` Título vacío / solo espacios | HTTP 422. |
| `CP-CRE-09` Fecha pasada al crear | HTTP 422. |
| `CP-ADJ-04` Extensión no permitida | HTTP 415. |
| `CP-ADJ-05` Adjunto >5 MB | HTTP 413. |
| `CP-ADJ-06` Cuarto adjunto | HTTP 409 (conserva 3). |
| `CP-ASG-02` Responsable de 61 caracteres | HTTP 422. |
| `CP-TAG-02`/`CP-ENL-03` 6 etiquetas / 6 enlaces | HTTP 409. |

## 13. Pruebas de caja blanca

Se analizaron **instrucciones, decisiones, condiciones y caminos** sobre unidades seleccionadas del backend y del frontend, con **7 casos** (`CP-CB-01` a `CP-CB-07`). Detalle en `docs/Etapa_5.md`.

**Unidades analizadas.** `clean_title` y `move_task`, `delete_task`/`restore_task`, `create_attachment`, `update_subtask` (backend) y `validateTaskInput`/`handleSubmit`, `dropIndex`/`handleDrop` (frontend).

| Caso | Unidad | Decisiones/condiciones cubiertas |
|------|--------|----------------------------------|
| CP-CB-01 | `clean_title` | Válido, vacío, solo espacios, 101 caracteres y `None` (rama defensiva no alcanzable desde la API). |
| CP-CB-02 | `move_task` | Existente/inexistente; `pending > 0` (bloqueo) y `pending == 0` (movimiento). |
| CP-CB-03 | `delete_task`/`restore_task` | Existente/inexistente; restauración válida e inválida. |
| CP-CB-04 | `create_attachment` | `total >= 3` (límite) y `total < 3` (alta). |
| CP-CB-05 | `update_subtask` | Condición compuesta `not done and status == Terminada` (los dos resultados). |
| CP-CB-06 | `validateTaskInput`/`handleSubmit` | Vacío, solo espacios, 101 y 501 caracteres, error de API y alta válida. |
| CP-CB-07 | `dropIndex`/`handleDrop` | Identificador inválido, misma columna y columna distinta. |

**Cobertura:** 100% de las decisiones alcanzables de las unidades listadas y 100% de las condiciones compuestas evaluadas. La rama `value is None` de `clean_title` se documenta como defensa interna no alcanzable a través de Pydantic (no es un defecto). Los casos de caja blanca del frontend (`CP-CB-06` y `CP-CB-07`) se ejecutaron sobre la interfaz real con Playwright, cubriendo las mismas ramas y la integración con la API.

## 14. Pruebas unitarias

Se implementaron **18 pruebas unitarias automatizadas** con **pytest** sobre **16 funciones o métodos** de las capas de validación, datos y persistencia (`docs/Etapa_8.md`). Luego se agregó el caso de TDD (`CP-UN-19`), con lo que el total unitario pasó a **19**.

| Métrica | Valor |
|---------|-------|
| Funciones o métodos con pruebas | 16 |
| Casos unitarios iniciales (Etapa 8) | 18 |
| Caso agregado por TDD (Etapa 12) | 1 |
| Total unitario tras la Etapa 12 | 19 |
| Aprobados (Etapa 8) | 18/18 |

**Funciones cubiertas:** `clean_title`, `clean_description`, `clean_priority`, `clean_assignee`, `clean_tag`, `clean_tags`, `clean_link_url`, `clean_link_label`, `_resolve_tag_id`, `_set_tags`, `_normalize_links`, `create_task`, `move_task`, `create_attachment`, `init_db`/`_needs_migration` y `connection`.

**Aislamiento.** Cada prueba crea su propia base SQLite y almacenamiento temporales con `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH` (fixture `unit_db`), sin depender de un servidor. Ubicación de las pruebas: `backend/tests/` (`test_unit_schemas.py`, `test_unit_repository.py`, `test_unit_database.py` y `test_unit_overdue.py`). Salida real de la corrida: `18 passed` (Etapa 8) y `25 passed` en la suite backend completa tras la Etapa 12.

## 15. Pruebas de integración

Se implementaron **6 pruebas de integración** con **pytest + `TestClient` de FastAPI**, sobre la funcionalidad *"alta de tarea enriquecida → persistencia → lectura con filtros y orden → flujo de estados con reglas de negocio"* (`docs/Etapa_9.md`).

**Componentes que interactúan:** `routers` (tareas, subtareas, adjuntos) → `schemas` → `repository` → `database` (SQLite y almacenamiento en disco).

**Estrategia:** **bottom-up**, apoyándose en las unidades ya verificadas en la Etapa 8 y ejercitando el stack HTTP real mediante `TestClient` (que dispara el ciclo de vida e inicializa el esquema), con base y almacenamiento temporales por prueba.

| Caso | Integración verificada |
|------|------------------------|
| CP-IN-01 | Alta enriquecida (subtareas, etiquetas, enlaces) → validación → persistencia → relectura. |
| CP-IN-02 | Subida de adjunto → escritura en disco → descarga íntegra. |
| CP-IN-03 | Flujo Pendiente → En curso → Terminada con bloqueo de finalización (409). |
| CP-IN-04 | Reapertura automática al agregar una subtarea pendiente a una tarea terminada. |
| CP-IN-05 | Lectura con filtros (prioridad, etiqueta, vencimiento, texto) y orden (prioridad, fecha). |
| CP-IN-06 | Historial de actividad, con la entrada más reciente primero. |

Resultado: `6 passed, 1 warning in 1.04s` (el aviso es un `StarletteDeprecationWarning` del `TestClient` y no afecta el resultado).

## 16. Pruebas de sistema

Se ejecutaron las pruebas sobre el **sistema integrado** (backend real en `http://127.0.0.1:8000` y frontend real en `http://127.0.0.1:5173`), reutilizando la suite reproducible de `scripts/etapa_6/` (`docs/Etapa_10.md`).

| Grupo | Casos | Aprobados | Fallidos | Resultado |
|-------|-------|-----------|----------|-----------|
| API (`httpx`) | 62 | 62 | 0 | 100% aprobado |
| Interfaz (Playwright) | 11 | 11 | 0 | 100% aprobado |
| Caja blanca | 7 | 7 | 0 | 100% aprobado |
| **Total** | **80** | **80** | **0** | **100% aprobado** |

Se cubrieron datos válidos, inválidos, de borde y situaciones excepcionales (error de red simulado, arrastres con identificadores inválidos, operaciones sobre recursos inexistentes y superación de límites). El comportamiento frente a errores se verificó en tres planos (interfaz, API y base).

**Matriz de trazabilidad RF1 a RF23.** Los 23 requisitos funcionales quedan cubiertos por al menos un caso aprobado (casos de sistema + unitarios + integración); no hay requisitos sin cobertura. La matriz completa figura en `docs/Etapa_10.md`.

| Métrica | Valor |
|---------|-------|
| Requisitos funcionales (RF1–RF23) | 23 |
| Requisitos cubiertos por al menos un caso aprobado | 23 |
| Requisitos sin cobertura | 0 |
| Casos de sistema ejecutados | 80 (todos aprobados) |
| Casos automatizados complementarios (Etapas 8 y 9) | 24 (todos aprobados) |
| Total de casos considerados | 104 |

**Conclusión de validación (Etapa 10):** *sí, el sistema desarrollado satisface las necesidades planteadas.* Se justifica por la cobertura total de requisitos, el funcionamiento verificado de las funcionalidades principales, el manejo controlado de errores, la interacción consistente entre funcionalidades y el 100% de aprobación de la suite.

## 17. Automatización

La automatización se construyó de forma incremental (Etapas 8, 9 y 10) y se consolidó en la Etapa 11 (`docs/Etapa_11.md`). Supera ampliamente el mínimo de tres casos exigido: se automatizaron **104 casos**, todos aprobados.

**Herramientas y casos automatizados:**

| Conjunto | Herramienta | Casos | Aprobados |
|----------|-------------|-------|-----------|
| Pruebas unitarias | pytest | 18 | 18 |
| Pruebas de integración | pytest + `TestClient` | 6 | 6 |
| Casos de API | httpx | 62 | 62 |
| Casos de interfaz | Playwright (Chrome headless) | 11 | 11 |
| Casos de caja blanca | Runner propio (invocación directa + Playwright) | 7 | 7 |
| **Total** | — | **104** | **104** |

**Marco de automatización:** pruebas automatizadas en `backend/tests/`; suite de sistema en `scripts/etapa_6/`; runners de evidencias en `scripts/etapa_8/` y `scripts/etapa_9/`. Elementos comunes: aislamiento por prueba (variables de entorno con rutas temporales), resultados en texto y JSON y comandos reejecutables.

**Ventajas:** reproducibilidad total; detección temprana y red de seguridad ante cambios; cobertura de los tres planos (lógica pura, contrato HTTP e interfaz real); aislamiento entre casos; evidencia trazable (JSON por caso); verificación de las peticiones de red de la interfaz.

**Limitaciones:** la suite de sistema depende del entorno (backend en 8000, frontend en 5173 y Chrome instalado); las pruebas de interfaz son más lentas y sensibles a la sincronización con React; los selectores `data-testid` obligan a mantener los localizadores; los identificadores de tarea cambian entre corridas; dos casos de caja blanca del frontend se ejecutan sobre la interfaz real.

## 18. TDD y refactorización

Se aplicó TDD de punta a punta y una refactorización sobre lógica interna, **sin modificar la API pública ni el modelo de datos** (`docs/Etapa_12.md`).

**TDD sobre el helper `is_overdue(due_date, status, today)`** (regla: vencida si la fecha límite es anterior a hoy y el estado no es "Terminada"):

1. **RED:** se escribió primero la prueba `test_cp_un_19_is_overdue_regla_de_vencimiento`, que falló al importar el helper inexistente (`ImportError: cannot import name 'is_overdue'`).
2. **GREEN:** se implementó lo mínimo para pasar la prueba, con la fecha de referencia inyectable.
3. **REFACTOR:** se adoptó el helper en `_task_dict`, reemplazando la expresión en línea por `is_overdue(due_date, row["status"])`, de modo que la regla queda definida en un solo lugar y con sus propias pruebas.

**Refactorización de `update_task`.** El problema era la **duplicación** de la lógica que calcula las etiquetas/enlaces quitados y agregados para el historial (dos ramas casi idénticas con cuatro bucles). Se extrajo el helper único **`_log_set_changes`**, que recibe los conjuntos anterior y nuevo (como pares `clave, texto`) y dos plantillas de mensaje. Beneficios: eliminación de la duplicación, mayor cohesión de `update_task`, mejor legibilidad y mantenimiento en un solo lugar. Los mensajes del historial se mantuvieron **idénticos**, por lo que el comportamiento observable no cambió.

**Verificación.** La suite completa pasó de 24 a **25 casos aprobados** (`25 passed`), y `ruff check backend scripts` no arrojó observaciones.

## 19. Pruebas de regresión

Tras los cambios de la Etapa 12 se reejecutó la batería completa para comprobar que no se afectaran funcionalidades que antes funcionaban (`docs/Etapa_13.md`).

**Línea base (antes del cambio):** 24/24 en el backend (18 unitarias + 6 de integración) y 80/80 en la suite de sistema → **104/104**.

**Cambios sobre los que se hizo la regresión:** (1) helper nuevo `is_overdue` adoptado en `_task_dict` (afecta el vencimiento y el filtro `overdue`); (2) extracción de `_log_set_changes` en `update_task` (afecta el historial de etiquetas y enlaces). Ambos tocan rutas de RF3, RF4, RF5, RF10, RF18, RF19, RF20, RF21 y RF22.

**Batería reejecutada y resultados:**

| Conjunto | Antes | Después | Fallidos | Veredicto |
|----------|-------|---------|----------|-----------|
| Backend (pytest) | 24/24 | 25/25 | 0 | Sin regresiones |
| Sistema (API + UI + caja blanca) | 80/80 | 80/80 | 0 | Sin regresiones |
| **Total** | **104/104** | **105/105** | **0** | **Sin regresiones** |

El único cambio en el conteo es la suma del caso nuevo de TDD (`CP-UN-19`). Los casos relacionados con los cambios (`CP-IN-05`, `CP-FEC-01/02`, `CP-ORD-01/02`, `CP-TAG-04`, `CP-IN-06`, `CP-HIS-01/02`) se comportaron igual que en la línea base.

## 20. Defectos encontrados

Se registraron **4 defectos** con ficha uniforme (ID, fecha, descripción, funcionalidad afectada, pasos, resultado esperado/obtenido, evidencia, severidad, prioridad, estado, causa raíz, corrección y fecha de cierre). Detalle en `docs/Etapa_7.md`.

| ID | Fecha | Funcionalidad afectada | Severidad | Prioridad | Estado |
|----|-------|------------------------|-----------|-----------|--------|
| DEF-01 | 30/10/2026 | Alta de subtareas y adjuntos (backend) | Alta | Alta | Verificado |
| DEF-02 | 30/10/2026 | Alta de tarea desde la interfaz (estilo) | Baja | Media | Verificado |
| DEF-03 | 01/11/2026 | Caso de prueba de interfaz `CP-UI-09` | Baja | Baja | Verificado |
| DEF-04 | 01/11/2026 | Scripts de prueba de la Etapa 6 | Baja | Baja | Verificado |

**Resumen de causas raíz y correcciones:**

- **DEF-01 (Alta):** la migración `_migrate_tasks` recreaba `tasks` con `ALTER TABLE tasks RENAME TO tasks_legacy`; al renombrar, SQLite reescribía las claves foráneas de `subtasks` y `attachments` y, al eliminar la tabla temporal con `DROP`, los `INSERT` fallaban con HTTP 500 (`OperationalError: no such table: main.tasks_legacy`). Se corrigió con una **migración aditiva** (`ALTER TABLE ... ADD COLUMN` y detección por columnas), sin renombrar ni recrear la tabla.
- **DEF-02 (Baja):** el `<button type="submit">` de `TaskForm.jsx` no tenía `className`, por lo que se veía sin el estilo primario. Se agregó `className="btn"`.
- **DEF-03 (Baja):** el caso `CP-UI-09` fallaba por un locator compuesto mal construido en el script (timeout de Playwright), no por el sistema. Se corrigió usando el helper `task_in`.
- **DEF-04 (Baja):** líneas que excedían el límite de longitud de Ruff en `scripts/etapa_6/`. Se ajustaron las líneas (commit `c60e4ef`).

Además, la verificación de la Etapa 4 registró 10 hallazgos (VER-01 a VER-10) y la revisión de artefactos de la Etapa 14 detectó 7 problemas (PRB-01 a PRB-07), que se detallan en las Secciones 10 y 22.

## 21. Seguimiento de defectos

Se utilizó un **ciclo de vida** de estados (Nuevo → En análisis → En corrección → Resuelto → Verificado) y criterios de severidad (Alta/Media/Baja) y prioridad (Alta/Media/Baja). El seguimiento se centralizó en la Etapa 7 aunque los defectos se originaron en distintas etapas.

| ID | Nuevo | En análisis | En corrección | Resuelto | Verificado |
|----|-------|-------------|---------------|----------|------------|
| DEF-01 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 01/11/2026 |
| DEF-02 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 01/11/2026 |
| DEF-03 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 |
| DEF-04 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 |

**Método de seguimiento y comprobación.** Cada corrección se verificó con casos de prueba que hoy pasan: DEF-01 con `CP-SUB-01`/`CP-SUB-04` y `CP-ADJ-01` a `CP-ADJ-06`/`CP-CB-04`; DEF-02 con `CP-UI-01` y `CP-UI-09`; DEF-03 con `CP-UI-09` y el registro `insignia='Alta'; responsable='Ana'`; DEF-04 con la corrida completa sin avisos de estilo.

**Métricas finales:** 4 defectos registrados, 4 resueltos, 4 verificados y **0 abiertos**. Por severidad: 1 Alta y 3 Baja. Por origen: 1 backend (datos/esquema), 1 frontend (estilo) y 2 scripts de prueba. La corrida del 01/11/2026 ejecutó los 80 casos de sistema con 100% de aprobación, confirmando que las correcciones no introdujeron regresiones.

## 22. Revisión de artefactos no código

Se revisaron, mediante **inspección cruzada (desk check)**, tres artefactos no código: `README.md`, `COMANDOS_BACKEND.md` y `backend/requirements-dev.txt` (`docs/Etapa_14.md`). Se detectaron y corrigieron **7 problemas** (2 de severidad Alta, 3 Media y 2 Baja).

| ID | Artefacto | Problema | Severidad | Corrección |
|----|-----------|----------|-----------|------------|
| PRB-01 | `README.md` | Comando de lint incompleto (`ruff check backend` no cubría `scripts/`). | Media | Se cambió a `ruff check backend scripts`. |
| PRB-02 | `README.md` | Estructura del proyecto desactualizada (faltaban `scripts/etapa_8/` y `scripts/etapa_9/`). | Baja | Se agregaron las carpetas faltantes. |
| PRB-03 | `README.md` | Faltaban instrucciones para ejecutar las pruebas automatizadas. | Alta | Se agregó la sección "Pruebas". |
| PRB-04 | `README.md` | Arranque del backend inconsistente con `COMANDOS_BACKEND.md` (no mencionaba `run_backend.sh`). | Media | Se alineó con el script y se aclaró la forma manual. |
| PRB-05 | `COMANDOS_BACKEND.md` | No explicaba cómo instalar dependencias de desarrollo ni ejecutar pruebas. | Media | Se agregó la sección "5. Ejecutar las pruebas". |
| PRB-06 | `backend/requirements-dev.txt` | Dependencias de prueba (pytest, httpx, playwright) sin declarar. | Alta | Se declararon `pytest==9.2.0`, `httpx==0.28.1`, `playwright==1.64.1`. |
| PRB-07 | `COMANDOS_BACKEND.md` | Falta de ortografía ("no te olvidés" → "no te olvides"). | Baja | Se corrigió la forma verbal. |

Las correcciones se validaron ejecutando los comandos documentados: `pip install -r backend/requirements-dev.txt` (éxito), `ruff check backend scripts` (`All checks passed!`) y `pytest backend/tests -v` (`25 passed`). No se modificó ningún artefacto de código.

## 23. Resultados

Resumen global de todos los conjuntos de prueba ejecutados sobre el sistema, con sus totales reales:

| Tipo de prueba | Casos | Aprobados | Fallidos | Resultado |
|----------------|-------|-----------|----------|-----------|
| Caja negra (API + interfaz) | 73 | 73 | 0 | 100% aprobado |
| Caja blanca | 7 | 7 | 0 | 100% aprobado |
| Unitarias (pytest) | 19 | 19 | 0 | 100% aprobado |
| Integración (pytest + TestClient) | 6 | 6 | 0 | 100% aprobado |
| Sistema (API 62 + UI 11 + caja blanca 7) | 80 | 80 | 0 | 100% aprobado |
| Automatización (total consolidado) | 104 | 104 | 0 | 100% aprobado |
| Regresión (con el caso nuevo de TDD) | 105 | 105 | 0 | Sin regresiones |

> Lectura de los totales: los 80 casos de sistema se descomponen en 73 de caja negra (62 de API + 11 de interfaz) y 7 de caja blanca. Los 104 casos automatizados agrupan 18 unitarios iniciales + 6 de integración + 80 de sistema. Tras la Etapa 12, la suite backend queda en 19 unitarios (18 + `CP-UN-19`) y el total con regresión en 105. No hubo casos fallidos en ninguna corrida y no quedaron defectos abiertos.

**Cobertura de requisitos:** 23/23 requisitos funcionales (RF1 a RF23) cubiertos por al menos un caso aprobado; 0 sin cobertura.

## 24. Conclusiones

**¿El sistema satisface las necesidades planteadas?** **Sí.** El tablero Kanban cumple con los requisitos RF1 a RF23 y con las restricciones definidas al inicio, según lo demuestran las 104 ejecuciones aprobadas de la suite de validación (y 105 tras la regresión) y la matriz de trazabilidad de la Etapa 10, que no deja requisitos sin cobertura. Las funcionalidades centrales funcionaron de punta a punta sobre el sistema integrado, el manejo de errores fue controlado y la interacción entre funcionalidades resultó consistente.

**Qué se aprendió del proceso de V&V:**

- La **separación en capas** facilita la verificación: permitió probar unidades, integrar el stack y validar el sistema completo con la misma estrategia **bottom-up**.
- La **verificación temprana** (Etapa 4) se justificó sola: el análisis estático no detectó problemas, pero la inspección manual y la revisión de consistencia entre capas encontraron 10 hallazgos, incluido DEF-01 (severidad Alta), que solo se manifiesta al reutilizar una base con el esquema anterior.
- La **automatización** es la que sostiene el proceso: pytest, httpx y Playwright dieron una red de seguridad reproducible que permitió refactorizar y hacer TDD sin miedo y detectar regresiones de inmediato.
- La **trazabilidad** requisito → caso → evidencia es lo que convierte las pruebas en una herramienta de decisión, no en una lista de resultados.
- Los **defectos no solo están en el código**: la revisión de artefactos no código (Etapa 14) detectó que las dependencias de prueba no estaban declaradas, lo que habría roto la reproducibilidad en una clonación limpia.

**Limitaciones:** el movimiento de tarjetas depende del arrastre (sin alternativa por teclado, OBS-01); la carga de adjuntos lee el archivo completo en memoria antes de validar el tamaño (OBS-02, aceptable con 5 MB); al eliminar una tarea el archivo del adjunto permanece en disco por el borrado lógico (OBS-03); la suite de sistema depende del entorno (backend, frontend y Chrome) y es más lenta que las pruebas de API; y quedan fuera del alcance la autenticación y la colaboración en tiempo real.

**Trabajos futuros:** agregar autenticación y colaboración en tiempo real; ofrecer una alternativa por teclado al arrastre (accesibilidad); ampliar la cobertura de navegadores en Playwright; persistir el archivo adjunto de otra forma para el modo deshacer; e incorporar métricas de cobertura de código en la integración continua.

## 25. Bibliografía y fuentes consultadas

**Consigna de la cátedra:**

- `ACTIVIDAD_INTEGRADORA_2026.pdf` — consigna de la Actividad Integradora de Verificación y Validación de Software, 3° Año TSDS (repositorio del proyecto).

**Documentación de las tecnologías utilizadas:**

- FastAPI — https://fastapi.tiangolo.com/
- Starlette (TestClient) — https://www.starlette.io/testclient/
- Pydantic — https://docs.pydantic.dev/
- Uvicorn — https://www.uvicorn.org/
- SQLite — https://www.sqlite.org/docs.html
- React — https://react.dev/
- Vite — https://vite.dev/
- pytest — https://docs.pytest.org/
- httpx — https://www.python-httpx.org/
- Playwright — https://playwright.dev/
- Ruff — https://docs.astral.sh/ruff/
- ESLint — https://eslint.org/
- python-docx — https://python-docx.readthedocs.io/
- MDN Web Docs (HTML, CSS y JavaScript) — https://developer.mozilla.org/

**Documentación del propio proyecto:** `README.md`, `COMANDOS_BACKEND.md`, `docs/Etapa_1.md` a `docs/Etapa_14.md`, `docs/casos_de_prueba.csv` y las evidencias en `docs/evidencias/`.

## Anexos

Evidencias del trabajo realizado, por etapa (todas las salidas son archivos reales de ejecución guardados en el repositorio):

| Etapa | Contenido | Ubicación |
|-------|-----------|-----------|
| Etapa 4 | Salidas de Ruff, `compileall`, ESLint, Vite build, SQLite, API y frontend (inicial y final). | `docs/evidencias/etapa_4/` |
| Etapa 6 | Log, resultados JSON de API/UI/caja blanca, resumen y capturas de pantalla. | `docs/evidencias/etapa_6/` (`screenshots/`) |
| Etapa 7 | Evidencias de los defectos DEF-01 a DEF-04 (migración, traza, botón/locator, Ruff). | `docs/evidencias/etapa_7/` |
| Etapa 8 | Salida de pytest y resultados de las pruebas unitarias. | `docs/evidencias/etapa_8/` |
| Etapa 9 | Salida de pytest y resultados de las pruebas de integración. | `docs/evidencias/etapa_9/` |
| Etapa 10 | Log consolidado, resultados JSON de la suite de sistema y resumen. | `docs/evidencias/etapa_10/` |
| Etapa 11 | Log de automatización, salidas de pytest y resultados JSON. | `docs/evidencias/etapa_11/` |
| Etapa 12 | Corridas RED/GREEN/final, diff del refactor y Ruff. | `docs/evidencias/etapa_12/` |
| Etapa 13 | Corrida de regresión, salidas de las suites y resultados consolidados. | `docs/evidencias/etapa_13/` |
| Etapa 14 | Registro de problemas no código, diff de artefactos, `pip install`, Ruff y pytest. | `docs/evidencias/etapa_14/` |

**Artefactos de prueba y documentación:** `backend/tests/` (conftest y suites de pruebas), `scripts/etapa_6/`, `scripts/etapa_8/`, `scripts/etapa_9/`, `docs/Etapa_5.md` y `docs/casos_de_prueba.csv`.

**Este informe.** Documento fuente: `docs/Etapa_15.md`. Versión Word: `docs/Etapa_15.docx`.
