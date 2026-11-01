# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 10 - Pruebas de sistema y validación

## Objetivo de la etapa

Ejecutar pruebas sobre el sistema completo ya integrado, con el backend y el frontend en funcionamiento conjunto, para determinar si el producto desarrollado cumple con los requisitos definidos al comienzo del proyecto (RF1 a RF23 de la Etapa 1 y las restricciones de la Etapa 3). Se comprueban el funcionamiento general, el cumplimiento de los requisitos, el manejo de errores, el comportamiento ante datos incorrectos, la interacción entre funcionalidades y la respuesta ante situaciones esperadas y no esperadas. La etapa cierra con una respuesta explícita y justificada a la pregunta: ¿el sistema desarrollado satisface las necesidades planteadas al comienzo del proyecto?

## Alcance

Las pruebas de sistema se ejecutan sobre el sistema integrado, es decir, con los dos procesos en ejecución y comunicados por HTTP:

- **Backend** real levantado con Uvicorn sobre `http://127.0.0.1:8000`, con la API completa (routers, schemas, repository y SQLite).
- **Frontend** real servido por Vite sobre `http://127.0.0.1:5173`, consumiendo la API a través del proxy de desarrollo.

Se reutiliza la suite de ejecución reproducible de `scripts/etapa_6/`, que ejercita 80 casos sobre el sistema integrado:

- 62 casos de API con `httpx` contra el backend real.
- 11 casos de interfaz con Playwright sobre Chrome del sistema.
- 7 casos de caja blanca: 5 por invocación directa de unidades del backend y 2 sobre la interfaz real.

La corrida de esta etapa se realizó sobre una base y un almacenamiento temporales (`KANBAN_DB_PATH=/tmp/kanban_etapa6.db` y `KANBAN_STORAGE_PATH=/tmp/kanban_etapa6_storage`) para no afectar los datos reales del proyecto.

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
| Google Chrome | 151.0.7922.75 |
| Playwright | 1.64.1, con `channel="chrome"` y modo headless |
| Backend | `http://127.0.0.1:8000` |
| Frontend | `http://127.0.0.1:5173` con Vite |

## Funcionalidades principales seleccionadas

Se seleccionaron las funcionalidades centrales del producto, priorizando las que producen valor directo para el usuario y las que tienen más reglas de negocio asociadas:

| Funcionalidad | Requisitos | Justificación de la selección |
|---------------|-----------|-------------------------------|
| Alta de tarea (simple y enriquecida) | RF1, RF2, RF16, RF17, RF18, RF19, RF23 | Es la puerta de entrada del sistema y concentra la mayor cantidad de validaciones y restricciones. |
| Mover y reordenar tarea | RF3, RF4, RF22 | Es el comportamiento característico del tablero Kanban y tiene reglas de estado y de posición. |
| Checklist de subtareas y control de finalización | RF6, RF7, RF8, RF9 | Tiene la regla de negocio más fuerte (bloqueo de finalización y reapertura automática). |
| Fecha límite y vencimiento | RF10 | Depende del paso del tiempo y del cálculo derivado del vencimiento. |
| Archivos adjuntos | RF11, RF12, RF13 | Combina validación de formato, tamaño y cantidad con escritura en disco. |
| Eliminar con deshacer | RF14, RF15 | Involucra confirmación previa, borrado lógico y restauración. |
| Prioridad, responsable, etiquetas y enlaces | RF16 a RF19 | Clasificación de la tarea con límites propios y reutilización de datos. |
| Historial de actividad | RF20 | Registro transversal a todas las operaciones. |
| Búsqueda, filtros y orden | RF21, RF22 | Uso cotidiano del tablero y combinación de parámetros de consulta. |
| Editar tarea | RF5 | Modificación del contenido de una tarea existente. |

## Estrategia de las pruebas de sistema

