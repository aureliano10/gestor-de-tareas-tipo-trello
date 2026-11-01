# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 9 - Pruebas de integración

## Objetivo de la etapa

Seleccionar funcionalidades que involucren la interacción entre dos o más componentes del sistema y verificar, mediante pruebas de integración automatizadas, que esos componentes funcionan correctamente en conjunto.

## Funcionalidad elegida

Se eligió la funcionalidad **"alta de tarea enriquecida → persistencia → lectura con filtros y orden → flujo de estados con reglas de negocio"**. Esta funcionalidad atraviesa las cuatro capas del backend:

- Un `POST /api/tasks` que transporta subtareas, etiquetas y enlaces.
- La validación y normalización en la capa de schemas.
- Las reglas de negocio y el acceso a datos del repositorio.
- La persistencia en SQLite, incluida la escritura del archivo adjunto en disco.
- La lectura posterior con filtros y orden, y las transiciones de estado con la regla de finalización.

## Componentes que interactúan

| Componente | Rol en el flujo |
|------------|-----------------|
| `routers/tasks.py`, `routers/subtasks.py`, `routers/attachments.py` | Reciben las peticiones HTTP y traducen los errores de dominio a códigos HTTP. |
| `schemas.py` | Valida y normaliza el cuerpo de la petición (título, etiquetas, enlaces, subtareas, prioridad y responsable). |
| `repository.py` | Aplica las reglas de negocio (límites, reapertura, bloqueo de finalización) y arma las consultas. |
| `database.py` | Abre la conexión SQLite, administra las transacciones y crea el esquema. |
| SQLite (archivo `.db`) | Almacena tareas, subtareas, adjuntos, etiquetas, enlaces y actividad. |
| Almacenamiento en disco | Guarda el contenido de los archivos adjuntos. |

Diagrama de flujo del componente probado:

```
Cliente (TestClient)
        |
        v
  [ routers ]  --- valida rutas y traduce errores ---> HTTP 201/200/409/404
        |
        v
  [ schemas ]  --- normaliza y valida (título, tags, links, subtareas) ---
        |
        v
  [ repository ] --- reglas de negocio: límites, reapertura, finalización ---
        |
        v
  [ database ] --- conexión y transacción SQLite (commit / rollback) -------
        |                                                              |
        v                                                              v
   SQLite (.db)                                            almacenamiento (archivos)
        |
        v
  Lectura: listado con filtros/orden + historial de actividad
```

## Estrategia de integración

Se utilizó una estrategia **de abajo hacia arriba (bottom-up)** con la base de datos completamente inicializada antes de ejercitar el flujo.

| Estrategia | Aplicabilidad | Decisión |
|------------|---------------|----------|
| Big-bang | Probaría todo el sistema de una sola vez, dificultando aislar la causa de un fallo. | Descartada para el diagnóstico. |
| Top-down | Requeriría stubs de las capas inferiores que no reflejan el comportamiento real de SQLite. | Descartada. |
| **Bottom-up** | Las capas inferiores (`database` y `repository`) ya fueron verificadas por unidad en la Etapa 8; la integración parte de esa base sólida y agrega la interacción real de las capas superiores. | **Elegida.** |

Justificación: como en la Etapa 8 se probaron por unidad la creación del esquema y las reglas de negocio, la integración se concentra en verificar que esas piezas funcionan en conjunto a través del stack HTTP real (`TestClient` de FastAPI → routers → schemas → repository → SQLite) y que los datos sobreviven a la lectura posterior.

Las pruebas se implementaron con pytest y el `TestClient` de FastAPI sobre la aplicación `app.main:app`, con una base y un almacenamiento temporales por prueba. Al usar el `TestClient` como gestor de contexto se dispara el evento de ciclo de vida de la aplicación, que inicializa el esquema con `init_db()`.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| pytest | 9.2.0 |
| FastAPI | 0.136.3 |
| httpx (TestClient) | 0.28.1 |
| Pydantic | 2.13.4 |
| SQLite | 3.45.1 |
| Backend bajo prueba | `app.main:app` importado directamente (sin servidor externo) |

No se utilizó el servidor del puerto 8000: cada prueba crea su propia base temporal con `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH`, por lo que no interfiere con los datos reales.

