# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 30/10/2026

# Etapa 5 - Diseño de casos de prueba

## Objetivo de la etapa

Diseñar los casos de prueba a partir de los requisitos y de las funcionalidades implementadas en la Etapa 3, aplicando técnicas de caja negra y de caja blanca, y dejando preparada la información necesaria para ejecutar las pruebas en la Etapa 6.

## Alcance y criterios

Esta etapa es de **diseño**. Los casos se documentan con todos sus campos. La ejecución y el registro de resultados se realizaron en la Etapa 6; por ese motivo, los campos `Resultado obtenido` y `Estado` reflejan los resultados de esa ejecución.

Se aplican las siguientes técnicas:

- **Caja negra:** clases de equivalencia, análisis de valores límite y datos válidos e inválidos.
- **Caja blanca:** análisis de instrucciones, decisiones, condiciones y caminos de ejecución sobre fragmentos seleccionados del backend y del frontend.

Criterios generales:

- Cada caso tiene un identificador único y evalúa una sola situación.
- Los datos válidos e inválidos se derivan de los requisitos y de las restricciones de la Etapa 1.
- Los casos de interfaz se ejecutan sobre el sistema completo; los de caja blanca sobre la unidad indicada.
- La cobertura indicada es la cobertura esperada del diseño; la cobertura real se midió al ejecutar las pruebas en la Etapa 6.

## Funcionalidades y requisitos cubiertos

| Funcionalidad | Requisitos asociados | Casos |
|---------------|----------------------|-------|
| Crear tarea | RF1, RF2 y restricciones del título, la descripción y la fecha | CP-CRE-01 a CP-CRE-09, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-06 |
| Mover y reordenar tarea | RF3, RF4 y restricción de estados válidos | CP-MOV-01 a CP-MOV-05, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-07 |
| Editar tarea | RF5 y restricción de fecha en la edición | CP-EDI-01 a CP-EDI-03, CP-UI-05 |
| Checklist de subtareas | RF6, RF7, RF8 | CP-SUB-01 a CP-SUB-04, CP-UI-06, CP-CB-05 |
| Control de finalización | RF9 y reglas de reapertura | CP-BLO-01 a CP-BLO-04, CP-UI-06, CP-CB-02, CP-CB-05 |
| Fecha límite y vencimiento | RF10 | CP-FEC-01, CP-FEC-02, CP-CRE-08 |
| Archivos adjuntos | RF11, RF12, RF13 y restricciones de extensión, tamaño y cantidad | CP-ADJ-01 a CP-ADJ-06, CP-UI-07, CP-CB-04 |
| Eliminar y restaurar | RF14, RF15 | CP-ELI-01, CP-ELI-02, CP-RES-01, CP-RES-02, CP-UI-08, CP-CB-03 |
| Listar tareas y persistencia | RF1, RF2 y persistencia | CP-LIS-01 |
| Prioridad | RF16 y restricción del conjunto {Baja, Media, Alta} | CP-PRI-01 a CP-PRI-04, CP-UI-09 |
| Responsable | RF17 y restricción de 60 caracteres | CP-ASG-01 a CP-ASG-03, CP-UI-09 |
| Etiquetas | RF18 y restricciones de cantidad (5) y longitud (30) | CP-TAG-01 a CP-TAG-04 |
| Enlaces | RF19 y restricciones de esquema, cantidad (5) y duplicados | CP-ENL-01 a CP-ENL-04 |
| Historial de actividad | RF20 y restricción de 20 entradas | CP-HIS-01, CP-HIS-02, CP-UI-11 |
| Búsqueda y filtros | RF21 | CP-FIL-01 a CP-FIL-03, CP-UI-10 |
| Orden del tablero | RF22 y restricción del conjunto de criterios | CP-ORD-01, CP-ORD-02 |
| Alta enriquecida | RF23 | CP-ALT-01, CP-ALT-02, CP-UI-09 |

## Caja negra

### Clases de equivalencia

| Entrada | Clase | Tipo | Valores representativos | Casos |
|---------|-------|------|-------------------------|-------|
| Título | Cadena de 1 a 100 caracteres después de quitar espacios extremos, no vacía | Válida | "Preparar informe" | CP-CRE-01 |
| Título | Cadena con espacios extremos que queda válida al normalizarse | Válida | "  Revisar pruebas  " | CP-CRE-07 |
| Título | Cadena vacía | Inválida | "" | CP-CRE-05 |
| Título | Cadena compuesta solo por espacios | Inválida | "     " | CP-CRE-06 |
| Título | Cadena de más de 100 caracteres después de normalizar | Inválida | 101 caracteres | CP-CRE-04 |
| Descripción | Cadena de hasta 500 caracteres, opcional | Válida | "Detalle de la tarea" | CP-CRE-08 |
| Descripción | Cadena de más de 500 caracteres | Inválida | 501 caracteres | CP-CB-06 |
| Fecha límite al crear | Fecha de hoy o posterior, u omitida | Válida | hoy + 7 días | CP-CRE-08 |
| Fecha límite al crear | Fecha anterior a hoy | Inválida | hoy − 1 día | CP-CRE-09 |
| Fecha límite al editar | Cualquier fecha válida, incluso pasada | Válida | hoy − 2 días | CP-EDI-03, CP-FEC-01 |
| Estado | Uno de los tres valores permitidos | Válido | "Pendiente", "En curso", "Terminada" | CP-MOV-01 |
| Estado | Cualquier otro valor o formato | Inválido | "Finalizada", "pendiente", "" | CP-MOV-02 |
| Posición | Entero mayor o igual a 0 | Válido | 0, 1, 2 | CP-MOV-05, CP-UI-04 |
| Posición | Entero negativo | Inválida | -1 | CP-MOV-02 |
| Identificador | Entero positivo existente | Válido | id de una tarea creada | CP-MOV-01, CP-ELI-01 |
| Identificador | Entero positivo inexistente | Inválido | 999999 | CP-MOV-03, CP-ELI-02, CP-RES-02 |
| Identificador | Valor no numérico | Inválido | "abc" | CP-MOV-04 |
| Subtarea: título | Cadena válida de hasta 100 caracteres | Válida | "Diseñar casos" | CP-SUB-01 |
| Subtarea: título | Cadena vacía o solo espacios | Inválida | "" | CP-CB-01 |
| Subtarea: estado | Booleano | Válido | true, false | CP-SUB-02 |
| Archivo adjunto: extensión | Extensión incluida en la lista permitida | Válida | ".txt", ".pdf", ".png" | CP-ADJ-01 |
| Archivo adjunto: extensión | Extensión ajena a la lista permitida | Inválida | ".exe" | CP-ADJ-04 |
| Archivo adjunto: tamaño | Entre 1 byte y 5 MB | Válido | 1024 bytes | CP-ADJ-01 |
| Archivo adjunto: tamaño | Más de 5 MB | Inválido | 5 MB + 1 byte | CP-ADJ-05 |
| Archivo adjunto: cantidad | Hasta 3 archivos por tarea | Válido | 3 archivos | CP-ADJ-06 |
| Archivo adjunto: cantidad | Un cuarto archivo | Inválido | 4.º archivo | CP-ADJ-06 |
| Prioridad | Uno de los tres valores permitidos u omitida | Válida | "Baja", "Media", "Alta" | CP-PRI-01, CP-PRI-02 |
| Prioridad | Cualquier otro valor | Inválida | "Urgente" | CP-PRI-03 |
| Responsable | Cadena de hasta 60 caracteres tras recortar, opcional | Válida | "Ana Gómez" | CP-ASG-01 |
| Responsable | Cadena de 61 caracteres | Inválida | 61 caracteres | CP-ASG-02 |
| Etiqueta | Nombre de 1 a 30 caracteres, hasta 5 por tarea | Válida | "backend" | CP-TAG-01 |
| Etiqueta | Nombre vacío o de solo espacios | Inválida | "", "   " | CP-TAG-03 |
| Etiqueta | Más de 5 etiquetas por tarea | Inválida | 6 etiquetas | CP-TAG-02 |
| Enlace: url | URL http(s) de hasta 500 caracteres | Válida | "https://ejemplo.com/doc" | CP-ENL-01 |
| Enlace: url | URL con otro esquema o sin esquema | Inválida | "ftp://...", "ejemplo.com" | CP-ENL-02 |
| Enlace: cantidad | Hasta 5 enlaces por tarea | Válida | 5 enlaces | CP-ENL-01 |
| Enlace: cantidad | Un sexto enlace o un enlace repetido | Inválida | 6 enlaces, url duplicada | CP-ENL-03, CP-ENL-04 |
| Criterio de orden (`sort`) | Uno de {position, priority, due, created} | Válido | "priority" | CP-ORD-01 |
| Criterio de orden (`sort`) | Cualquier otro valor | Inválido | "invalido" | CP-ORD-02 |
| Subtareas en el alta | Hasta 20 por tarea | Válida | 2 subtareas | CP-ALT-01 |
| Subtareas en el alta | 21 o más subtareas | Inválida | 21 subtareas | CP-ALT-02 |

### Análisis de valores límite

| Variable | Límite | Valores considerados | Casos |
|----------|--------|----------------------|-------|
| Longitud del título | Inferior | 0 caracteres útil (vacío o solo espacios) y 1 carácter | CP-CRE-02, CP-CRE-05, CP-CRE-06 |
| Longitud del título | Superior | 100 (máximo válido) y 101 (fuera de límite) | CP-CRE-03, CP-CRE-04 |
| Longitud de la descripción | Superior | 500 (máximo válido) y 501 (fuera de límite) | CP-CRE-08, CP-CB-06 |
| Fecha límite | Inferior respecto de hoy | Hoy (permitida al crear) y ayer (rechazada al crear) | CP-CRE-08, CP-CRE-09 |
| Estado | Conjunto de valores permitidos | Coincidencia exacta con uno de los tres estados y un valor fuera del conjunto | CP-MOV-01, CP-MOV-02 |
| Posición | Inferior | 0 (primera posición) y -1 (rechazada) | CP-MOV-05, CP-MOV-02 |
| Tamaño del adjunto | Superior | 5 MB (máximo válido) y 5 MB + 1 byte (rechazado) | CP-ADJ-01, CP-ADJ-05 |
| Cantidad de adjuntos | Superior | 3 (máximo válido) y 4 (rechazado) | CP-ADJ-06 |
| Identificador | Existencia | Tarea existente, tarea inexistente y valor no numérico | CP-MOV-01, CP-MOV-03, CP-MOV-04, CP-ELI-01, CP-ELI-02 |
| Longitud del responsable | Superior | 60 (máximo válido) y 61 (rechazado) | CP-ASG-01, CP-ASG-02 |
| Cantidad de etiquetas | Superior | 5 (máximo válido) y 6 (rechazado) | CP-TAG-01, CP-TAG-02 |
| Cantidad de enlaces | Superior | 5 (máximo válido) y 6 (rechazado) | CP-ENL-01, CP-ENL-03 |
| Cantidad de subtareas en el alta | Superior | 20 (máximo válido) y 21 (rechazado) | CP-HIS-02, CP-ALT-02 |
| Entradas del historial | Superior | 20 (máximo devuelto) | CP-HIS-02 |
| Prioridad | Conjunto de valores permitidos | Coincidencia con el conjunto y un valor fuera del conjunto | CP-PRI-01, CP-PRI-03 |
| Criterio de orden | Conjunto de valores permitidos | Coincidencia con el conjunto y un valor fuera del conjunto | CP-ORD-01, CP-ORD-02 |

## Caja blanca

### Unidades analizadas