- **Sistema completo:** cada caso se ejecuta contra los procesos reales (backend y frontend), sin dobles de prueba en el camino de producción.
- **Niveles combinados:** los flujos se verifican por API con `httpx`, por interfaz con Playwright y por invocación directa para las ramas de caja blanca.
- **Datos válidos, inválidos y de borde:** se cubren clases de equivalencia, valores límite y situaciones excepcionales, en línea con la consigna.
- **Verificación en tres planos:** código HTTP y cuerpo de la respuesta, estado persistido (relecutura y recarga de la página) y comportamiento visible en la interfaz.
- **Aislamiento:** antes de cada caso se limpian las tablas y el almacenamiento, de modo que los resultados no dependan del orden de ejecución.

Criterios de aprobación: un caso se considera **Aprobado** cuando todas sus comprobaciones se cumplen; en caso contrario queda **Fallido** y se registra la verificación incumplida.

## Casos de sistema

Los casos de sistema agrupan cada funcionalidad principal en un escenario de punta a punta y se apoyan en los casos concretos ya ejecutados sobre el sistema integrado. El **Resultado obtenido** de cada caso resume lo observado en esta corrida y la evidencia detallada queda en los archivos JSON de la corrida y en el log consolidado.

| ID | Funcionalidad | Objetivo | Precondiciones | Datos de entrada | Procedimiento | Resultado esperado | Resultado obtenido | Estado | Observaciones |
|----|---------------|----------|----------------|------------------|---------------|--------------------|--------------------|--------|---------------|
| CP-SIS-01 | Alta de tarea (simple y enriquecida) | Verificar que una tarea se puede registrar con título obligatorio y, además, con prioridad, responsable, subtareas, etiquetas y enlaces, en una sola operación. | Sistema integrado en ejecución y base vacía. | `POST /api/tasks` con título con espacios, prioridad "Alta", responsable, 2 subtareas, 2 etiquetas y 1 enlace; alta simple desde el formulario web. | Crear la tarea enriquecida por API y una simple desde la interfaz; verificar el 201, el estado "Pendiente", los datos persistidos y la tarjeta visible. | 201; título recortado; prioridad Alta; responsable; 2 subtareas; etiquetas deduplicadas; enlace con nombre; la tarjeta aparece en Pendiente y persiste al recargar. | 201; se persistieron prioridad, responsable, 2 subtareas, 2 etiquetas y 1 enlace en un solo POST; la tarjeta se mostró en Pendiente con insignia "Alta" y responsable "Ana" y persistió tras recargar. | Aprobado | Casos de apoyo: CP-CRE-01/02/03/07/08, CP-ALT-01, CP-UI-01, CP-UI-09, CP-UN-01/02, CP-IN-01. |
| CP-SIS-02 | Mover y reordenar tarea | Verificar el cambio de estado entre las tres columnas y el reordenamiento dentro de una misma columna. | Tareas creadas en Pendiente. | `PATCH /api/tasks/{id}/move` con estado destino y posición; arrastre entre columnas y dentro de la misma columna en la interfaz. | Mover a "En curso" y a "Terminada" por API; arrastrar una tarjeta a otra columna y reordenar dos tarjetas en la misma columna. | Transiciones válidas con 200; los valores fuera del conjunto y las posiciones negativas con 422; el reordenamiento deja posiciones 0, 1, 2 sin huecos; la interfaz emite el PATCH correcto y actualiza contadores. | Se aceptaron las tres transiciones y se rechazaron estado "Finalizada" y posición -1 con 422; el reordenamiento por API quedó C, A, B con posiciones 0, 1, 2 y por arrastre el PATCH de posición 0 reordenó Segunda/Primera sin cambiar el estado. | Aprobado | Casos de apoyo: CP-MOV-01 a CP-MOV-05, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-07. |
| CP-SIS-03 | Checklist y control de finalización | Verificar el alta, marcado, desmarcado y eliminación de subtareas, y la regla que impide finalizar con subtareas pendientes. | Tarea creada. | Subtareas con `title` y `done`; movimiento de la tarea a "Terminada". | Agregar subtareas, marcarlas y desmarcarlas, eliminarlas, intentar finalizar y completar luego la finalización. | Alta 201; el avance se refleja en `subtask_done`; finalizar con pendientes responde 409 y conserva el estado; al completar todas, finaliza con 200; desmarcar reabre a "En curso". | Se bloqueó la finalización con 409 "la tarea tiene 1 subtarea pendiente" y se conservó "En curso"; al completar la subtarea se finalizó con 200; desmarcar y agregar una subtarea pendiente reabrieron la tarea a "En curso"; la interfaz mostró el avance 0/2 → 1/2 → 1/1. | Aprobado | Casos de apoyo: CP-SUB-01 a CP-SUB-04, CP-BLO-01 a CP-BLO-04, CP-UI-06, CP-CB-02, CP-CB-05, CP-IN-03, CP-IN-04. |
| CP-SIS-04 | Fecha límite y vencimiento | Verificar la asignación de fecha límite y el señalamiento de tareas vencidas, incluyendo la restricción al crear y la libertad al editar. | Tareas creadas con y sin fecha. | Fecha futura al crear; fecha pasada al crear; fecha pasada al editar; filtro `overdue=true`. | Crear con fecha futura, intentar crear con fecha pasada, editar una tarea con fecha pasada y consultar el filtro de vencidas. | 201 con fecha futura y `overdue` falso; 422 con fecha pasada al crear; 200 al editar con fecha pasada y `overdue` verdadero; el filtro devuelve solo las vencidas. | Se rechazó la fecha pasada al crear con 422 "anterior a hoy"; la edición la admitió y `overdue` pasó a verdadero; el filtro `overdue=true` devolvió solo la tarea vencida y el listado completo devolvió las dos. | Aprobado | Casos de apoyo: CP-CRE-08, CP-CRE-09, CP-EDI-03, CP-FEC-01, CP-FEC-02, CP-IN-05. |
| CP-SIS-05 | Archivos adjuntos | Verificar la subida, la descarga íntegra y la eliminación de adjuntos, junto con los límites de extensión, tamaño y cantidad. | Tarea creada. | Archivos `.txt` válidos; archivo `.exe`; archivo de más de 5 MB; cuarta subida sobre el límite de 3. | Subir, descargar y eliminar un adjunto; subir archivos inválidos. | 201 con metadatos correctos y archivo en disco; descarga 200 con contenido idéntico; 204 al eliminar; 415 por extensión, 413 por tamaño y 409 por cantidad. | El adjunto de 1024 bytes se subió con 201, se descargó con contenido idéntico y nombre original, y se eliminó con 204; las subidas inválidas respondieron 415, 413 y 409 conservando el estado previo. | Aprobado | Casos de apoyo: CP-ADJ-01 a CP-ADJ-06, CP-UI-07, CP-CB-04, CP-IN-02. |
| CP-SIS-06 | Eliminar con deshacer | Verificar la eliminación con confirmación previa y la restauración de la tarea. | Tarea creada. | `DELETE /api/tasks/{id}` y `POST /api/tasks/{id}/restore`; clic en "Deshacer" sobre el aviso. | Eliminar la tarea por API y por interfaz, restaurarla y verificar la persistencia. | 204 al eliminar; la tarea sale del listado; 200 al restaurar y vuelve al final de su columna; la interfaz muestra el diálogo y ofrece "Deshacer". | La eliminación respondió 204 y la tarea dejó de aparecer; la restauración respondió 200 y la tarjeta volvió al tablero; restaurar una tarea activa o inexistente respondió 404; la interfaz mostró el diálogo y el aviso con "Deshacer" y persistió al recargar. | Aprobado | Casos de apoyo: CP-ELI-01, CP-ELI-02, CP-RES-01, CP-RES-02, CP-UI-08, CP-CB-03. |
| CP-SIS-07 | Clasificación e historial de actividad | Verificar prioridad, responsable, etiquetas, enlaces e historial de actividad sobre la tarea integrada. | Tarea creada. | Prioridad válida e inválida; responsable de 61 caracteres; 6 etiquetas; enlaces con esquema inválido y repetidos; consulta del historial. | Clasificar la tarea, editar sus datos y releer el historial. | Conjunto de prioridad respetado con "Media" por defecto; responsable recortado y limitado; etiquetas deduplicadas y limitadas a 5; enlaces http/https limitados a 5 sin duplicados; el historial registra cada acción y devuelve hasta 20 entradas, la más reciente primero. | Prioridad "Alta" y por defecto "Media"; responsable de 61 caracteres con 422; 6 etiquetas y 6 enlaces con 409; enlace `ftp://` y repetido rechazados; el historial registró "Tarea creada", "Movida a En curso", cambios de prioridad y responsable y devolvió 20 entradas como máximo, la más reciente primero. | Aprobado | Casos de apoyo: CP-PRI-01 a CP-PRI-04, CP-ASG-01 a CP-ASG-03, CP-TAG-01 a CP-TAG-04, CP-ENL-01 a CP-ENL-04, CP-HIS-01, CP-HIS-02, CP-UI-11, CP-UN-04 a CP-UN-12, CP-IN-06. |
| CP-SIS-08 | Búsqueda, filtros y orden | Verificar la búsqueda por texto y los filtros por prioridad, etiqueta y vencimiento, junto con el orden del listado. | Varias tareas creadas con distinta prioridad, etiqueta, descripción y fecha. | `GET /api/tasks` con `q`, `priority`, `tag`, `overdue` y `sort`; búsqueda desde la interfaz. | Crear tareas variadas y ejecutar cada consulta comparando los resultados con lo esperado. | La búsqueda coincide en título y descripción sin distinguir mayúsculas; los filtros devuelven solo las tareas correspondientes; el orden respeta los criterios permitidos y rechaza los inválidos con 422. | La búsqueda "informe" encontró coincidencias por título y por descripción sin distinguir mayúsculas; los filtros por prioridad, etiqueta y vencimiento devolvieron solo las tareas esperadas; `sort=priority` ordenó Alta, Media, Baja y un valor inválido respondió 422. | Aprobado | Casos de apoyo: CP-FIL-01 a CP-FIL-03, CP-ORD-01, CP-ORD-02, CP-UI-10, CP-IN-05. |
| CP-SIS-09 | Manejo de errores y datos incorrectos | Verificar que el sistema responde de forma controlada ante datos incorrectos y operaciones inválidas, sin corromper el estado. | Sistema integrado en ejecución. | Título vacío, con solo espacios y de 101 caracteres; descripción de 501; identificador no numérico e inexistente; cantidad y tamaño inválidos de adjuntos; estado y posición inválidos. | Enviar cada dato incorrecto y comparar el código de respuesta, el mensaje y el estado persistido. | 422 para validaciones de formato; 404 para recursos inexistentes; 409, 413 y 415 para las reglas de negocio y de adjuntos; el estado previo se conserva. | Todos los casos devolvieron el código previsto (422/404/409/413/415); los mensajes fueron legibles y el estado persistido no cambió tras un rechazo. | Aprobado | Casos de apoyo: CP-CRE-04/05/06/09, CP-MOV-02/03/04, CP-EDI-02, CP-SUB-04, CP-ADJ-04/05/06, CP-PRI-03, CP-ASG-02, CP-TAG-02/03, CP-ENL-02/03/04, CP-ALT-02, CP-CB-01, CP-CB-06. |
| CP-SIS-10 | Situaciones no esperadas | Verificar el comportamiento del sistema ante situaciones excepcionales o no previstas en el uso normal. | Sistema integrado en ejecución. | Error de red simulado; arrastre con identificadores inválidos; soltado dentro de la misma columna; restauración de una tarea activa. | Provocar cada situación y observar la reacción de la API y de la interfaz. | La interfaz muestra el error sin crear datos; las operaciones con identificadores inválidos no emiten peticiones; el soltado en la misma columna reordena en lugar de fallar; la restauración inválida responde 404. | El error de red simulado se mostró en la interfaz sin crear la tarjeta; los identificadores inválidos en el arrastre no emitieron PATCH; el soltado en la misma columna reordenó con posición 0; la restauración de una tarea activa respondió 404. | Aprobado | Casos de apoyo: CP-CB-06, CP-CB-07, CP-MOV-04, CP-RES-02, CP-ELI-02. |