## Casos evaluados

| ID | Funcionalidad | Objetivo | Precondiciones | Datos de entrada | Procedimiento | Resultado esperado | Resultado obtenido | Estado | Observaciones |
|----|---------------|----------|----------------|------------------|---------------|--------------------|--------------------|--------|---------------|
| CP-IN-01 | Alta enriquecida y persistencia | Verificar que un alta con subtareas, etiquetas y enlaces se valida, persiste y vuelve a leerse completa. | Base inicializada y vacía. | `POST /api/tasks` con título con espacios, prioridad Alta, responsable, 3 etiquetas (dos con distinta caja), 2 subtareas y 1 enlace. | Enviar el POST; verificar el 201 y el cuerpo; listar con `GET /api/tasks`; consultar `GET /api/tags`. | 201; título recortado; prioridad Alta; estado Pendiente; 2 subtareas; etiquetas deduplicadas `["bug","release"]`; enlace con label; el listado y las etiquetas reflejan lo persistido. | 201; título `"Lanzamiento 1.0"`; prioridad Alta; `subtask_total` 2; tags `["bug","release"]`; `/api/tags` devolvió `["bug","release"]`. | Aprobado | Atraviesa routers → schemas → repository → SQLite y vuelve por la lectura. |
| CP-IN-02 | Archivos adjuntos | Verificar subida, escritura en disco y descarga íntegra del adjunto, con sus metadatos en la tarea. | Tarea creada. | `POST /api/tasks/{id}/attachments` con `notas.txt` de 18 bytes; luego `GET` de descarga. | Subir el archivo; verificar 201 y metadatos; comprobar el archivo en disco; descargar y comparar el contenido. | 201; `filename` y `size_bytes` correctos; 1 archivo en disco; descarga 200 con contenido idéntico y nombre original; la tarea lista el adjunto. | 201; `notas.txt` de 18 bytes; 1 archivo en disco; descarga 200 con contenido idéntico y `content-disposition` con `notas.txt`. | Aprobado | Integra la capa de adjuntos con `database.get_storage_path` y el sistema de archivos. |
| CP-IN-03 | Flujo de estados con regla de negocio | Verificar las transiciones Pendiente → En curso → Terminada y el bloqueo de finalización con subtareas pendientes. | Tarea creada con una subtarea pendiente. | `PATCH /api/tasks/{id}/move` a "En curso" y a "Terminada"; `PATCH /api/subtasks/{id}` con `done=true`; luego mover a "Terminada". | Mover a En curso; intentar finalizar; completar la subtarea; finalizar. | En curso 200; finalizar bloqueado 409 con detalle de la subtarea pendiente y estado "En curso"; tras completar, finalizar 200 con "Terminada". | 200 a En curso; 409 con "No se puede finalizar: la tarea tiene 1 subtarea pendiente"; `subtask_done` 1 tras completar; finalización 200 "Terminada". | Aprobado | Regla de negocio del repositorio traducida a 409 por el router. |
| CP-IN-04 | Reapertura automática | Verificar que agregar una subtarea pendiente a una tarea terminada la reabre a "En curso". | Tarea creada y finalizada (sin subtareas). | `POST /api/tasks/{id}/subtasks` con una subtarea pendiente. | Finalizar la tarea; verificar "Terminada"; agregar la subtarea; releer el listado. | 200 al finalizar; tras agregar la subtarea, 201 y estado "En curso", persistido en el listado. | 200 "Terminada"; 201 con estado "En curso"; el listado confirmó "En curso". | Aprobado | Cubre la reapertura disparada desde la capa de subtareas hacia la de tareas. |
| CP-IN-05 | Lectura con filtros y orden | Verificar los filtros por prioridad, etiqueta, vencimiento y texto, y el orden por prioridad y por fecha. | Tres tareas creadas con distinta prioridad, etiqueta y descripción; una con fecha pasada vía edición. | `GET /api/tasks` con `sort=priority`, `tag=backend`, `overdue=true`, `q=despliegue`, `sort=due`. | Crear las tareas; editar una con fecha pasada; ejecutar cada consulta y comparar los resultados. | Orden Alta, Media, Baja; filtro de etiqueta solo la que la tiene; vencidas solo la de fecha pasada; búsqueda solo la coincidencia en descripción; orden por fecha con la vencida primero. | Orden `["Alfa alta","Beta media","Gamma baja"]`; etiqueta y vencidas acotadas; búsqueda devolvió la tarea con "despliegue"; `overdue` verdadero y primero por fecha. | Aprobado | Integra el cálculo de `overdue` del repositorio con los filtros del router. |
| CP-IN-06 | Historial de actividad | Verificar que cada operación registra una entrada y que el orden de lectura es el más reciente primero. | Tarea creada. | `POST` de subtarea y `PATCH` de movimiento a "En curso". | Ejecutar las operaciones; releer el listado y revisar `activity`. | El historial contiene, del más reciente al más antiguo: "Movida a En curso", "Subtarea agregada: Paso" y "Tarea creada". | `activity` devolvió exactamente esas tres entradas en ese orden. | Aprobado | Confirma la persistencia de la actividad entre peticiones. |