| Unidad | Ubicación | Motivo de selección |
|--------|-----------|---------------------|
| `clean_title` | `backend/app/schemas.py:23-32` | Concentra las decisiones de validación del título, reutilizada en tareas y subtareas. |
| `move_task` | `backend/app/repository.py:191-206` | Contiene la decisión de existencia y la regla de bloqueo por subtareas pendientes. |
| `delete_task` y `restore_task` | `backend/app/repository.py:209-239` | Contienen el borrado lógico y las decisiones de restauración. |
| `create_attachment` | `backend/app/repository.py:293-314` | Contiene la decisión del límite de adjuntos por tarea. |
| `update_subtask` | `backend/app/repository.py:257-278` | Contiene la condición de reapertura de una tarea terminada. |
| `validateTaskInput` y `handleSubmit` | `frontend/src/components/TaskFields.jsx:4-16` y `TaskForm.jsx:12-31` | Concentran las validaciones previas al envío del formulario. |
| `dropIndex` y `handleDrop` | `frontend/src/components/Column.jsx:9-22` y `Column.jsx:54-64` | Contienen la decisión del identificador y el cálculo de la posición de destino. |

### Modelo de decisiones y caminos

| Unidad | Decisión o condición | Resultado | Camino | Casos asociados |
|--------|----------------------|-----------|--------|-----------------|
| `clean_title` | `value is None` | Lanza error de título obligatorio | Defensivo, no alcanzable desde la API | Sin caso funcional |
| `clean_title` | `not clean_title_value` | Lanza error de título vacío | Inválido | CP-CB-01, CP-CRE-05, CP-CRE-06 |
| `clean_title` | `len(clean_title_value) > 100` | Lanza error de longitud | Inválido | CP-CB-01, CP-CRE-04 |
| `clean_title` | Ninguna condición anterior | Devuelve el título recortado | Válido | CP-CB-01, CP-CRE-07 |
| `move_task` | `row is None` | Devuelve `None` y el router responde 404 | Inexistente | CP-CB-02, CP-MOV-03 |
| `move_task` | `pending > 0` al pasar a Terminada | Lanza `PendingSubtasksError` y el router responde 409 | Bloqueado | CP-CB-02, CP-BLO-01 |
| `move_task` | `pending == 0` al pasar a Terminada | Aplica el movimiento y devuelve la tarea | Válido | CP-CB-02, CP-BLO-02, CP-MOV-01 |
| `delete_task` | `row is not None` | Marca `deleted_at` y devuelve `True` | Existente | CP-CB-03, CP-ELI-01 |
| `delete_task` | `row is None` | Devuelve `False` y el router responde 404 | Inexistente | CP-CB-03, CP-ELI-02 |
| `restore_task` | Fila con `deleted_at` no nulo | Restaura y devuelve la tarea | Existente | CP-CB-03, CP-RES-01 |
| `restore_task` | Fila inexistente o activa | Devuelve `None` y el router responde 404 | Inexistente | CP-CB-03, CP-RES-02 |
| `create_attachment` | `total >= 3` | Lanza `AttachmentLimitError` y el router responde 409 | Bloqueado | CP-CB-04, CP-ADJ-06 |
| `create_attachment` | `total < 3` | Inserta el adjunto y devuelve la tarea | Válido | CP-CB-04, CP-ADJ-01 |
| `update_subtask` | `done is False` y la tarea está Terminada | Reabre la tarea a En curso | Reapertura | CP-CB-05, CP-BLO-04 |
| `update_subtask` | `done is False` y la tarea no está Terminada | Solo actualiza la subtarea | Válido | CP-CB-05, CP-SUB-02 |
| `validateTaskInput` | `!cleanTitle` | Devuelve error de título | Inválido | CP-CB-06, CP-UI-02 |
| `validateTaskInput` | `cleanTitle.length > 100` | Devuelve error de longitud | Inválido | CP-CB-06 |
| `validateTaskInput` | `description.length > 500` | Devuelve error de descripción | Inválido | CP-CB-06 |
| `handleSubmit` | Validaciones superadas | Invoca `onCreate` y limpia el formulario | Válido | CP-CB-06, CP-UI-01 |
| `handleSubmit` | `catch` de la llamada a `onCreate` | Muestra el error recibido | Error de API | CP-CB-06 |
| `handleDrop` | `!Number.isInteger(taskId) \|\| taskId <= 0` | No invoca `onMove` | Inválido | CP-CB-07 |
| `handleDrop` | Identificador válido | Invoca `onMove` con `dropIndex` calculado | Válido | CP-CB-07, CP-UI-03, CP-UI-04 |

La rama `value is None` de `clean_title` es una defensa interna: Pydantic rechaza un valor nulo o ausente antes de ejecutar el validador, por lo que no es alcanzable a través de la API. Se documenta como camino no cubierto por un caso funcional y no se considera un defecto.

### Estimación de cobertura

| Unidad | Cobertura de decisiones | Cobertura de condiciones | Observación |
|--------|-------------------------|--------------------------|-------------|
| `clean_title` | 100% de las decisiones alcanzables | No aplica | La decisión defensiva `value is None` no es alcanzable desde la API. |
| `move_task` | 100% | No aplica | Se cubren tarea existente, inexistente y finalización bloqueada. |
| `delete_task` y `restore_task` | 100% | No aplica | Se cubren borrado existente e inexistente y restauración válida e inválida. |
| `create_attachment` | 100% | No aplica | Se cubren el alta y el exceso del límite. |
| `update_subtask` | 100% | 100% de la condición compuesta | Se cubren los dos resultados de `not done and status == Terminada`. |
| `validateTaskInput` y `handleSubmit` | 100% de las decisiones de validación | No aplica | Se cubren vacío, solo espacios, 101 caracteres, 501 de descripción, error de API y alta válida. |
| `dropIndex` y `handleDrop` | 100% de la decisión | 100% de las condiciones simples | Se cubren identificador inválido, misma columna y columna distinta. |

La cobertura real se verificó durante la ejecución de la Etapa 6; las pruebas unitarias formales se incorporarán en la Etapa 8.

## Matriz de trazabilidad y resumen de casos

| ID | Funcionalidad | Técnica principal | Requisito o restricción | Capa |
|----|---------------|-------------------|-------------------------|------|
| CP-CRE-01 | Crear tarea | Clase de equivalencia válida | RF1, RF2 | API |
| CP-CRE-02 | Crear tarea | Valor límite inferior | RF1, RF2 | API |
| CP-CRE-03 | Crear tarea | Valor límite superior | RF1, RF2 | API |
| CP-CRE-04 | Crear tarea | Valor límite superior inválido | RF1 | API |
| CP-CRE-05 | Crear tarea | Clase de equivalencia inválida | RF1 | API |
| CP-CRE-06 | Crear tarea | Clase inválida y valor límite | RF1 | API |
| CP-CRE-07 | Crear tarea | Clase válida con normalización | RF1, RF2 | API |
| CP-CRE-08 | Crear tarea | Clase válida con descripción y fecha límite | RF1, RF2, RF10 | API |
| CP-CRE-09 | Crear tarea | Clase inválida de fecha límite | RF1, RF10 | API |
| CP-MOV-01 | Mover tarea | Clase de equivalencia válida | RF3 | API |
| CP-MOV-02 | Mover tarea | Clase de equivalencia inválida | RF3 | API |
| CP-MOV-03 | Mover tarea | Identificador inexistente | RF3 | API |
| CP-MOV-04 | Mover tarea | Identificador no numérico | RF3 | API |
| CP-MOV-05 | Mover tarea | Reordenamiento en la misma columna | RF4 | API |
| CP-EDI-01 | Editar tarea | Clase de equivalencia válida | RF5 | API |
| CP-EDI-02 | Editar tarea | Identificador inexistente | RF5 | API |
| CP-EDI-03 | Editar tarea | Valor límite de fecha permitido | RF5, RF10 | API |
| CP-SUB-01 | Checklist | Flujo normal | RF6 | API |
| CP-SUB-02 | Checklist | Cambio de estado de la subtarea | RF7 | API |
| CP-SUB-03 | Checklist | Eliminación de la subtarea | RF8 | API |
| CP-SUB-04 | Checklist | Tarea inexistente | RF6 | API |
| CP-BLO-01 | Control de finalización | Regla de bloqueo | RF9 | API |
| CP-BLO-02 | Control de finalización | Flujo normal | RF9 | API |
| CP-BLO-03 | Control de finalización | Reapertura al agregar subtarea | RF9 | API |
| CP-BLO-04 | Control de finalización | Reapertura al desmarcar subtarea | RF9 | API |
| CP-FEC-01 | Fecha y vencimiento | Estado calculado | RF10 | API |
| CP-FEC-02 | Fecha y vencimiento | Filtro de vencidas | RF10 | API |
| CP-ADJ-01 | Adjuntos | Flujo normal de subida | RF11 | API |
| CP-ADJ-02 | Adjuntos | Flujo normal de descarga | RF12 | API |
| CP-ADJ-03 | Adjuntos | Flujo normal de eliminación | RF13 | API |
| CP-ADJ-04 | Adjuntos | Extensión no permitida | RF11 | API |
| CP-ADJ-05 | Adjuntos | Valor límite de tamaño | RF11 | API |
| CP-ADJ-06 | Adjuntos | Valor límite de cantidad | RF11 | API |
| CP-ELI-01 | Eliminar tarea | Clase de equivalencia válida | RF14 | API |
| CP-ELI-02 | Eliminar tarea | Identificador inexistente | RF14 | API |
| CP-RES-01 | Restaurar tarea | Flujo normal | RF15 | API |
| CP-RES-02 | Restaurar tarea | Restauración de una tarea no eliminada | RF15 | API |
| CP-LIS-01 | Listar tareas | Flujo normal y persistencia | RF1, RF2 | API |
| CP-PRI-01 | Prioridad | Clase de equivalencia válida | RF16 | API |
| CP-PRI-02 | Prioridad | Clase válida por omisión | RF16 | API |
| CP-PRI-03 | Prioridad | Clase de equivalencia inválida | RF16 | API |
| CP-PRI-04 | Prioridad | Flujo normal de actualización | RF16, RF20 | API |
| CP-ASG-01 | Responsable | Clase válida con normalización | RF17 | API |
| CP-ASG-02 | Responsable | Valor límite superior inválido | RF17 | API |
| CP-ASG-03 | Responsable | Flujo normal de actualización | RF17, RF20 | API |
| CP-TAG-01 | Etiquetas | Clase de equivalencia válida | RF18 | API |
| CP-TAG-02 | Etiquetas | Valor límite superior inválido | RF18 | API |
| CP-TAG-03 | Etiquetas | Clase inválida y valor límite | RF18 | API |
| CP-TAG-04 | Etiquetas | Flujo normal de reemplazo | RF18, RF20 | API |
| CP-ENL-01 | Enlaces | Clase de equivalencia válida | RF19 | API |
| CP-ENL-02 | Enlaces | Clase inválida de esquema | RF19 | API |
| CP-ENL-03 | Enlaces | Valor límite superior inválido | RF19 | API |
| CP-ENL-04 | Enlaces | Clase inválida de duplicados | RF19 | API |
| CP-HIS-01 | Historial de actividad | Flujo normal | RF20 | API |
| CP-HIS-02 | Historial de actividad | Valor límite y orden | RF20 | API |
| CP-FIL-01 | Búsqueda y filtros | Flujo normal de filtro | RF21 | API |
| CP-FIL-02 | Búsqueda y filtros | Flujo normal de filtro | RF21 | API |
| CP-FIL-03 | Búsqueda y filtros | Flujo normal de búsqueda | RF21 | API |
| CP-ORD-01 | Orden del tablero | Flujo normal de orden | RF22 | API |
| CP-ORD-02 | Orden del tablero | Clase de equivalencia inválida | RF22 | API |
| CP-ALT-01 | Alta enriquecida | Flujo normal | RF16, RF17, RF18, RF19, RF23 | API |
| CP-ALT-02 | Alta enriquecida | Valor límite superior inválido | RF23 | API |
| CP-UI-01 | Crear tarea | Flujo válido de interfaz | RF1, RF2 | Interfaz |
| CP-UI-02 | Crear tarea | Clase inválida y valor límite | RF1 | Interfaz |
| CP-UI-03 | Mover tarea | Flujo de interfaz | RF3 | Interfaz |
| CP-UI-04 | Mover y reordenar | Condición de borde de interfaz | RF4 | Interfaz |
| CP-UI-05 | Editar tarea | Flujo de interfaz | RF5 | Interfaz |
| CP-UI-06 | Checklist | Flujo de interfaz con reapertura | RF6, RF7, RF8, RF9 | Interfaz |
| CP-UI-07 | Adjuntos | Flujo de interfaz de subida y descarga | RF11, RF12 | Interfaz |
| CP-UI-08 | Eliminar y restaurar | Flujo de interfaz con deshacer | RF14, RF15 | Interfaz |
| CP-UI-09 | Alta enriquecida | Flujo de interfaz | RF16, RF17, RF23 | Interfaz |
| CP-UI-10 | Búsqueda y filtros | Flujo de interfaz | RF21 | Interfaz |
| CP-UI-11 | Historial de actividad | Flujo de interfaz | RF20 | Interfaz |
| CP-CB-01 | Validar título | Caja blanca - decisiones | RF1 y restricciones del título | Backend (unidad) |
| CP-CB-02 | Mover tarea | Caja blanca - decisiones | RF3, RF9 | Backend (unidad) |
| CP-CB-03 | Eliminar y restaurar | Caja blanca - decisiones | RF14, RF15 | Backend (unidad) |
| CP-CB-04 | Límite de adjuntos | Caja blanca - decisiones | RF11 | Backend (unidad) |
| CP-CB-05 | Reapertura de subtarea | Caja blanca - condiciones | RF9 | Backend (unidad) |
| CP-CB-06 | Validar formulario | Caja blanca - decisiones | RF1 | Frontend (unidad) |
| CP-CB-07 | Mover por arrastre | Caja blanca - condiciones | RF3, RF4 | Frontend (unidad) |