## Manejo de errores y datos incorrectos

El comportamiento frente a datos incorrectos se verificó en los tres planos del sistema (interfaz, API y base). Resumen de las respuestas observadas:

| Situación | Respuesta observada | Verificado en |
|-----------|---------------------|---------------|
| Título vacío o solo espacios | HTTP 422 con mensaje legible; sin alta; la interfaz no emite POST. | CP-CRE-05, CP-CRE-06, CP-UI-02, CP-CB-06 |
| Título de 101 caracteres | HTTP 422 con el límite de 100. | CP-CRE-04, CP-CB-01, CP-CB-06 |
| Descripción de 501 caracteres | HTTP 422 con el límite de 500. | CP-CB-06 |
| Fecha límite pasada al crear | HTTP 422 "anterior a hoy". | CP-CRE-09 |
| Estado no permitido o posición negativa | HTTP 422; el estado y la posición previos se conservan. | CP-MOV-02 |
| Identificador no numérico o inexistente | HTTP 422 en la ruta y HTTP 404 en recursos ausentes. | CP-MOV-03, CP-MOV-04, CP-EDI-02, CP-SUB-04, CP-ELI-02, CP-RES-02 |
| Prioridad, responsable, etiqueta o enlace inválidos | HTTP 422 con el detalle correspondiente; sin cambios. | CP-PRI-03, CP-ASG-02, CP-TAG-03, CP-ENL-02 |
| Más de 5 etiquetas, 5 enlaces o 20 subtareas | HTTP 409 con el detalle del límite; no se crea la tarea. | CP-TAG-02, CP-ENL-03, CP-ENL-04, CP-ALT-02 |
| Enlace repetido | HTTP 409 "El enlace ya está agregado a la tarea". | CP-ENL-04 |
| Finalizar con subtareas pendientes | HTTP 409; la tarea conserva su estado. | CP-BLO-01, CP-CB-02 |
| Adjunto con extensión no permitida | HTTP 415 con los formatos aceptados. | CP-ADJ-04 |
| Adjunto de más de 5 MB | HTTP 413 "El archivo supera el tamaño máximo de 5 MB". | CP-ADJ-05 |
| Cuarto adjunto | HTTP 409; la tarea conserva 3 adjuntos. | CP-ADJ-06, CP-CB-04 |
| Error de conexión con la API | Mensaje "Error simulado de red" visible en la interfaz; sin creación. | CP-CB-06 |