## Procedimiento de ejecución

1. Configurar la base y el almacenamiento temporales con `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH` antes de crear el `TestClient`.
2. Instanciar `TestClient(app.main:app)` como gestor de contexto para disparar la inicialización del esquema.
3. Ejecutar las peticiones del flujo (alta, alta de subtarea, subida de adjunto, movimientos de estado y lecturas con filtros).
4. Verificar códigos HTTP, cuerpos de respuesta, archivos en disco y persistencia releyendo el listado.
5. Registrar los resultados en las evidencias.

Las pruebas se ejecutan con:

`.venv/bin/python -m pytest backend/tests/test_integration_flow.py -v`

## Resultados observados

| Métrica | Valor |
|---------|-------|
| Casos de integración | 6 |
| Pasados | 6 |
| Fallados | 0 |
| Resultado | 100% aprobado |

Resultado de la corrida: `6 passed, 1 warning in 1.04s`.

El aviso (`StarletteDeprecationWarning` sobre `httpx`/`httpx2`) proviene del `TestClient` de FastAPI y no afecta el resultado de las pruebas.

Observaciones relevantes:

- La capa de schemas normalizó los espacios del título y deduplicó las etiquetas sin distinguir mayúsculas antes de persistirlas.
- La escritura del adjunto quedó en disco y su contenido se recuperó idéntico en la descarga, con el nombre original conservado.
- La regla de finalización se aplicó de forma consistente: el repositorio lanzó el error de dominio y el router lo tradujo a HTTP 409.
- La reapertura automática funcionó al integrar la capa de subtareas con la de tareas.
- El cálculo de vencimiento se realizó en cada lectura sin almacenarse, y se combinó correctamente con los filtros del router.
- El historial de actividad se persistió y se devolvió con la entrada más reciente primero.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Código de las pruebas | `backend/tests/test_integration_flow.py` y la fixture de `backend/tests/conftest.py` |
| Salida completa de pytest | `docs/evidencias/etapa_9/pytest_salida.txt` |
| Casos evaluados y su estado | `docs/evidencias/etapa_9/resultados_integracion.json` |
| Script de ejecución | `scripts/etapa_9/ejecutar_pytest.py` |

## Reproducibilidad

Desde la raíz del repositorio:

1. Ejecutar las pruebas: `.venv/bin/python -m pytest backend/tests/test_integration_flow.py -v`.
2. Regenerar las evidencias: `.venv/bin/python scripts/etapa_9/ejecutar_pytest.py`.

No se requiere ningún servidor en ejecución ni una base previa.

## Conclusión de la etapa

Se implementaron 6 pruebas de integración que ejercitan la interacción real entre los routers HTTP, la capa de validación, el repositorio y la base SQLite, además del almacenamiento de adjuntos en disco. Los 6 casos se ejecutaron y aprobaron, verificando el alta enriquecida, la persistencia, la lectura con filtros y orden, el flujo de estados con la regla de finalización, la reapertura automática y el historial de actividad. La estrategia bottom-up permitió apoyarse en las unidades ya verificadas en la Etapa 8 y concentrar la integración en los puntos de contacto entre componentes.