## Trazabilidad por requisito

| Requisito o restricción | Casos que lo cubren |
|-------------------------|---------------------|
| RF1: registrar una tarea | CP-CRE-01 a CP-CRE-09, CP-LIS-01, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-06 |
| RF2: estado inicial Pendiente | CP-CRE-01, CP-CRE-02, CP-CRE-03, CP-CRE-07, CP-CRE-08, CP-LIS-01, CP-UI-01 |
| RF3: actualizar el estado | CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-CB-02, CP-CB-07 |
| RF4: reordenar dentro de la columna | CP-MOV-05, CP-UI-04, CP-CB-07 |
| RF5: editar una tarea | CP-EDI-01 a CP-EDI-03, CP-UI-05 |
| RF6: registrar subtareas | CP-SUB-01, CP-SUB-04, CP-UI-06 |
| RF7: marcar y desmarcar subtareas | CP-SUB-02, CP-UI-06, CP-CB-05 |
| RF8: eliminar subtareas | CP-SUB-03, CP-UI-06 |
| RF9: control de finalización | CP-BLO-01 a CP-BLO-04, CP-UI-06, CP-CB-02, CP-CB-05 |
| RF10: fecha límite y vencimiento | CP-CRE-08, CP-CRE-09, CP-EDI-03, CP-FEC-01, CP-FEC-02 |
| RF11: adjuntar archivos | CP-ADJ-01, CP-ADJ-04, CP-ADJ-05, CP-ADJ-06, CP-UI-07, CP-CB-04 |
| RF12: descargar adjuntos | CP-ADJ-02, CP-UI-07 |
| RF13: eliminar adjuntos | CP-ADJ-03 |
| RF14: eliminar tareas | CP-ELI-01, CP-ELI-02, CP-UI-08, CP-CB-03 |
| RF15: recuperar tareas eliminadas | CP-RES-01, CP-RES-02, CP-UI-08, CP-CB-03 |
| Título obligatorio, no vacío y de hasta 100 caracteres | CP-CRE-02 a CP-CRE-07, CP-UI-02, CP-CB-01, CP-CB-06 |
| Descripción de hasta 500 caracteres | CP-CRE-08, CP-CB-06 |
| Un solo estado válido por tarea | CP-CRE-01, CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-CB-02 |
| Hasta 3 adjuntos de 5 MB con extensiones permitidas | CP-ADJ-01, CP-ADJ-04, CP-ADJ-05, CP-ADJ-06, CP-CB-04 |
| Persistencia de los cambios | CP-LIS-01, CP-UI-01, CP-UI-03, CP-UI-05, CP-UI-06, CP-UI-07, CP-UI-08, CP-CB-02, CP-CB-03 |
| RF16: prioridad de la tarea | CP-PRI-01 a CP-PRI-04, CP-ALT-01, CP-UI-09 |
| RF17: responsable de la tarea | CP-ASG-01 a CP-ASG-03, CP-ALT-01, CP-UI-09 |
| RF18: etiquetas | CP-TAG-01 a CP-TAG-04, CP-ALT-01 |
| RF19: enlaces | CP-ENL-01 a CP-ENL-04, CP-ALT-01 |
| RF20: historial de actividad | CP-PRI-04, CP-ASG-03, CP-TAG-04, CP-HIS-01, CP-HIS-02, CP-UI-11 |
| RF21: búsqueda y filtros | CP-FIL-01 a CP-FIL-03, CP-UI-10 |
| RF22: orden del tablero | CP-ORD-01, CP-ORD-02 |
| RF23: alta enriquecida | CP-ALT-01, CP-ALT-02, CP-UI-09 |

## Fichas de casos de prueba

### CP-CRE-01

- ID: CP-CRE-01
- Funcionalidad: Crear tarea
- Objetivo: Verificar el alta de una tarea con un título válido y la asignación del estado inicial.
- Precondiciones: API en ejecución y base de datos SQLite accesible.
- Datos de entrada: {"title": "Preparar informe"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y luego consultar GET /api/tasks.
- Resultado esperado: HTTP 201, con id entero, title "Preparar informe", description "", status "Pendiente", due_date nulo, position 0, overdue falso, subtask_total 0, subtasks y attachments vacíos; la tarea aparece en el listado.
- Resultado obtenido: HTTP 201; tarea #81 creada en estado Pendiente, position 0 y overdue falso, presente en el listado.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia válida típica. Verifica además RF2 y la forma completa de la respuesta.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2
- Capa: API

### CP-CRE-02

- ID: CP-CRE-02
- Funcionalidad: Crear tarea
- Objetivo: Verificar el límite inferior de longitud del título con un carácter.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "A"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y registrar la respuesta.
- Resultado esperado: HTTP 201, title "A" y status "Pendiente".
- Resultado obtenido: HTTP 201; título de un carácter aceptado con estado Pendiente.
- Estado: Aprobado.
- Observaciones: Valor límite inferior válido.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1, RF2
- Capa: API

### CP-CRE-03

- ID: CP-CRE-03
- Funcionalidad: Crear tarea
- Objetivo: Verificar el límite superior válido de longitud del título con 100 caracteres.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "a" repetido 100 veces}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y medir la longitud del título devuelto.
- Resultado esperado: HTTP 201; el título devuelto tiene exactamente 100 caracteres y estado "Pendiente".
- Resultado obtenido: HTTP 201; título de exactamente 100 caracteres aceptado.
- Estado: Aprobado.
- Observaciones: Valor límite superior válido.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1, RF2
- Capa: API

### CP-CRE-04

- ID: CP-CRE-04
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título que supera el máximo permitido.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "a" repetido 101 veces}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con el mensaje "El título no puede superar los 100 caracteres"; la tarea no se crea.
- Resultado obtenido: HTTP 422; título de 101 caracteres rechazado y listado vacío.
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1
- Capa: API

### CP-CRE-05

- ID: CP-CRE-05
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título vacío.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": ""}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con mensaje de título vacío; la tarea no se crea.
- Resultado obtenido: HTTP 422; título vacío rechazado y listado vacío.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF1
- Capa: API

### CP-CRE-06

- ID: CP-CRE-06
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título compuesto solo por espacios.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "     "}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con el mensaje "El título no puede estar vacío ni contener solo espacios"; la tarea no se crea.
- Resultado obtenido: HTTP 422; título con solo espacios rechazado y listado vacío.
- Estado: Aprobado.
- Observaciones: Clase inválida y valor límite inferior después de quitar espacios.
- Técnica: Caja negra - clase de equivalencia inválida y valor límite.
- Requisito: RF1
- Capa: API

### CP-CRE-07

- ID: CP-CRE-07
- Funcionalidad: Crear tarea
- Objetivo: Verificar la normalización de espacios al inicio y al final del título.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "  Revisar pruebas  "}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar el título almacenado.
- Resultado esperado: HTTP 201 con title "Revisar pruebas", sin espacios extremos, y status "Pendiente".
- Resultado obtenido: HTTP 201; espacios externos recortados y título persistido como "Revisar pruebas".
- Estado: Aprobado.
- Observaciones: Clase válida con normalización.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2
- Capa: API

### CP-CRE-08

- ID: CP-CRE-08
- Funcionalidad: Crear tarea
- Objetivo: Verificar el alta con descripción y fecha límite futura, y el cálculo de vencimiento.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Informe final", "description": "Detalle de la tarea", "due_date": fecha de hoy más 7 días}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar los campos devueltos.
- Resultado esperado: HTTP 201 con description "Detalle de la tarea", due_date igual a la enviada y overdue falso.
- Resultado obtenido: HTTP 201; descripción y fecha límite (2026-11-08) almacenadas y overdue falso.
- Estado: Aprobado.
- Observaciones: Valor límite de fecha permitido y verificación del estado calculado.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2, RF10
- Capa: API

### CP-CRE-09

- ID: CP-CRE-09
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de una fecha límite anterior a hoy al crear la tarea.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Tarea atrasada", "due_date": fecha de ayer}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con el mensaje "La fecha límite no puede ser anterior a hoy"; la tarea no se crea.
- Resultado obtenido: HTTP 422; fecha límite pasada rechazada al crear y listado vacío.
- Estado: Aprobado.
- Observaciones: Valor límite inválido de fecha al crear.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1, RF10
- Capa: API

### CP-MOV-01

- ID: CP-MOV-01
- Funcionalidad: Mover tarea
- Objetivo: Verificar las transiciones válidas entre los tres estados.
- Precondiciones: Existe una tarea en estado "Pendiente" con identificador conocido.
- Datos de entrada: PATCH {"status": "En curso"} y luego PATCH {"status": "Terminada"} sobre la misma tarea.
- Procedimiento: Crear la tarea, mover a "En curso", consultar, mover a "Terminada" y volver a consultar.
- Resultado esperado: HTTP 200 en cada movimiento; los estados quedan persistidos y el id y el título no cambian.
- Resultado obtenido: Tres estados válidos: PATCH 200 a En curso y a Terminada, con estado final "Terminada" persistido.
- Estado: Aprobado.
- Observaciones: Cubre los tres valores válidos del estado y las transiciones permitidas.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF3
- Capa: API

### CP-MOV-02

- ID: CP-MOV-02
- Funcionalidad: Mover tarea
- Objetivo: Verificar el rechazo de un estado o una posición no permitidos.
- Precondiciones: Existe una tarea con estado conocido.
- Datos de entrada: PATCH {"status": "Finalizada"} y PATCH {"status": "Pendiente", "position": -1}.
- Procedimiento: Enviar PATCH /api/tasks/{id}/move con cada cuerpo y luego consultar la tarea.
- Resultado esperado: HTTP 422 en ambos casos; la tarea conserva su estado y su posición.
- Resultado obtenido: HTTP 422 con estado y con posición inválidos; la tarea conservó su estado Pendiente y su posición 0.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida de estado y valor límite inválido de posición.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3
- Capa: API