## Interacción entre funcionalidades

La interacción se verificó con flujos que atraviesan varias funcionalidades sobre el mismo estado persistido:

- **Alta enriquecida → listado → etiquetas:** un solo `POST` carga subtareas, etiquetas, enlaces, prioridad y responsable; el listado y el catálogo de etiquetas reflejan lo persistido (CP-ALT-01, CP-IN-01).
- **Checklist → control de finalización → reapertura:** la presencia de subtareas pendientes condiciona la finalización y, al agregar una pendiente o desmarcar una subtarea, la tarea se reabre sola (CP-BLO-03, CP-BLO-04, CP-CB-05, CP-IN-03, CP-IN-04).
- **Edición de fecha → vencimiento → filtro:** cambiar la fecha altera el cálculo de `overdue`, que a su vez cambia el resultado del filtro de vencidas (CP-FEC-01, CP-FEC-02, CP-EDI-03).
- **Adjunto → tarea → descarga:** el archivo subido queda asociado a la tarea, se escribe en disco y se recupera íntegro en la descarga (CP-ADJ-01, CP-ADJ-02, CP-IN-02).
- **Toda operación → historial:** cada acción deja una entrada en la actividad, que se lee ordenada de la más reciente a la más antigua (CP-HIS-01, CP-HIS-02, CP-IN-06).
- **Interfaz ↔ API:** la interfaz traduce las interacciones del usuario en las peticiones correctas (un `PATCH` por movimiento, un `PUT` por edición, un `DELETE` por eliminación) y refleja la respuesta de la API en el tablero (CP-UI-03 a CP-UI-08).