### CP-MOV-03

- ID: CP-MOV-03
- Funcionalidad: Mover tarea
- Objetivo: Verificar la respuesta al intentar mover una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 999999.
- Datos de entrada: PATCH /api/tasks/999999/move con {"status": "En curso"}.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404 con detalle "Tarea no encontrada".
- Estado: Aprobado.
- Observaciones: Identificador válido como número pero inexistente.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3
- Capa: API

### CP-MOV-04

- ID: CP-MOV-04
- Funcionalidad: Mover tarea
- Objetivo: Verificar el rechazo de un identificador no numérico en la ruta.
- Precondiciones: API en ejecución.
- Datos de entrada: PATCH /api/tasks/abc/move con {"status": "En curso"}.
- Procedimiento: Enviar la petición y registrar el código de respuesta.
- Resultado esperado: HTTP 422 por error de validación del parámetro de ruta; no se modifica ninguna tarea.
- Resultado obtenido: HTTP 422 por identificador no numérico en la ruta.
- Estado: Aprobado.
- Observaciones: Clase inválida de identificador.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3
- Capa: API

### CP-MOV-05

- ID: CP-MOV-05
- Funcionalidad: Mover y reordenar tarea
- Objetivo: Verificar el reordenamiento de una tarea dentro de la misma columna.
- Precondiciones: Existen tres tareas en "Pendiente" creadas en el orden A, B y C.
- Datos de entrada: PATCH /api/tasks/{id_C}/move con {"status": "Pendiente", "position": 0}.
- Procedimiento: Enviar el movimiento y luego consultar GET /api/tasks para observar las posiciones.
- Resultado esperado: HTTP 200; el orden de la columna pasa a ser C, A, B con posiciones 0, 1 y 2 sin huecos.
- Resultado obtenido: HTTP 200; la columna quedó ordenada como C, A, B con posiciones [0, 1, 2].
- Estado: Aprobado.
- Observaciones: Cubre el reordenamiento sin cambio de estado y el reindexado de la columna.
- Técnica: Caja negra - flujo normal.
- Requisito: RF4
- Capa: API

### CP-EDI-01

- ID: CP-EDI-01
- Funcionalidad: Editar tarea
- Objetivo: Verificar la edición del título, la descripción y la fecha límite de una tarea.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: PUT con {"title": "Tarea editada", "description": "Nueva descripción", "due_date": fecha de hoy más 3 días}.
- Procedimiento: Enviar PUT /api/tasks/{id} y luego consultar la tarea.
- Resultado esperado: HTTP 200 con los tres campos actualizados y el resto de la tarea sin cambios.
- Resultado obtenido: PUT 200; título, descripción y fecha límite actualizados sin alterar el estado.
- Estado: Aprobado.
- Observaciones: Flujo normal de edición.
- Técnica: Caja negra - flujo normal.
- Requisito: RF5
- Capa: API

### CP-EDI-02

- ID: CP-EDI-02
- Funcionalidad: Editar tarea
- Objetivo: Verificar la respuesta al intentar editar una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 999999.
- Datos de entrada: PUT /api/tasks/999999 con {"title": "Tarea fantasma"}.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404 con detalle "Tarea no encontrada".
- Estado: Aprobado.
- Observaciones: Identificador inexistente en la edición.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF5
- Capa: API

### CP-EDI-03

- ID: CP-EDI-03
- Funcionalidad: Editar tarea
- Objetivo: Verificar que la edición admite una fecha límite pasada, a diferencia del alta.
- Precondiciones: Existe una tarea en "Pendiente" creada sin fecha límite.
- Datos de entrada: PUT con {"title": "Revisar informe", "due_date": fecha de hace 2 días}.
- Procedimiento: Enviar PUT /api/tasks/{id} y observar la fecha y el estado de vencimiento.
- Resultado esperado: HTTP 200 con la fecha límite pasada almacenada y overdue verdadero.
- Resultado obtenido: HTTP 200; la edición admitió la fecha pasada (2026-10-30) y overdue quedó verdadero.
- Estado: Aprobado.
- Observaciones: La restricción de fecha futura se aplica solo al crear; en la edición se admite una fecha pasada.
- Técnica: Caja negra - valor límite permitido.
- Requisito: RF5, RF10
- Capa: API

### CP-SUB-01

- ID: CP-SUB-01
- Funcionalidad: Checklist de subtareas
- Objetivo: Verificar el alta de una subtarea dentro de una tarea.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: POST /api/tasks/{id}/subtasks con {"title": "Diseñar casos"}.
- Procedimiento: Enviar la petición y observar la tarea devuelta.
- Resultado esperado: HTTP 201 con una subtarea nueva, subtask_total 1, subtask_done 0 y el título recortado.
- Resultado obtenido: HTTP 201; subtarea creada, subtask_total 1 y subtask_done 0.
- Estado: Aprobado.
- Observaciones: Flujo normal de alta de subtarea.
- Técnica: Caja negra - flujo normal.
- Requisito: RF6
- Capa: API

### CP-SUB-02

- ID: CP-SUB-02
- Funcionalidad: Checklist de subtareas
- Objetivo: Verificar el marcado y el desmarcado de una subtarea completada.
- Precondiciones: Existe una tarea con una subtarea pendiente.
- Datos de entrada: PATCH /api/subtasks/{id} con {"done": true} y luego con {"done": false}.
- Procedimiento: Enviar ambos PATCH y observar el contador de avance en cada respuesta.
- Resultado esperado: HTTP 200 en ambos casos; subtask_done pasa a 1 y vuelve a 0 sin cambiar el estado de la tarea.
- Resultado obtenido: HTTP 200 en ambos PATCH; el avance pasó a 1/1 y volvió a 0/1 sin cambiar el estado.
- Estado: Aprobado.
- Observaciones: Modificación del estado de completado de la subtarea.
- Técnica: Caja negra - flujo normal.
- Requisito: RF7
- Capa: API

### CP-SUB-03

- ID: CP-SUB-03
- Funcionalidad: Checklist de subtareas
- Objetivo: Verificar la eliminación de una subtarea.
- Precondiciones: Existe una tarea con una subtarea.
- Datos de entrada: DELETE /api/subtasks/{id}.
- Procedimiento: Enviar la petición y consultar la tarea.
- Resultado esperado: HTTP 204 sin cuerpo; la tarea queda con subtask_total 0.
- Resultado obtenido: DELETE 204 sin cuerpo; la tarea quedó con subtask_total 0.
- Estado: Aprobado.
- Observaciones: Flujo normal de eliminación de subtarea.
- Técnica: Caja negra - flujo normal.
- Requisito: RF8
- Capa: API

### CP-SUB-04

- ID: CP-SUB-04
- Funcionalidad: Checklist de subtareas
- Objetivo: Verificar la respuesta al intentar agregar una subtarea a una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 999999.
- Datos de entrada: POST /api/tasks/999999/subtasks con {"title": "Subtarea huérfana"}.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404 con detalle "Tarea no encontrada".
- Estado: Aprobado.
- Observaciones: Identificador inexistente en el alta de subtarea.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF6
- Capa: API

### CP-BLO-01

- ID: CP-BLO-01
- Funcionalidad: Control de finalización
- Objetivo: Verificar el bloqueo al intentar finalizar una tarea con subtareas pendientes.
- Precondiciones: Existe una tarea con una subtarea pendiente.
- Datos de entrada: PATCH /api/tasks/{id}/move con {"status": "Terminada"}.
- Procedimiento: Enviar la petición y luego consultar la tarea.
- Resultado esperado: HTTP 409 con el detalle "No se puede finalizar: la tarea tiene 1 subtarea pendiente"; la tarea conserva su estado anterior.
- Resultado obtenido: HTTP 409 con detalle del bloqueo; la tarea conservó su estado Pendiente.
- Estado: Aprobado.
- Observaciones: Regla de negocio principal del control de finalización.
- Técnica: Caja negra - regla de negocio.
- Requisito: RF9
- Capa: API

### CP-BLO-02

- ID: CP-BLO-02
- Funcionalidad: Control de finalización
- Objetivo: Verificar que la tarea se finaliza cuando todas sus subtareas están completadas.
- Precondiciones: Existe una tarea con una subtarea marcada como completada.
- Datos de entrada: PATCH /api/tasks/{id}/move con {"status": "Terminada"}.
- Procedimiento: Enviar la petición y observar el estado devuelto.
- Resultado esperado: HTTP 200 con status "Terminada".
- Resultado obtenido: HTTP 200; tarea finalizada al no tener subtareas pendientes.
- Estado: Aprobado.
- Observaciones: Complemento del bloqueo: sin subtareas pendientes la finalización se permite.
- Técnica: Caja negra - flujo normal.
- Requisito: RF9
- Capa: API

### CP-BLO-03

- ID: CP-BLO-03
- Funcionalidad: Control de finalización
- Objetivo: Verificar la reapertura automática al agregar una subtarea pendiente a una tarea terminada.
- Precondiciones: Existe una tarea en estado "Terminada" sin subtareas.
- Datos de entrada: POST /api/tasks/{id}/subtasks con {"title": "Tarea adicional"}.
- Procedimiento: Enviar la petición y observar el estado de la tarea devuelta.
- Resultado esperado: HTTP 201 con la subtarea creada y el status de la tarea cambiado a "En curso".
- Resultado obtenido: HTTP 201 con la subtarea creada y la tarea reabierta a "En curso".
- Estado: Aprobado.
- Observaciones: Regla de coherencia entre el checklist y el estado de la tarea.
- Técnica: Caja negra - regla de negocio.
- Requisito: RF9
- Capa: API

### CP-BLO-04

- ID: CP-BLO-04
- Funcionalidad: Control de finalización
- Objetivo: Verificar la reapertura automática al desmarcar una subtarea de una tarea terminada.
- Precondiciones: Existe una tarea en estado "Terminada" con una subtarea completada.
- Datos de entrada: PATCH /api/subtasks/{id} con {"done": false}.
- Procedimiento: Enviar la petición y observar el estado de la tarea devuelta.
- Resultado esperado: HTTP 200 con la subtarea desmarcada y el status de la tarea cambiado a "En curso".
- Resultado obtenido: HTTP 200 con la subtarea desmarcada y la tarea reabierta a "En curso".
- Estado: Aprobado.
- Observaciones: Misma regla de coherencia que CP-BLO-03, en sentido inverso.
- Técnica: Caja negra - regla de negocio.
- Requisito: RF9
- Capa: API

### CP-FEC-01

- ID: CP-FEC-01
- Funcionalidad: Fecha límite y vencimiento
- Objetivo: Verificar que el estado de vencimiento se calcula a partir de la fecha límite y el estado de la tarea.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: Tarea creada con fecha de hoy más 2 días; luego editada con fecha de hace 2 días.
- Procedimiento: Consultar la tarea tras el alta y tras la edición, y comparar el campo overdue.
- Resultado esperado: En el alta overdue es falso; tras la edición overdue es verdadero y el estado de la tarea no cambia.
- Resultado obtenido: overdue pasó de falso a verdadero al editar la fecha, sin cambiar el estado.
- Estado: Aprobado.
- Observaciones: Confirma que overdue no se almacena sino que se deriva.
- Técnica: Caja negra - estado calculado.
- Requisito: RF10
- Capa: API

### CP-FEC-02

- ID: CP-FEC-02
- Funcionalidad: Fecha límite y vencimiento
- Objetivo: Verificar el filtro de tareas vencidas.
- Precondiciones: Existe una tarea vencida (fecha pasada editada) y otra con fecha futura.
- Datos de entrada: GET /api/tasks?overdue=true y GET /api/tasks.
- Procedimiento: Consultar ambos listados y comparar su contenido.
- Resultado esperado: El listado con filtro devuelve solo la tarea vencida; el listado sin filtro devuelve las dos.
- Resultado obtenido: El filtro overdue devolvió solo la tarea vencida y el listado completo las dos.
- Estado: Aprobado.
- Observaciones: Verifica el parámetro de consulta de vencidas.
- Técnica: Caja negra - flujo normal.
- Requisito: RF10
- Capa: API

### CP-ADJ-01

- ID: CP-ADJ-01
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar la subida de un archivo adjunto válido.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: POST multipart con el archivo "notas.txt" de 1 KB.
- Procedimiento: Enviar la petición y observar los adjuntos de la tarea devuelta.
- Resultado esperado: HTTP 201 con un adjunto de filename "notas.txt" y size_bytes 1024.
- Resultado obtenido: HTTP 201; adjunto "notas.txt" de 1024 bytes agregado a la tarea.
- Estado: Aprobado.
- Observaciones: Flujo normal de subida con extensión permitida.
- Técnica: Caja negra - flujo normal.
- Requisito: RF11
- Capa: API

### CP-ADJ-02

- ID: CP-ADJ-02
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar la descarga de un archivo adjunto.
- Precondiciones: Existe una tarea con el adjunto "notas.txt" subido previamente.
- Datos de entrada: GET /api/tasks/{id}/attachments/{attachment_id}.
- Procedimiento: Descargar el adjunto y comparar el contenido con el archivo original.
- Resultado esperado: HTTP 200 con el contenido idéntico al archivo subido y el nombre original en la cabecera de descarga.
- Resultado obtenido: HTTP 200 con el contenido idéntico al subido y el nombre original en la cabecera.
- Estado: Aprobado.
- Observaciones: Verifica la integridad del archivo almacenado.
- Técnica: Caja negra - flujo normal.
- Requisito: RF12
- Capa: API

### CP-ADJ-03

- ID: CP-ADJ-03
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar la eliminación de un archivo adjunto.
- Precondiciones: Existe una tarea con un adjunto subido.
- Datos de entrada: DELETE /api/tasks/{id}/attachments/{attachment_id}.
- Procedimiento: Enviar la petición, consultar la tarea y volver a intentar la descarga.
- Resultado esperado: HTTP 204; la tarea queda sin adjuntos y la descarga posterior responde HTTP 404.
- Resultado obtenido: DELETE 204; la tarea quedó sin adjuntos y la descarga posterior respondió 404.
- Estado: Aprobado.
- Observaciones: Verifica también que el archivo físico deja de estar disponible.
- Técnica: Caja negra - flujo normal.
- Requisito: RF13
- Capa: API

### CP-ADJ-04

- ID: CP-ADJ-04
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar el rechazo de un archivo con extensión no permitida.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: POST multipart con el archivo "programa.exe".
- Procedimiento: Enviar la petición y consultar los adjuntos de la tarea.
- Resultado esperado: HTTP 415 con el detalle de los formatos aceptados; la tarea queda sin adjuntos.
- Resultado obtenido: HTTP 415 con el detalle de los formatos aceptados; la tarea quedó sin adjuntos.
- Estado: Aprobado.
- Observaciones: Clase inválida de extensión.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF11
- Capa: API

### CP-ADJ-05

- ID: CP-ADJ-05
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar el rechazo de un archivo que supera el tamaño máximo.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: POST multipart con un archivo de 5 MB más 1 byte.
- Procedimiento: Enviar la petición y consultar los adjuntos de la tarea.
- Resultado esperado: HTTP 413 con el detalle "El archivo supera el tamaño máximo de 5 MB"; la tarea queda sin adjuntos.
- Resultado obtenido: HTTP 413 con el detalle "El archivo supera el tamaño máximo de 5 MB"; sin adjuntos.
- Estado: Aprobado.
- Observaciones: Valor límite superior de tamaño.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF11
- Capa: API

### CP-ADJ-06

- ID: CP-ADJ-06
- Funcionalidad: Archivos adjuntos
- Objetivo: Verificar el rechazo del cuarto archivo adjunto de una misma tarea.
- Precondiciones: Existe una tarea con tres adjuntos válidos.
- Datos de entrada: POST multipart con un cuarto archivo "cuarto.txt".
- Procedimiento: Enviar la petición y consultar los adjuntos de la tarea.
- Resultado esperado: HTTP 409 con el detalle del límite de 3 archivos; la tarea conserva exactamente 3 adjuntos.
- Resultado obtenido: HTTP 409 con el detalle del límite; la tarea conservó exactamente 3 adjuntos.
- Estado: Aprobado.
- Observaciones: Valor límite superior de cantidad de adjuntos.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF11
- Capa: API

### CP-ELI-01

- ID: CP-ELI-01
- Funcionalidad: Eliminar tarea
- Objetivo: Verificar la eliminación de una tarea existente.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: DELETE /api/tasks/{id}.
- Procedimiento: Enviar la petición y luego consultar GET /api/tasks.
- Resultado esperado: HTTP 204 sin cuerpo; la tarea ya no aparece en el listado.
- Resultado obtenido: DELETE 204 sin cuerpo; la tarea dejó de aparecer en el listado.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia válida.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF14
- Capa: API

### CP-ELI-02

- ID: CP-ELI-02
- Funcionalidad: Eliminar tarea
- Objetivo: Verificar la respuesta al intentar eliminar una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 999999.
- Datos de entrada: DELETE /api/tasks/999999.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404 con detalle "Tarea no encontrada".
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF14
- Capa: API

### CP-RES-01

- ID: CP-RES-01
- Funcionalidad: Restaurar tarea
- Objetivo: Verificar la restauración de una tarea eliminada.
- Precondiciones: Existe una tarea eliminada con identificador conocido.
- Datos de entrada: POST /api/tasks/{id}/restore.
- Procedimiento: Enviar la petición y luego consultar GET /api/tasks.
- Resultado esperado: HTTP 200 con la tarea restaurada y presente otra vez en el listado, en la última posición de su columna.
- Resultado obtenido: HTTP 200; la tarea eliminada volvió a estar presente en el listado.
- Estado: Aprobado.
- Observaciones: Flujo normal de deshacer la eliminación.
- Técnica: Caja negra - flujo normal.
- Requisito: RF15
- Capa: API

### CP-RES-02

- ID: CP-RES-02
- Funcionalidad: Restaurar tarea
- Objetivo: Verificar la respuesta al intentar restaurar una tarea que no está eliminada.
- Precondiciones: Existe una tarea activa con identificador conocido.
- Datos de entrada: POST /api/tasks/{id}/restore.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404 con detalle "Tarea no encontrada".
- Estado: Aprobado.
- Observaciones: Clase inválida: la restauración solo aplica a tareas eliminadas.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF15
- Capa: API

### CP-LIS-01

- ID: CP-LIS-01
- Funcionalidad: Listar tareas y persistencia
- Objetivo: Verificar el listado vacío, el orden por estado y posición y la persistencia de las tareas creadas.
- Precondiciones: Base de datos sin tareas y API en ejecución.
- Datos de entrada: Sin datos inicialmente; luego tres tareas válidas en "Pendiente".
- Procedimiento: Consultar GET /api/tasks, crear las tres tareas y volver a consultar.
- Resultado esperado: El primer listado es un arreglo vacío; el segundo contiene las tres tareas en orden de creación, con todas sus propiedades y estados "Pendiente".
- Resultado obtenido: El primer listado fue vacío y el segundo contuvo las tres tareas en orden de creación.
- Estado: Aprobado.
- Observaciones: Verifica el flujo normal de consulta y la persistencia en SQLite.
- Técnica: Caja negra - flujo normal.
- Requisito: RF1, RF2
- Capa: API

### CP-PRI-01

- ID: CP-PRI-01
- Funcionalidad: Prioridad de la tarea
- Objetivo: Verificar el alta de una tarea con la prioridad "Alta".
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Tarea prioritaria", "priority": "Alta"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar el campo priority devuelto.
- Resultado esperado: HTTP 201 con priority "Alta" y title "Tarea prioritaria".
- Resultado obtenido: HTTP 201; la tarea se creó con priority "Alta".
- Estado: Aprobado.
- Observaciones: Clase válida de prioridad con un valor extremo del conjunto.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF16
- Capa: API

### CP-PRI-02

- ID: CP-PRI-02
- Funcionalidad: Prioridad de la tarea
- Objetivo: Verificar que al omitir la prioridad la tarea toma el valor por defecto "Media".
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Tarea sin prioridad"}
- Procedimiento: Enviar POST /api/tasks sin el campo priority y observar el valor devuelto.
- Resultado esperado: HTTP 201 con priority "Media".
- Resultado obtenido: HTTP 201; al omitir priority la tarea quedó con "Media".
- Estado: Aprobado.
- Observaciones: Clase válida por omisión del campo, con el valor por defecto del requisito.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF16
- Capa: API

### CP-PRI-03

- ID: CP-PRI-03
- Funcionalidad: Prioridad de la tarea
- Objetivo: Verificar el rechazo de una prioridad fuera del conjunto permitido.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Prioridad inválida", "priority": "Urgente"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con un mensaje que menciona la prioridad; la tarea no se crea.
- Resultado obtenido: HTTP 422; prioridad fuera del conjunto rechazada y listado sin cambios.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida; verifica que el listado no cambia.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF16
- Capa: API

### CP-PRI-04

- ID: CP-PRI-04
- Funcionalidad: Prioridad de la tarea
- Objetivo: Verificar el cambio de la prioridad de una tarea existente y su registro en el historial.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: PUT con {"title": "Cambiar prioridad", "priority": "Baja"}.
- Procedimiento: Enviar PUT /api/tasks/{id}, consultar la tarea y revisar su actividad.
- Resultado esperado: HTTP 200 con priority "Baja" persistida y la acción "Prioridad cambiada a Baja" en la actividad.
- Resultado obtenido: PUT 200; prioridad "Baja" aplicada y registrada en la actividad.
- Estado: Aprobado.
- Observaciones: Actualización de la prioridad con registro en el historial de la tarea.
- Técnica: Caja negra - flujo normal.
- Requisito: RF16, RF20
- Capa: API

### CP-ASG-01

- ID: CP-ASG-01
- Funcionalidad: Responsable de la tarea
- Objetivo: Verificar el alta de una tarea con responsable y la normalización de los espacios extremos.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Responsable con espacios", "assignee": "  Ana Gómez  "}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar el campo assignee devuelto.
- Resultado esperado: HTTP 201 con assignee "Ana Gómez", sin espacios extremos.
- Resultado obtenido: HTTP 201; los espacios externos se recortaron a "Ana Gómez".
- Estado: Aprobado.
- Observaciones: Clase válida con normalización del responsable.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF17
- Capa: API

### CP-ASG-02

- ID: CP-ASG-02
- Funcionalidad: Responsable de la tarea
- Objetivo: Verificar el rechazo de un responsable que supera los 60 caracteres.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Responsable largo", "assignee": "a" repetido 61 veces}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con un mensaje que menciona el responsable; la tarea no se crea.
- Resultado obtenido: HTTP 422; responsable de 61 caracteres rechazado y listado sin cambios.
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido de longitud del responsable.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF17
- Capa: API

### CP-ASG-03