## Situaciones esperadas y no esperadas

**Esperadas.** Los flujos normales de alta, edición, movimiento, checklist, adjuntos, clasificación, búsqueda y eliminación con deshacer funcionaron según lo previsto, con persistencia comprobada al recargar la página y al releer la API.

**No esperadas.** Se probaron de forma deliberada las siguientes situaciones: un error de red simulado, el arrastre con identificadores inválidos ("abc" y "0"), el soltado dentro de la misma columna, el intento de finalizar con subtareas pendientes, la restauración de una tarea que no estaba eliminada, el acceso a recursos inexistentes y la superación de los límites de etiquetas, enlaces y subtareas. En todos los casos el sistema respondió de forma controlada: mensajes claros en la interfaz, códigos HTTP adecuados y ningún estado corrupto.

## Resultados generales

| Grupo | Casos | Aprobados | Fallidos | Resultado |
|-------|-------|-----------|----------|-----------|
| API (`httpx`) | 62 | 62 | 0 | 100% aprobado |
| Interfaz (Playwright) | 11 | 11 | 0 | 100% aprobado |
| Caja blanca | 7 | 7 | 0 | 100% aprobado |
| **Total** | **80** | **80** | **0** | **100% aprobado** |

Si se suman las pruebas automatizadas de las etapas 8 y 9 sobre el mismo sistema, el total validado asciende a **104 casos aprobados** (80 de sistema + 18 unitarios + 6 de integración), todos con resultado favorable.