- ID: CP-ASG-03
- Funcionalidad: Responsable de la tarea
- Objetivo: Verificar la asignación de un responsable a una tarea existente y su registro en el historial.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: PUT con {"title": "Asignar responsable", "assignee": "Luis"}.
- Procedimiento: Enviar PUT /api/tasks/{id}, consultar la tarea y revisar su actividad.
- Resultado esperado: HTTP 200 con assignee "Luis" persistido y la acción "Responsable asignado a Luis" en la actividad.
- Resultado obtenido: PUT 200; responsable "Luis" asignado y registrado en la actividad.
- Estado: Aprobado.
- Observaciones: Actualización del responsable con registro en el historial de la tarea.
- Técnica: Caja negra - flujo normal.
- Requisito: RF17, RF20
- Capa: API

### CP-TAG-01

- ID: CP-TAG-01
- Funcionalidad: Etiquetas
- Objetivo: Verificar el alta de una tarea con etiquetas y su incorporación al catálogo.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Tarea etiquetada", "tags": ["backend", "pruebas"]}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar GET /api/tags.
- Resultado esperado: HTTP 201 con las dos etiquetas en la tarea y presentes en el catálogo.
- Resultado obtenido: HTTP 201; las dos etiquetas quedaron en la tarea y en /api/tags.
- Estado: Aprobado.
- Observaciones: Clase válida de etiquetas; verifica el catálogo además de la tarea.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF18
- Capa: API

### CP-TAG-02

- ID: CP-TAG-02
- Funcionalidad: Etiquetas
- Objetivo: Verificar el rechazo de una tarea con más de cinco etiquetas.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Demasiadas etiquetas", "tags": ["a", "b", "c", "d", "e", "f"]}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 409 con el detalle del límite de 5 etiquetas; no se crea ninguna tarea.
- Resultado obtenido: HTTP 409 con el detalle del límite; no se creó ninguna tarea.
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido de cantidad de etiquetas.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF18
- Capa: API

### CP-TAG-03

- ID: CP-TAG-03
- Funcionalidad: Etiquetas
- Objetivo: Verificar el rechazo de una etiqueta vacía y de una compuesta solo por espacios.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Etiqueta vacía", "tags": [""]} y {"title": "Etiqueta con espacios", "tags": ["   "]}.
- Procedimiento: Enviar POST /api/tasks con cada JSON y consultar el listado.
- Resultado esperado: HTTP 422 en ambos casos con un mensaje que menciona la etiqueta; no se crea ninguna tarea.
- Resultado obtenido: HTTP 422 con la etiqueta vacía y con la de solo espacios.
- Estado: Aprobado.
- Observaciones: Clase inválida y valor límite inferior de la etiqueta.
- Técnica: Caja negra - clase de equivalencia inválida y valor límite.
- Requisito: RF18
- Capa: API

### CP-TAG-04

- ID: CP-TAG-04
- Funcionalidad: Etiquetas
- Objetivo: Verificar el reemplazo completo de las etiquetas y el registro de las altas y bajas.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: PUT con tags ["uno", "dos"] y luego con tags ["dos", "tres"].
- Procedimiento: Enviar los dos PUT, consultar la tarea y revisar su actividad.
- Resultado esperado: HTTP 200 con las etiquetas ["dos", "tres"] y las acciones "Etiqueta eliminada: uno" y "Etiqueta agregada: tres".
- Resultado obtenido: PUT 200; se quitó "uno", se agregó "tres" y ambas acciones quedaron registradas.
- Estado: Aprobado.
- Observaciones: Actualización del conjunto de etiquetas con registro en el historial.
- Técnica: Caja negra - flujo normal.
- Requisito: RF18, RF20
- Capa: API

### CP-ENL-01

- ID: CP-ENL-01
- Funcionalidad: Enlaces
- Objetivo: Verificar el alta de una tarea con un enlace https y su nombre.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Tarea con enlace", "links": [{"url": "https://ejemplo.com/doc", "label": "Documento"}]}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar los enlaces devueltos.
- Resultado esperado: HTTP 201 con un enlace cuya url y label coinciden con los enviados.
- Resultado obtenido: HTTP 201; el enlace https quedó persistido con su nombre.
- Estado: Aprobado.
- Observaciones: Clase válida de enlace con esquema permitido y nombre.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF19
- Capa: API

### CP-ENL-02

- ID: CP-ENL-02
- Funcionalidad: Enlaces
- Objetivo: Verificar el rechazo de enlaces con un esquema distinto de http(s) o sin esquema.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: links [{"url": "ftp://ejemplo.com"}] y [{"url": "ejemplo.com"}].
- Procedimiento: Enviar POST /api/tasks con cada JSON y consultar el listado.
- Resultado esperado: HTTP 422 en ambos casos con un mensaje que menciona http; no se crea ninguna tarea.
- Resultado obtenido: HTTP 422 con ftp:// y con una url sin esquema.
- Estado: Aprobado.
- Observaciones: Clase inválida de esquema del enlace.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF19
- Capa: API

### CP-ENL-03

- ID: CP-ENL-03
- Funcionalidad: Enlaces
- Objetivo: Verificar el rechazo de una tarea con más de cinco enlaces.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Demasiados enlaces", "links": seis enlaces https distintos}.
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 409 con el detalle del límite de 5 enlaces; no se crea ninguna tarea.
- Resultado obtenido: HTTP 409 con el detalle del límite; no se creó ninguna tarea.
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido de cantidad de enlaces.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF19
- Capa: API

### CP-ENL-04

- ID: CP-ENL-04
- Funcionalidad: Enlaces
- Objetivo: Verificar el rechazo de enlaces repetidos en la misma tarea.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Enlaces duplicados", "links": dos enlaces con la misma url}.
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 409 con el detalle del enlace ya agregado; no se crea ninguna tarea.
- Resultado obtenido: HTTP 409 con el detalle del enlace duplicado; no se creó ninguna tarea.
- Estado: Aprobado.
- Observaciones: Clase inválida por repetición de enlaces.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF19
- Capa: API

### CP-HIS-01

- ID: CP-HIS-01
- Funcionalidad: Historial de actividad
- Objetivo: Verificar el registro de la creación y de un movimiento en el historial de la tarea.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: crear la tarea y luego PATCH a "En curso".
- Procedimiento: Consultar la actividad tras el alta, mover la tarea y volver a consultar la actividad.
- Resultado esperado: la actividad incluye "Tarea creada" y, tras el movimiento, "Movida a En curso"; el historial crece.
- Resultado obtenido: La creación dejó "Tarea creada" y el movimiento agregó "Movida a En curso".
- Estado: Aprobado.
- Observaciones: Verifica que las acciones relevantes quedan registradas y ordenadas.
- Técnica: Caja negra - flujo normal.
- Requisito: RF20
- Capa: API

### CP-HIS-02

- ID: CP-HIS-02
- Funcionalidad: Historial de actividad
- Objetivo: Verificar el límite de 20 entradas del historial y su orden descendente.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: alta con 20 subtareas.
- Procedimiento: Enviar POST /api/tasks con las 20 subtareas y observar la actividad devuelta.
- Resultado esperado: HTTP 201 con exactamente 20 entradas, ordenadas de la más nueva a la más antigua, siendo la primera "Subtarea agregada: Paso 20" y sin "Tarea creada".
- Resultado obtenido: El historial devolvió 20 entradas como máximo, con la más reciente primero.
- Estado: Aprobado.
- Observaciones: Valor límite de cantidad del historial y verificación del orden.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF20
- Capa: API

### CP-FIL-01

- ID: CP-FIL-01
- Funcionalidad: Búsqueda y filtros
- Objetivo: Verificar el filtro de tareas por prioridad.
- Precondiciones: Existen tres tareas con prioridad Baja, Alta y Media.
- Datos de entrada: GET /api/tasks?priority=Alta.
- Procedimiento: Consultar con y sin el filtro y comparar el contenido de ambos listados.
- Resultado esperado: el filtro devuelve solo la tarea de prioridad Alta; sin filtro se listan las tres.
- Resultado obtenido: El filtro priority devolvió solo la tarea de prioridad Alta.
- Estado: Aprobado.
- Observaciones: Verifica el parámetro de consulta de prioridad.
- Técnica: Caja negra - flujo normal.
- Requisito: RF21
- Capa: API

### CP-FIL-02

- ID: CP-FIL-02
- Funcionalidad: Búsqueda y filtros
- Objetivo: Verificar el filtro de tareas por etiqueta.
- Precondiciones: Existen una tarea etiquetada y otra sin etiquetas.
- Datos de entrada: GET /api/tasks?tag=backend.
- Procedimiento: Consultar con y sin el filtro y comparar el contenido de ambos listados.
- Resultado esperado: el filtro devuelve solo la tarea con la etiqueta indicada; sin filtro se listan las dos.
- Resultado obtenido: El filtro tag devolvió solo la tarea con la etiqueta indicada.
- Estado: Aprobado.
- Observaciones: Verifica el parámetro de consulta de etiqueta.
- Técnica: Caja negra - flujo normal.
- Requisito: RF21
- Capa: API

### CP-FIL-03

- ID: CP-FIL-03
- Funcionalidad: Búsqueda y filtros
- Objetivo: Verificar la búsqueda por texto en el título y en la descripción, sin distinguir mayúsculas.
- Precondiciones: Existen una tarea con el texto en el título, otra con el texto en la descripción y una tercera ajena.
- Datos de entrada: GET /api/tasks?q=informe.
- Procedimiento: Consultar con el parámetro de búsqueda y comparar los identificadores devueltos.
- Resultado esperado: la búsqueda devuelve las tareas que contienen "informe" en el título o en la descripción, incluyendo coincidencias en mayúsculas, y excluye a la ajena.
- Resultado obtenido: La búsqueda encontró coincidencias en el título y en la descripción, sin distinguir mayúsculas.
- Estado: Aprobado.
- Observaciones: Verifica la búsqueda parcial y la insensibilidad a mayúsculas.
- Técnica: Caja negra - flujo normal.
- Requisito: RF21
- Capa: API

### CP-ORD-01

- ID: CP-ORD-01
- Funcionalidad: Orden del tablero
- Objetivo: Verificar el orden de las tareas por prioridad.
- Precondiciones: Existen tareas de prioridad Baja, Alta y Media.
- Datos de entrada: GET /api/tasks?sort=priority.
- Procedimiento: Consultar con el criterio de orden por prioridad y observar el orden de los títulos.
- Resultado esperado: HTTP 200 con el orden Alta, Media, Baja.
- Resultado obtenido: sort=priority ordenó las tareas como Alta, Media y Baja.
- Estado: Aprobado.
- Observaciones: Verifica el criterio de orden por prioridad dentro del mismo estado.
- Técnica: Caja negra - flujo normal.
- Requisito: RF22
- Capa: API

### CP-ORD-02

- ID: CP-ORD-02
- Funcionalidad: Orden del tablero
- Objetivo: Verificar el rechazo de un criterio de orden fuera del conjunto permitido.
- Precondiciones: API en ejecución.
- Datos de entrada: GET /api/tasks?sort=invalido.
- Procedimiento: Consultar con el criterio inválido y registrar el código de respuesta.
- Resultado esperado: HTTP 422 por error de validación del parámetro de orden.
- Resultado obtenido: HTTP 422 por valor de sort fuera de los permitidos.
- Estado: Aprobado.
- Observaciones: Clase inválida del parámetro de orden.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF22
- Capa: API

### CP-ALT-01

- ID: CP-ALT-01
- Funcionalidad: Alta enriquecida
- Objetivo: Verificar el alta de una tarea con prioridad, responsable, subtareas, etiquetas y enlaces en una sola petición.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Alta enriquecida", "priority": "Alta", "assignee": "Marta", "subtasks": ["Analizar", "Diseñar"], "tags": ["frontend", "backend"], "links": [{"url": "https://ejemplo.com/spec", "label": "Especificación"}]}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar todos los campos enriquecidos.
- Resultado esperado: HTTP 201 con prioridad Alta, responsable Marta, subtask_total 2, dos subtareas, dos etiquetas y un enlace persistidos.
- Resultado obtenido: HTTP 201; prioridad, responsable, 2 subtareas, 2 etiquetas y 1 enlace persistidos en un solo POST.
- Estado: Aprobado.
- Observaciones: Integra en una sola petición las funcionalidades de las nuevas etapas.
- Técnica: Caja negra - flujo normal.
- Requisito: RF16, RF17, RF18, RF19, RF23
- Capa: API

### CP-ALT-02

- ID: CP-ALT-02
- Funcionalidad: Alta enriquecida
- Objetivo: Verificar el rechazo de un alta con más de veinte subtareas.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Demasiadas subtareas", "subtasks": 21 títulos}.
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 409 con el detalle del límite de 20 subtareas; no se crea ninguna tarea.
- Resultado obtenido: HTTP 409 con el detalle del límite; no se creó ninguna tarea.
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido de cantidad de subtareas en el alta.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF23
- Capa: API

### CP-UI-01

- ID: CP-UI-01
- Funcionalidad: Crear tarea desde la interfaz
- Objetivo: Verificar el alta desde el formulario y la actualización visual del tablero.
- Precondiciones: Backend y frontend en ejecución; tablero cargado sin tareas.
- Datos de entrada: Título "Tarea desde interfaz".
- Procedimiento: Escribir el título, presionar "Agregar tarea" y recargar la página.
- Resultado esperado: La tarjeta aparece en "Pendiente", el contador general pasa a 1, el campo de título se limpia y la tarea persiste tras recargar.
- Resultado obtenido: tarjeta visible=True; input=''; resumen='1 tarea'; contador Pendiente='1'; persistió=True.
- Estado: Aprobado.
- Observaciones: Flujo válido de interfaz con integración a la API.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF1, RF2
- Capa: Interfaz

### CP-UI-02

- ID: CP-UI-02
- Funcionalidad: Crear tarea desde la interfaz
- Objetivo: Verificar la validación del formulario ante un título compuesto solo por espacios.
- Precondiciones: Backend y frontend en ejecución; tablero cargado.
- Datos de entrada: "     " en el campo de título.
- Procedimiento: Presionar "Agregar tarea" y observar la interfaz y las peticiones emitidas.
- Resultado esperado: Se muestra el mensaje "El título es obligatorio y no puede contener solo espacios."; no se crea ninguna tarjeta y no se envía ninguna petición POST.
- Resultado obtenido: error='El título es obligatorio y no puede contener solo espacios.'; tarjetas=0; POST=0.
- Estado: Aprobado.
- Observaciones: Clase inválida y valor límite inferior en la interfaz.
- Técnica: Caja negra - clase de equivalencia inválida y valor límite.
- Requisito: RF1
- Capa: Interfaz

### CP-UI-03

- ID: CP-UI-03
- Funcionalidad: Mover tarea desde la interfaz
- Objetivo: Verificar el movimiento de una tarjeta entre columnas.
- Precondiciones: Existe una tarea en la columna "Pendiente".
- Datos de entrada: Arrastrar la tarjeta de "Pendiente" a "En curso".
- Procedimiento: Arrastrar y soltar la tarjeta, observar la interfaz y recargar la página.
- Resultado esperado: La tarjeta se muestra en "En curso", los contadores de las columnas se actualizan, se emite un PATCH con el estado destino y el cambio persiste tras recargar.
- Resultado obtenido: En curso=True; tarjetas en Pendiente=0; contador Pendiente='0'; contador En curso='1'; PATCH=1; persistió=True.
- Estado: Aprobado.
- Observaciones: Flujo de interfaz con integración a la API.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF3
- Capa: Interfaz

### CP-UI-04

- ID: CP-UI-04
- Funcionalidad: Mover y reordenar tarea desde la interfaz
- Objetivo: Verificar el reordenamiento de una tarjeta dentro de su misma columna.
- Precondiciones: Existen dos tareas en "Pendiente" con los títulos "Primera" y "Segunda".
- Datos de entrada: Arrastrar "Segunda" hacia la parte superior de la columna.
- Procedimiento: Realizar el arrastre dentro de la columna y observar el orden resultante y las peticiones emitidas.
- Resultado esperado: Se emite un PATCH con el estado "Pendiente" y posición 0; el orden visible pasa a ser "Segunda" y luego "Primera".
- Resultado obtenido: orden inicial=['Primera', 'Segunda']; PATCH=[{'status': 'Pendiente', 'position': 0}]; orden final=['Segunda', 'Primera']; contador Pendiente='2'.
- Estado: Aprobado.
- Observaciones: Condición de borde de la interfaz: soltar en la misma columna reordena en lugar de no hacer nada.
- Técnica: Caja negra - condición de borde.
- Requisito: RF4
- Capa: Interfaz

### CP-UI-05

- ID: CP-UI-05
- Funcionalidad: Editar tarea desde la interfaz
- Objetivo: Verificar la edición del título y la descripción desde el detalle de la tarea.
- Precondiciones: Existe una tarea visible en el tablero.
- Datos de entrada: Título "Tarea corregida" y descripción "Descripción nueva".
- Procedimiento: Abrir el detalle, presionar "Editar", completar los campos, guardar y volver al tablero.
- Resultado esperado: Se emite un PUT; el detalle muestra los valores nuevos y la tarjeta del tablero refleja el título actualizado.
- Resultado obtenido: PUT=1; título del detalle='Tarea corregida'; descripción='Descripción nueva'; tarjetas=['Tarea corregida'].
- Estado: Aprobado.
- Observaciones: Flujo de interfaz con integración a la API.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF5
- Capa: Interfaz

### CP-UI-06

- ID: CP-UI-06
- Funcionalidad: Checklist desde la interfaz
- Objetivo: Verificar el alta, el marcado y la eliminación de subtareas y el avance mostrado.
- Precondiciones: Existe una tarea abierta en el detalle.
- Datos de entrada: Subtareas "Paso 1" y "Paso 2"; luego marcar "Paso 1" y eliminar "Paso 2".
- Procedimiento: Agregar las dos subtareas, marcar la primera, eliminar la segunda y observar la tarjeta del tablero.
- Resultado esperado: El contador del checklist pasa por 0/2 y 1/2; la tarjeta muestra la insignia "1/2 subtareas"; al eliminar la segunda queda 1/1.
- Resultado obtenido: subtareas listadas=2; contador inicial='0/2'; contador al marcar='1/2'; insignia='1/2 subtareas'; contador al eliminar='1/1'; insignia final='1/1 subtareas'.
- Estado: Aprobado.
- Observaciones: Verifica el avance del checklist tanto en el detalle como en la tarjeta.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF6, RF7, RF8
- Capa: Interfaz

### CP-UI-07

- ID: CP-UI-07
- Funcionalidad: Adjuntos desde la interfaz
- Objetivo: Verificar la subida y la descarga de un archivo desde el detalle de la tarea.
- Precondiciones: Existe una tarea abierta en el detalle, sin adjuntos.
- Datos de entrada: Archivo "acta.txt" de 1 KB.
- Procedimiento: Subir el archivo, observar el detalle y la tarjeta, y descargarlo.
- Resultado esperado: El contador de adjuntos pasa a 1/3, aparece el enlace "acta.txt", la tarjeta muestra la insignia "1 archivo" y la descarga conserva el nombre original.
- Resultado obtenido: contador='1/3'; enlace='acta.txt'; insignia='1 archivo'; nombre descargado='acta.txt'; bytes descargados=1024.
- Estado: Aprobado.
- Observaciones: Flujo de interfaz con integración a la API y al sistema de archivos.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF11, RF12
- Capa: Interfaz

### CP-UI-08

- ID: CP-UI-08
- Funcionalidad: Eliminar y restaurar desde la interfaz
- Objetivo: Verificar la eliminación con confirmación previa y el deshacer.
- Precondiciones: Existe una tarea visible en el tablero.
- Datos de entrada: Botón "Eliminar" de la tarjeta y luego la acción "Deshacer" del aviso.
- Procedimiento: Presionar "Eliminar", confirmar en el diálogo, observar el tablero y presionar "Deshacer".
- Resultado esperado: Aparece el diálogo de confirmación; al confirmar desaparece la tarjeta y se muestra el aviso con "Deshacer"; al usarlo la tarjeta vuelve al tablero.
- Resultado obtenido: diálogo='¿Querés eliminar "Eliminar desde interfaz"? Podés deshacerlo durante unos segundos.'; DELETE=1; tarjetas restantes=0; aviso='Eliminaste "Eliminar desde interfaz".\nDeshacer\n×'; restaurada=True; persistió=True.
- Estado: Aprobado.
- Observaciones: Verifica el borrado lógico desde la interfaz y la restauración.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF14, RF15
- Capa: Interfaz

### CP-UI-09

- ID: CP-UI-09
- Funcionalidad: Alta enriquecida desde la interfaz
- Objetivo: Verificar el alta desde el formulario con prioridad y responsable y su reflejo en la tarjeta.
- Precondiciones: Backend y frontend en ejecución; tablero cargado.
- Datos de entrada: Título "Tarea con prioridad y responsable", prioridad "Alta" y responsable "Ana".
- Procedimiento: Completar el título, seleccionar la prioridad Alta, escribir "Ana" en responsable, presionar "Agregar tarea" y observar la tarjeta.
- Resultado esperado: la tarjeta aparece en "Pendiente", la insignia de prioridad muestra "Alta" y el responsable "Ana".
- Resultado obtenido: insignia='Alta'; responsable='Ana'.
- Estado: Aprobado.
- Observaciones: Verifica que la prioridad y el responsable ingresados en el formulario se reflejan en la tarjeta.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF16, RF17, RF23
- Capa: Interfaz

### CP-UI-10

- ID: CP-UI-10
- Funcionalidad: Búsqueda desde la interfaz
- Objetivo: Verificar que el buscador filtra las tarjetas por texto.
- Precondiciones: Existen dos tareas en el tablero: "Informe de ventas" y "Reunión de equipo".
- Datos de entrada: "informe" en el campo de búsqueda.
- Procedimiento: Escribir "informe" en el buscador y observar las tarjetas visibles y el resumen.
- Resultado esperado: queda una sola tarjeta ("Informe de ventas"), desaparece la ajena y el resumen muestra "1 tarea".
- Resultado obtenido: tarjetas visibles=['Informe de ventas']; resumen='1 tarea'.
- Estado: Aprobado.
- Observaciones: Verifica la búsqueda parcial desde el tablero y la actualización del resumen.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF21
- Capa: Interfaz

### CP-UI-11

- ID: CP-UI-11
- Funcionalidad: Historial desde la interfaz
- Objetivo: Verificar la visualización de la cronología de actividad tras mover una tarea.
- Precondiciones: Existe una tarea en la columna "Pendiente".
- Datos de entrada: Arrastrar la tarjeta de "Pendiente" a "En curso" y abrir el detalle.
- Procedimiento: Mover la tarjeta, abrir su detalle y revisar la cronología.
- Resultado esperado: la tarjeta queda en "En curso" y la cronología muestra al menos una entrada, incluida "Movida a En curso".
- Resultado obtenido: entradas=2; acciones=['Movida a En curso', 'Tarea creada'].
- Estado: Aprobado.
- Observaciones: Verifica que el movimiento queda registrado y visible en el detalle.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF20
- Capa: Interfaz

### CP-CB-01