## Matriz de trazabilidad

Matriz que vincula cada requisito funcional (RF1 a RF23 de la Etapa 1) con los casos que lo cubren, el resultado obtenido y su evidencia. La columna "Casos" incluye los casos de la suite de sistema (Etapa 10), los unitarios (CP-UN, Etapa 8) y los de integración (CP-IN, Etapa 9) cuando corresponden.

| Requisito | Descripción | Casos asociados | Resultado | Evidencia |
|-----------|-------------|-----------------|-----------|-----------|
| RF1 | Registrar una tarea con título y datos opcionales | CP-CRE-01 a CP-CRE-09, CP-LIS-01, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-06, CP-UN-01, CP-UN-02, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json`, `resultados_unitarias.json`, `resultados_integracion.json` |
| RF2 | Estado inicial "Pendiente" | CP-CRE-01, CP-CRE-02, CP-CRE-03, CP-CRE-07, CP-CRE-08, CP-LIS-01, CP-UI-01, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF3 | Actualizar el estado de una tarea | CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-CB-02, CP-CB-07, CP-IN-03 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json`, `resultados_integracion.json` |
| RF4 | Reordenar dentro de la columna | CP-MOV-05, CP-UI-04, CP-CB-07 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json` |
| RF5 | Editar título, descripción y fecha | CP-EDI-01 a CP-EDI-03, CP-UI-05, CP-IN-05 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF6 | Registrar subtareas | CP-SUB-01, CP-SUB-04, CP-UI-06, CP-BLO-03, CP-IN-04 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF7 | Marcar y desmarcar subtareas | CP-SUB-02, CP-UI-06, CP-CB-05, CP-BLO-04, CP-IN-03 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json`, `resultados_integracion.json` |
| RF8 | Eliminar subtareas | CP-SUB-03, CP-UI-06 | Aprobado | `resultados_api.json`, `resultados_ui.json` |
| RF9 | Impedir finalizar con subtareas pendientes | CP-BLO-01 a CP-BLO-04, CP-UI-06, CP-CB-02, CP-CB-05, CP-IN-03 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json`, `resultados_integracion.json` |
| RF10 | Fecha límite y vencimiento | CP-CRE-08, CP-CRE-09, CP-EDI-03, CP-FEC-01, CP-FEC-02, CP-IN-05 | Aprobado | `resultados_api.json`, `resultados_integracion.json` |
| RF11 | Adjuntar archivos | CP-ADJ-01, CP-ADJ-04, CP-ADJ-05, CP-ADJ-06, CP-UI-07, CP-CB-04, CP-IN-02 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json`, `resultados_integracion.json` |
| RF12 | Descargar adjuntos | CP-ADJ-02, CP-UI-07, CP-IN-02 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF13 | Eliminar adjuntos | CP-ADJ-03 | Aprobado | `resultados_api.json` |
| RF14 | Eliminar una tarea | CP-ELI-01, CP-ELI-02, CP-UI-08, CP-CB-03 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json` |
| RF15 | Recuperar una tarea eliminada | CP-RES-01, CP-RES-02, CP-UI-08, CP-CB-03 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_caja_blanca.json` |
| RF16 | Prioridad por defecto "Media" | CP-PRI-01 a CP-PRI-04, CP-UI-09, CP-ALT-01, CP-UN-04, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_unitarias.json`, `resultados_integracion.json` |
| RF17 | Responsable de hasta 60 caracteres | CP-ASG-01 a CP-ASG-03, CP-UI-09, CP-ALT-01, CP-UN-05 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_unitarias.json` |
| RF18 | Hasta 5 etiquetas de 30 caracteres | CP-TAG-01 a CP-TAG-04, CP-ALT-01, CP-UN-06, CP-UN-07, CP-UN-10, CP-UN-11, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_unitarias.json`, `resultados_integracion.json` |
| RF19 | Hasta 5 enlaces http/https sin duplicados | CP-ENL-01 a CP-ENL-04, CP-ALT-01, CP-UN-08, CP-UN-09, CP-UN-12, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_unitarias.json`, `resultados_integracion.json` |
| RF20 | Historial de actividad (20 entradas) | CP-HIS-01, CP-HIS-02, CP-UI-11, CP-PRI-04, CP-ASG-03, CP-TAG-04, CP-IN-06 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF21 | Búsqueda y filtros | CP-FIL-01 a CP-FIL-03, CP-UI-10, CP-IN-05 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_integracion.json` |
| RF22 | Orden del listado | CP-ORD-01, CP-ORD-02, CP-IN-05 | Aprobado | `resultados_api.json`, `resultados_integracion.json` |
| RF23 | Alta enriquecida | CP-ALT-01, CP-ALT-02, CP-UI-09, CP-UN-13, CP-IN-01 | Aprobado | `resultados_api.json`, `resultados_ui.json`, `resultados_unitarias.json`, `resultados_integracion.json` |

Cobertura de requisitos:

| Métrica | Valor |
|---------|-------|
| Requisitos funcionales (RF1 a RF23) | 23 |
| Requisitos cubiertos por al menos un caso aprobado | 23 |
| Requisitos sin cobertura | 0 |
| Casos de sistema ejecutados | 80 (todos aprobados) |
| Casos automatizados complementarios (etapas 8 y 9) | 24 (todos aprobados) |
| Total de casos considerados | 104 |

Los 23 requisitos funcionales quedan cubiertos por al menos un caso ejecutado y aprobado, y las restricciones asociadas (longitud de título y descripción, estados válidos, fecha límite, adjuntos, persistencia, prioridad, responsable, etiquetas, enlaces, historial, búsqueda, orden y alta enriquecida) también quedaron verificadas por los casos de borde e inválidos de la suite.

## Conclusión: ¿el sistema satisface las necesidades planteadas?

**Sí, el sistema desarrollado satisface las necesidades planteadas al comienzo del proyecto.** La respuesta se justifica con las evidencias obtenidas:

1. **Cobertura total de requisitos.** Los 23 requisitos funcionales (RF1 a RF23) definidos en la Etapa 1 quedan cubiertos por casos ejecutados y aprobados, y la matriz de trazabilidad muestra que no existe ningún requisito sin cobertura.
2. **Funcionamiento verificado de las funcionalidades principales.** Las diez funcionalidades seleccionadas (alta simple y enriquecida, movimiento y reordenamiento, checklist y control de finalización, fecha límite y vencimiento, adjuntos, eliminación con deshacer, clasificación, historial, búsqueda/filtros/orden y edición) funcionaron según lo esperado sobre el sistema integrado, tanto por API como por interfaz.
3. **Manejo de errores y datos incorrectos.** El sistema respondió de forma controlada a títulos inválidos, fechas pasadas, estados y posiciones fuera de rango, identificadores inexistentes o no numéricos, límites de etiquetas, enlaces y adjuntos, extensiones y tamaños no permitidos, y errores de conexión, sin corromper el estado persistido.
4. **Interacción entre funcionalidades.** Los flujos que combinan varias funcionalidades (alta enriquecida, checklist con bloqueo y reapertura, edición con recálculo de vencimiento, adjuntos con descarga, historial transversal y coordinación interfaz–API) se comportaron de forma consistente sobre el mismo estado.
5. **Situaciones esperadas y no esperadas.** Tanto los flujos normales como las situaciones excepcionales (error de red simulado, arrastres inválidos, operaciones sobre recursos inexistentes y límites superados) se resolvieron correctamente.
6. **Resultados de la suite.** Los 80 casos de sistema se aprobaron en su totalidad (62 de API, 11 de interfaz y 7 de caja blanca), y los 24 casos automatizados de las etapas 8 y 9 también se aprobaron, sin detectar defectos funcionales en esta etapa.

El producto cumple, entonces, con los requisitos definidos inicialmente y con las restricciones establecidas, y las evidencias de ejecución respaldan esa conclusión sin reservas.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Log consolidado de la corrida de sistema | `docs/evidencias/etapa_10/ejecucion_sistema.log` |
| Resultados de los 62 casos de API | `docs/evidencias/etapa_10/resultados_api.json` |
| Resultados de los 11 casos de interfaz | `docs/evidencias/etapa_10/resultados_ui.json` |
| Resultados de los 7 casos de caja blanca | `docs/evidencias/etapa_10/resultados_caja_blanca.json` |
| Resumen consolidado de resultados | `docs/evidencias/etapa_10/resumen_resultados.json` |
| Referencia de ejecución de la Etapa 6 | `docs/evidencias/etapa_10/ejecucion_etapa6_referencia.log` |
| Resultados automatizados de unitarias e integración | `docs/evidencias/etapa_8/` y `docs/evidencias/etapa_9/` |

## Reproducibilidad

1. Iniciar el backend de pruebas desde `backend/`:
   `KANBAN_DB_PATH=/tmp/kanban_etapa6.db KANBAN_STORAGE_PATH=/tmp/kanban_etapa6_storage ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
2. Iniciar el frontend con `npm run dev` desde `frontend/`.
3. Ejecutar la suite desde la raíz del repositorio:
   `.venv/bin/python scripts/etapa_6/ejecutar_api.py`,
   `.venv/bin/python scripts/etapa_6/ejecutar_ui.py` y
   `.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py`.
4. Consolidar los resultados con `.venv/bin/python scripts/etapa_6/consolidar.py`.
5. Ejecutar las pruebas automatizadas complementarias:
   `.venv/bin/python scripts/etapa_8/ejecutar_pytest.py` y
   `.venv/bin/python scripts/etapa_9/ejecutar_pytest.py`.

## Próxima etapa

La Etapa 11 consistirá en la automatización de las pruebas: se documentarán las herramientas utilizadas, los casos automatizados, el procedimiento de ejecución, los resultados y las ventajas y limitaciones encontradas.