- ID: CP-CB-01
- Funcionalidad: Validar título en el backend
- Objetivo: Cubrir las decisiones de `clean_title` con un título válido, uno vacío, uno compuesto solo por espacios, uno que supera los 100 caracteres y un valor nulo.
- Precondiciones: Función de validación importable desde `backend/app/schemas.py`.
- Datos de entrada: "  Tarea válida  "; ""; "     "; "a" repetido 101 veces; None.
- Procedimiento: Invocar el validador con cada dato y registrar el valor devuelto o la excepción.
- Resultado esperado: El primer dato devuelve "Tarea válida"; la cadena vacía y la de solo espacios lanzan error de título vacío; la de 101 caracteres lanza error de longitud; el valor nulo lanza el error de título obligatorio.
- Resultado obtenido: válido='Tarea válida'; vacío='El título no puede estar vacío ni contener solo espacios'; espacios='El título no puede estar vacío ni contener solo espacios'; 101='El título no puede superar los 100 caracteres'; None='El título es obligatorio'.
- Estado: Aprobado.
- Observaciones: Cubre las decisiones de normalización, vacío y longitud. La rama del valor nulo es defensiva y no se alcanza desde la API.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF1 y restricciones del título
- Capa: Backend (unidad)

### CP-CB-02

- ID: CP-CB-02
- Funcionalidad: Mover tarea en el repositorio
- Objetivo: Cubrir los caminos de `move_task` con una tarea inexistente, una finalización bloqueada y una finalización permitida.
- Precondiciones: Base SQLite temporal con tareas y subtareas de identificadores conocidos.
- Datos de entrada: (999999, "En curso"), (id con subtarea pendiente, "Terminada") y (id con subtarea completada, "Terminada").
- Procedimiento: Invocar `repository.move_task` con cada combinación y registrar el valor devuelto o la excepción.
- Resultado esperado: El primer caso devuelve None; el segundo lanza PendingSubtasksError; el tercero devuelve la tarea con estado "Terminada".
- Resultado obtenido: inexistente=None; bloqueada=PendingSubtasksError('La tarea tiene subtareas pendientes'); estado bloqueado='Pendiente'; finalizada='Terminada'.
- Estado: Aprobado.
- Observaciones: Cubre las tres decisiones del flujo de movimiento.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF3, RF9
- Capa: Backend (unidad)

### CP-CB-03

- ID: CP-CB-03
- Funcionalidad: Eliminar y restaurar tareas en el repositorio
- Objetivo: Cubrir los caminos de `delete_task` y `restore_task`.
- Precondiciones: Base SQLite temporal con una tarea de identificador conocido.
- Datos de entrada: delete de la tarea existente; delete de 999999; restore de la tarea eliminada; restore de la tarea activa.
- Procedimiento: Invocar ambas funciones y consultar el listado después de cada operación.
- Resultado esperado: El primer delete devuelve True y la tarea sale del listado; el segundo devuelve False; el primer restore devuelve la tarea; el segundo restore devuelve None.
- Resultado obtenido: delete=True; listado tras delete=0; segundo delete=False; delete inexistente=False; restore=ok; listado tras restore=1; segundo restore=None; restore inexistente=None.
- Estado: Aprobado.
- Observaciones: Cubre el borrado lógico y sus dos resultados de restauración.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF14, RF15
- Capa: Backend (unidad)

### CP-CB-04

- ID: CP-CB-04
- Funcionalidad: Límite de adjuntos en el repositorio
- Objetivo: Cubrir la decisión del límite de adjuntos de `create_attachment`.
- Precondiciones: Base SQLite temporal con una tarea de identificador conocido.
- Datos de entrada: Tres altas válidas de adjunto y una cuarta.
- Procedimiento: Invocar `repository.create_attachment` cuatro veces y registrar el resultado de cada llamada.
- Resultado esperado: Las tres primeras devuelven la tarea con el adjunto agregado; la cuarta lanza AttachmentLimitError y la tarea conserva 3 adjuntos.
- Resultado obtenido: acumulado=[1, 2, 3]; cuarta alta=AttachmentLimitError('Una tarea no puede tener más de 3 archivos adjuntos'); adjuntos finales=3.
- Estado: Aprobado.
- Observaciones: Cubre `total >= 3` en sus dos resultados.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF11
- Capa: Backend (unidad)

### CP-CB-05

- ID: CP-CB-05
- Funcionalidad: Reapertura de subtareas en el repositorio
- Objetivo: Cubrir la condición compuesta de reapertura de `update_subtask`.
- Precondiciones: Base SQLite temporal con una tarea terminada y una tarea pendiente.
- Datos de entrada: PATCH con done en falso sobre la tarea terminada y PATCH con done en verdadero sobre la tarea pendiente.
- Procedimiento: Invocar `repository.update_subtask` en ambos casos y observar el estado de la tarea devuelta.
- Resultado esperado: En el primer caso la tarea pasa a "En curso"; en el segundo la tarea conserva "Pendiente".
- Resultado obtenido: estado previo='Terminada'; tras desmarcar='En curso'; pendientes=0; tras marcar='Pendiente'.
- Estado: Aprobado.
- Observaciones: Cubre los dos resultados de la condición `not done and status == Terminada`.
- Técnica: Caja blanca - cobertura de condiciones.
- Requisito: RF9
- Capa: Backend (unidad)

### CP-CB-06

- ID: CP-CB-06
- Funcionalidad: Validar formulario en el frontend
- Objetivo: Cubrir las decisiones de `validateTaskInput` y las ramas de `handleSubmit` con un título vacío, uno de solo espacios, uno de 101 caracteres, una descripción de 501 caracteres, un alta válida y un error de API.
- Precondiciones: Aplicación completa en ejecución; la petición POST se intercepta para simular un error de red.
- Datos de entrada: ""; "     "; "a" repetido 101 veces; descripción de 501 caracteres; "Tarea válida"; "Tarea con error" con la API interceptada para responder HTTP 500.
- Procedimiento: Ejecutar el formulario real con cada dato y observar el mensaje y las peticiones emitidas.
- Resultado esperado: El título vacío y el de solo espacios muestran el error de título y no emiten la petición; el de 101 caracteres muestra el error de longitud; el de descripción larga muestra el error de descripción; el válido emite la petición y limpia el campo; con la API fallando se muestra el mensaje devuelto.
- Resultado obtenido: vacío='El título es obligatorio y no puede contener solo espacios.'; espacios='El título es obligatorio y no puede contener solo espacios.'; len(101)=101; título largo='El título no puede superar los 100 caracteres.'; descripción larga='La descripción no puede superar los 500 caracteres.'; POST inválidos=0; error API='Error simulado de red'; tarjetas tras error=0; alta válida=True; input tras alta=''; POST totales=2.
- Estado: Aprobado.
- Observaciones: El atributo `maxLength` limita el ingreso manual; los valores fuera de límite se cargan programáticamente para ejercitar las ramas de validación.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF1
- Capa: Frontend (unidad)

### CP-CB-07

- ID: CP-CB-07
- Funcionalidad: Mover por arrastre en el frontend
- Objetivo: Cubrir la decisión de `handleDrop` y el cálculo de `dropIndex`.
- Precondiciones: Aplicación completa en ejecución con dos tareas en la columna Pendiente.
- Datos de entrada: Soltar una tarea sobre su misma columna; soltar una tarea sobre otra columna; soltar un identificador inválido.
- Procedimiento: Realizar los arrastres con eventos de arrastre reales y registrar las peticiones PATCH y las posiciones enviadas.
- Resultado esperado: El arrastre en la misma columna emite un PATCH con posición 0 y reordena; el arrastre a otra columna emite un PATCH con el estado destino; el identificador inválido no emite ninguna petición.
- Resultado obtenido: orden inicial=['Alfa', 'Beta']; PATCH reorden=[{'status': 'Pendiente', 'position': 0}]; orden final=['Beta', 'Alfa']; PATCH movimiento=[{'status': 'Pendiente', 'position': 0}, {'status': 'En curso', 'position': 0}]; En curso=True; PATCH totales=2; tarjetas en Terminada=0.
- Estado: Aprobado.
- Observaciones: Cubre los dos resultados de `!Number.isInteger(taskId) || taskId <= 0` y el valor devuelto por `dropIndex`.
- Técnica: Caja blanca - cobertura de condiciones.
- Requisito: RF3, RF4
- Capa: Frontend (unidad)

## Resumen de cobertura

| Funcionalidad | Casos de caja negra | Casos de caja blanca | Total |
|---------------|---------------------|----------------------|-------|
| Crear tarea | 11 | 2 | 13 |
| Mover y reordenar tarea | 7 | 2 | 9 |
| Editar tarea | 4 | 0 | 4 |
| Checklist de subtareas | 5 | 1 | 6 |
| Control de finalización | 4 | 0 | 4 |
| Fecha límite y vencimiento | 2 | 0 | 2 |
| Archivos adjuntos | 7 | 1 | 8 |
| Eliminar y restaurar tarea | 5 | 1 | 6 |
| Listar tareas | 1 | 0 | 1 |
| Prioridad | 4 | 0 | 4 |
| Responsable | 3 | 0 | 3 |
| Etiquetas | 4 | 0 | 4 |
| Enlaces | 4 | 0 | 4 |
| Historial de actividad | 3 | 0 | 3 |
| Búsqueda y filtros | 4 | 0 | 4 |
| Orden del tablero | 2 | 0 | 2 |
| Alta enriquecida | 3 | 0 | 3 |
| Total | 73 | 7 | 80 |

Cada caso se contabiliza en una sola fila, según su funcionalidad principal en la matriz de trazabilidad. Algunos casos cubren además otras funcionalidades o requisitos, por ejemplo `CP-UI-06`, `CP-CB-02` y `CP-CB-05` en el control de finalización, sin alterar el total.

| Técnica principal | Casos |
|-------------------|-------|
| Clases de equivalencia y valores límite (caja negra) | CP-CRE-01 a CP-CRE-09, CP-MOV-01 a CP-MOV-05, CP-EDI-01 a CP-EDI-03, CP-FEC-01, CP-FEC-02, CP-ADJ-04 a CP-ADJ-06, CP-UI-02, CP-PRI-01 a CP-PRI-03, CP-ASG-01, CP-ASG-02, CP-TAG-02, CP-TAG-03, CP-ENL-02 a CP-ENL-04, CP-HIS-02, CP-ORD-02, CP-ALT-02 |
| Flujos normales y reglas de negocio sobre la API (caja negra) | CP-SUB-01 a CP-SUB-04, CP-BLO-01 a CP-BLO-04, CP-ADJ-01 a CP-ADJ-03, CP-ELI-01, CP-ELI-02, CP-RES-01, CP-RES-02, CP-LIS-01, CP-PRI-04, CP-ASG-03, CP-TAG-01, CP-TAG-04, CP-ENL-01, CP-HIS-01, CP-FIL-01 a CP-FIL-03, CP-ORD-01, CP-ALT-01 |
| Flujos normales sobre la interfaz (caja negra) | CP-UI-01, CP-UI-03 a CP-UI-11 |
| Caja blanca - decisiones y condiciones | CP-CB-01 a CP-CB-07 |

Algunos casos aplican más de una técnica, por lo que la agrupación refleja la técnica principal de cada uno y suma los 80 casos únicos.

## Conclusión de la etapa

Se diseñaron 80 casos de prueba que cubren las funcionalidades del sistema y los requisitos RF1 a RF23, incluidas las restricciones de título, descripción, fecha límite, adjuntos, cantidad de archivos, prioridad, responsable, etiquetas, enlaces, historial, búsqueda, orden y alta enriquecida. La caja negra aporta casos de clases de equivalencia, valores límite y reglas de negocio sobre la API y la interfaz; la caja blanca permite cubrir las decisiones y condiciones principales del backend y del frontend. El conjunto queda listo para su ejecución y registro en la Etapa 6.

## Próxima etapa

La Etapa 6 consistirá en ejecutar estos casos sobre el sistema desarrollado, registrar el resultado obtenido y el estado de cada uno, y documentar los defectos que aparezcan para su seguimiento en la Etapa 7.
