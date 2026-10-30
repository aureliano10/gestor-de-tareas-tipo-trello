# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 29/10/2026

# Etapa 5 - Diseño de casos de prueba

## Objetivo de la etapa

Diseñar los casos de prueba a partir de los requisitos y de las funcionalidades implementadas, aplicando técnicas de caja negra y de caja blanca, y dejando preparada la información necesaria para ejecutar las pruebas en la Etapa 6.

## Alcance y criterios

Esta etapa es de **diseño**. Los casos se documentan con todos sus campos. La ejecución y el registro de resultados se realizaron en la Etapa 6; por ese motivo, los campos `Resultado obtenido` y `Estado` reflejan los resultados de esa ejecución.

Se aplican las siguientes técnicas:

- **Caja negra:** clases de equivalencia, análisis de valores límite y datos válidos e inválidos.
- **Caja blanca:** análisis de instrucciones, decisiones, condiciones y caminos de ejecución sobre fragmentos seleccionados del backend y del frontend.

Criterios generales:

- Cada caso tiene un identificador único y evalúa una sola situación.
- Los datos válidos e inválidos se derivan de las restricciones de la Etapa 1.
- Los casos de interfaz se ejecutan sobre el sistema completo; los de caja blanca sobre la unidad indicada.
- La cobertura indicada es la cobertura esperada del diseño; la cobertura real se medirá al ejecutar las pruebas.

## Funcionalidades y requisitos cubiertos

| Funcionalidad | Requisitos asociados | Casos |
|---------------|----------------------|-------|
| Crear tarea | RF1, RF2 y restricciones del título | CP-CRE-01 a CP-CRE-08, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-04 |
| Mover tarea | RF3 y restricción de estados válidos | CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-05 |
| Eliminar tarea | RF4 | CP-ELI-01, CP-ELI-02, CP-UI-05, CP-CB-03 |
| Listar tareas y persistencia | RF1, RF2 y persistencia | CP-LIS-01 |

## Caja negra

### Clases de equivalencia

| Entrada | Clase | Tipo | Valores representativos | Casos |
|---------|-------|------|-------------------------|-------|
| Título | Cadena de 1 a 100 caracteres después de quitar espacios extremos, no vacía | Válida | "Preparar informe" | CP-CRE-01 |
| Título | Cadena con espacios extremos que queda válida al normalizarse | Válida | "  Revisar pruebas  " | CP-CRE-07 |
| Título | Cadena con acentos y símbolos dentro del límite | Válida | "Revisión de señalización #1 – ñandú" | CP-CRE-08 |
| Título | Cadena vacía | Inválida | "" | CP-CRE-05 |
| Título | Cadena compuesta solo por espacios | Inválida | "     " | CP-CRE-06 |
| Título | Cadena de más de 100 caracteres después de normalizar | Inválida | 101 caracteres | CP-CRE-04 |
| Estado | Uno de los tres valores permitidos | Válido | "Pendiente", "En curso", "Terminada" | CP-MOV-01 |
| Estado | Cualquier otro valor | Inválido | "Finalizada", "pendiente", "" | CP-MOV-02 |
| Identificador | Entero positivo existente | Válido | id de una tarea creada | CP-MOV-01, CP-ELI-01 |
| Identificador | Entero positivo inexistente | Inválido | 99999 | CP-MOV-03, CP-ELI-02 |
| Identificador | Valor no numérico | Inválido | "abc" | CP-MOV-04 |

### Análisis de valores límite

| Variable | Límite | Valores considerados | Casos |
|----------|--------|----------------------|-------|
| Longitud del título | Inferior | 0 caracteres útil (vacío o solo espacios) y 1 carácter | CP-CRE-05, CP-CRE-06, CP-CRE-02 |
| Longitud del título | Superior | 99 caracteres (válido, cubierto por la clase válida), 100 (máximo válido) y 101 (fuera de límite) | CP-CRE-01, CP-CRE-03, CP-CRE-04 |
| Estado | Conjunto de valores permitidos | Coincidencia exacta con uno de los tres estados y un valor fuera del conjunto | CP-MOV-01, CP-MOV-02 |
| Identificador | Existencia | Tarea existente, tarea inexistente y valor no numérico | CP-MOV-01, CP-MOV-03, CP-MOV-04, CP-ELI-01, CP-ELI-02 |

## Caja blanca

### Unidades analizadas

| Unidad | Ubicación | Motivo de selección |
|--------|-----------|---------------------|
| `validate_title` | `backend/app/schemas.py:17-27` | Concentra las decisiones de validación del título. |
| `update_task_status` | `backend/app/repository.py:36-43` y `backend/app/routers/tasks.py:18-25` | Contiene la decisión entre tarea existente e inexistente. |
| `delete_task` | `backend/app/repository.py:46-49` y `backend/app/routers/tasks.py:28-34` | Contiene la decisión de eliminación exitosa o inexistente. |
| `handleSubmit` | `frontend/src/components/TaskForm.jsx:10-33` | Contiene las validaciones previas al envío. |
| `handleDrop` | `frontend/src/components/Column.jsx:16-24` | Contiene una condición compuesta para decidir si mueve la tarea. |

### Modelo de decisiones y caminos

| Unidad | Decisión o condición | Resultado | Camino | Casos asociados |
|--------|----------------------|-----------|--------|-----------------|
| `validate_title` | `value is None` | Lanza error de título obligatorio | Defensivo, no alcanzable desde la API | Sin caso funcional |
| `validate_title` | `not clean_title` | Lanza error de título vacío | Inválido | CP-CB-01 |
| `validate_title` | `len(clean_title) > 100` | Lanza error de longitud | Inválido | CP-CB-01 |
| `validate_title` | Ninguna condición anterior | Devuelve el título recortado | Válido | CP-CB-01, CP-CRE-01 |
| `update_task_status` | `cursor.rowcount == 0` | Devuelve `None` | Inexistente | CP-CB-02, CP-MOV-03 |
| `update_task_status` | `task is None` en el router | Responde HTTP 404 | Inexistente | CP-CB-02, CP-MOV-03 |
| `update_task_status` | `rowcount > 0` y tarea encontrada | Devuelve la tarea actualizada | Existente | CP-CB-02, CP-MOV-01 |
| `delete_task` | `cursor.rowcount > 0` | Devuelve `True` | Existente | CP-CB-03, CP-ELI-01 |
| `delete_task` | `cursor.rowcount == 0` | Devuelve `False` y el router responde 404 | Inexistente | CP-CB-03, CP-ELI-02 |
| `handleSubmit` | `!cleanTitle` | Muestra error y no envía | Inválido | CP-CB-04, CP-UI-02 |
| `handleSubmit` | `cleanTitle.length > 100` | Muestra error y no envía | Inválido | CP-CB-04 |
| `handleSubmit` | Validaciones superadas | Invoca `onCreate` y limpia el campo | Válido | CP-CB-04, CP-UI-01 |
| `handleSubmit` | `catch` de la llamada a `onCreate` | Muestra el error recibido | Error de API | CP-CB-04 |
| `handleDrop` | `Number.isInteger(taskId) && taskId > 0` | Identificador válido | Condición compuesta | CP-CB-05 |
| `handleDrop` | `!alreadyInColumn` | Permite mover solo si cambia de columna | Condición compuesta | CP-CB-05, CP-UI-04 |

La rama `value is None` de `validate_title` es una defensa interna: Pydantic rechaza un valor nulo o ausente antes de ejecutar el validador, por lo que no es alcanzable a través de la API. Se documenta como camino no cubierto por un caso funcional y no se considera un defecto.

### Estimación de cobertura

| Unidad | Cobertura de decisiones | Cobertura de condiciones | Observación |
|--------|-------------------------|--------------------------|-------------|
| `validate_title` | 100% de las decisiones alcanzables | No aplica | La decisión defensiva `value is None` no es alcanzable desde la API. |
| `update_task_status` | 100% | No aplica | Se cubren tarea existente e inexistente. |
| `delete_task` | 100% | No aplica | Se cubren eliminación exitosa e inexistente. |
| `handleSubmit` | 100% de las decisiones de validación | No aplica | El límite de 100 también se controla con `maxLength` en el formulario. |
| `handleDrop` | 100% de la decisión compuesta | 100% de las condiciones simples | Se cubren identificador inválido, misma columna y columna distinta. |

La cobertura real se verificó durante la ejecución de la Etapa 6; las pruebas unitarias formales se incorporarán en la Etapa 8.

## Matriz de trazabilidad y resumen de casos

| ID | Funcionalidad | Técnica principal | Requisito o restricción | Capa | Estado |
|----|---------------|-------------------|-------------------------|------|--------|
| CP-CRE-01 | Crear tarea | Clase de equivalencia válida | RF1, RF2 | API | Aprobado |
| CP-CRE-02 | Crear tarea | Valor límite inferior | RF1, RF2 | API | Aprobado |
| CP-CRE-03 | Crear tarea | Valor límite superior | RF1, RF2 | API | Aprobado |
| CP-CRE-04 | Crear tarea | Valor límite superior inválido | RF1 | API | Aprobado |
| CP-CRE-05 | Crear tarea | Clase de equivalencia inválida | RF1 | API | Aprobado |
| CP-CRE-06 | Crear tarea | Clase inválida y valor límite | RF1 | API | Aprobado |
| CP-CRE-07 | Crear tarea | Clase válida con normalización | RF1, RF2 | API | Aprobado |
| CP-CRE-08 | Crear tarea | Clase válida con caracteres especiales | RF1, RF2 | API | Aprobado |
| CP-MOV-01 | Mover tarea | Clase de equivalencia válida | RF3 | API | Aprobado |
| CP-MOV-02 | Mover tarea | Clase de equivalencia inválida | RF3 | API | Aprobado |
| CP-MOV-03 | Mover tarea | Identificador inexistente | RF3 | API | Aprobado |
| CP-MOV-04 | Mover tarea | Identificador no numérico | RF3 | API | Aprobado |
| CP-ELI-01 | Eliminar tarea | Clase de equivalencia válida | RF4 | API | Aprobado |
| CP-ELI-02 | Eliminar tarea | Identificador inexistente | RF4 | API | Aprobado |
| CP-LIS-01 | Listar tareas | Flujo normal y persistencia | RF1, RF2 | API | Aprobado |
| CP-UI-01 | Crear tarea | Flujo válido de interfaz | RF1, RF2 | Interfaz | Aprobado |
| CP-UI-02 | Crear tarea | Clase inválida y valor límite | RF1 | Interfaz | Aprobado |
| CP-UI-03 | Mover tarea | Flujo de interfaz | RF3 | Interfaz | Aprobado |
| CP-UI-04 | Mover tarea | Condición de borde de interfaz | RF3 | Interfaz | Aprobado |
| CP-UI-05 | Eliminar tarea | Flujo de interfaz | RF4 | Interfaz | Aprobado |
| CP-CB-01 | Validar título | Caja blanca - decisiones | RF1 y restricciones del título | Backend (unidad) | Aprobado |
| CP-CB-02 | Actualizar estado | Caja blanca - decisiones | RF3 | Backend (unidad) | Aprobado |
| CP-CB-03 | Eliminar tarea | Caja blanca - decisiones | RF4 | Backend (unidad) | Aprobado |
| CP-CB-04 | Validar formulario | Caja blanca - decisiones | RF1 | Frontend (unidad) | Aprobado |
| CP-CB-05 | Mover por arrastre | Caja blanca - condiciones | RF3 | Frontend (unidad) | Aprobado |

## Trazabilidad por requisito

| Requisito o restricción | Casos que lo cubren |
|-------------------------|---------------------|
| RF1: registrar una tarea | CP-CRE-01 a CP-CRE-08, CP-LIS-01, CP-UI-01, CP-UI-02, CP-CB-01, CP-CB-04 |
| RF2: estado inicial Pendiente | CP-CRE-01, CP-CRE-02, CP-CRE-03, CP-CRE-07, CP-CRE-08, CP-LIS-01, CP-UI-01 |
| RF3: actualizar el estado | CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-05 |
| RF4: eliminar una tarea | CP-ELI-01, CP-ELI-02, CP-UI-05, CP-CB-03 |
| Título obligatorio, no vacío y de hasta 100 caracteres | CP-CRE-02 a CP-CRE-08, CP-UI-02, CP-CB-01, CP-CB-04 |
| Existencia de un solo estado válido por tarea | CP-CRE-01, CP-CRE-02, CP-CRE-03, CP-MOV-01 a CP-MOV-04, CP-UI-03, CP-UI-04, CP-CB-02, CP-CB-05 |
| Persistencia de los cambios | CP-LIS-01, CP-UI-01, CP-UI-03, CP-UI-05, CP-CB-02, CP-CB-03 |

## Fichas de casos de prueba

### CP-CRE-01

- ID: CP-CRE-01
- Funcionalidad: Crear tarea
- Objetivo: Verificar el alta de una tarea con un título válido y la asignación del estado inicial.
- Precondiciones: API en ejecución y base de datos SQLite accesible.
- Datos de entrada: {"title": "Preparar informe"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y luego consultar GET /api/tasks.
- Resultado esperado: HTTP 201, con id, title "Preparar informe", status "Pendiente" y created_at válido; la tarea aparece en el listado.
- Resultado obtenido: HTTP 201; respuesta={"id": 33, "title": "Preparar informe", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.397774Z"}; listado=[{"id": 33, "title": "Preparar informe", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.397774Z"}].
- Estado: Aprobado.
- Observaciones: Clase de equivalencia válida típica. Se verifica además RF2.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2.
- Capa: API.

### CP-CRE-02

- ID: CP-CRE-02
- Funcionalidad: Crear tarea
- Objetivo: Verificar el límite inferior de longitud del título con un carácter.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "A"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y registrar la respuesta.
- Resultado esperado: HTTP 201, title "A" y status "Pendiente".
- Resultado obtenido: HTTP 201; respuesta={"id": 34, "title": "A", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.503768Z"}; listado=[{"id": 34, "title": "A", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.503768Z"}].
- Estado: Aprobado.
- Observaciones: Valor límite inferior válido.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1, RF2.
- Capa: API.

### CP-CRE-03

- ID: CP-CRE-03
- Funcionalidad: Crear tarea
- Objetivo: Verificar el límite superior válido de longitud del título con 100 caracteres.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "a" repetido 100 veces}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y medir la longitud del título devuelto.
- Resultado esperado: HTTP 201; el título devuelto tiene exactamente 100 caracteres y estado "Pendiente".
- Resultado obtenido: HTTP 201; respuesta={"id": 35, "title": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.600768Z"}; listado=[{"id": 35, "title": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.600768Z"}].
- Estado: Aprobado.
- Observaciones: Valor límite superior válido. El valor 99 queda cubierto por la clase válida.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1, RF2.
- Capa: API.

### CP-CRE-04

- ID: CP-CRE-04
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título que supera el máximo permitido.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "a" repetido 101 veces}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con el mensaje "El título no puede superar los 100 caracteres"; la tarea no se crea.
- Resultado obtenido: HTTP 422; respuesta={"detail": [{"type": "value_error", "loc": ["body", "title"], "msg": "Value error, El título no puede superar los 100 caracteres", "input": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "ctx": {"error": {}}}]}; listado=[].
- Estado: Aprobado.
- Observaciones: Valor límite superior inválido.
- Técnica: Caja negra - análisis de valores límite.
- Requisito: RF1.
- Capa: API.

### CP-CRE-05

- ID: CP-CRE-05
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título vacío.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": ""}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con mensaje de título vacío; la tarea no se crea.
- Resultado obtenido: HTTP 422; respuesta={"detail": [{"type": "value_error", "loc": ["body", "title"], "msg": "Value error, El título no puede estar vacío ni contener solo espacios", "input": "", "ctx": {"error": {}}}]}; listado=[].
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF1.
- Capa: API.

### CP-CRE-06

- ID: CP-CRE-06
- Funcionalidad: Crear tarea
- Objetivo: Verificar el rechazo de un título compuesto solo por espacios.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "     "}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y consultar el listado.
- Resultado esperado: HTTP 422 con el mensaje "El título no puede estar vacío ni contener solo espacios"; la tarea no se crea.
- Resultado obtenido: HTTP 422; respuesta={"detail": [{"type": "value_error", "loc": ["body", "title"], "msg": "Value error, El título no puede estar vacío ni contener solo espacios", "input": "     ", "ctx": {"error": {}}}]}; listado=[].
- Estado: Aprobado.
- Observaciones: Clase inválida y valor límite inferior después de quitar espacios.
- Técnica: Caja negra - clase de equivalencia inválida y valor límite.
- Requisito: RF1.
- Capa: API.

### CP-CRE-07

- ID: CP-CRE-07
- Funcionalidad: Crear tarea
- Objetivo: Verificar la normalización de espacios al inicio y al final del título.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "  Revisar pruebas  "}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y observar el título almacenado.
- Resultado esperado: HTTP 201 con title "Revisar pruebas", sin espacios extremos, y status "Pendiente".
- Resultado obtenido: HTTP 201; respuesta={"id": 36, "title": "Revisar pruebas", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.927885Z"}; listado=[{"id": 36, "title": "Revisar pruebas", "status": "Pendiente", "created_at": "2026-10-30T03:05:35.927885Z"}].
- Estado: Aprobado.
- Observaciones: Clase válida con normalización.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2.
- Capa: API.

### CP-CRE-08

- ID: CP-CRE-08
- Funcionalidad: Crear tarea
- Objetivo: Verificar la aceptación de acentos y símbolos dentro del límite de longitud.
- Precondiciones: API en ejecución y base de datos accesible.
- Datos de entrada: {"title": "Revisión de señalización #1 – ñandú"}
- Procedimiento: Enviar POST /api/tasks con el JSON indicado y comparar el título devuelto.
- Resultado esperado: HTTP 201 con el título idéntico al enviado y status "Pendiente".
- Resultado obtenido: HTTP 201; respuesta={"id": 37, "title": "Revisión de señalización #1 – ñandú", "status": "Pendiente", "created_at": "2026-10-30T03:05:36.019551Z"}; listado=[{"id": 37, "title": "Revisión de señalización #1 – ñandú", "status": "Pendiente", "created_at": "2026-10-30T03:05:36.019551Z"}].
- Estado: Aprobado.
- Observaciones: Clase válida con caracteres especiales.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF1, RF2.
- Capa: API.

### CP-MOV-01

- ID: CP-MOV-01
- Funcionalidad: Mover tarea
- Objetivo: Verificar las transiciones válidas entre los tres estados.
- Precondiciones: Existe una tarea en estado "Pendiente" con identificador conocido.
- Datos de entrada: PATCH {"status": "En curso"} y luego PATCH {"status": "Terminada"} sobre la misma tarea.
- Procedimiento: Crear la tarea, actualizar a "En curso", consultar, actualizar a "Terminada" y volver a consultar.
- Resultado esperado: HTTP 200 en cada actualización; los estados quedan persistidos y el id y el título no cambian.
- Resultado obtenido: En curso: HTTP 200 (En curso); Terminada: HTTP 200 (Terminada); persistido=Terminada.
- Estado: Aprobado.
- Observaciones: Cubre los tres valores válidos del estado y las transiciones permitidas.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF3.
- Capa: API.

### CP-MOV-02

- ID: CP-MOV-02
- Funcionalidad: Mover tarea
- Objetivo: Verificar el rechazo de un estado no permitido.
- Precondiciones: Existe una tarea con estado conocido.
- Datos de entrada: PATCH {"status": "Finalizada"}.
- Procedimiento: Enviar PATCH /api/tasks/{id}/status y luego consultar la tarea.
- Resultado esperado: HTTP 422; la tarea conserva su estado anterior.
- Resultado obtenido: HTTP 422; respuesta={"detail": [{"type": "literal_error", "loc": ["body", "status"], "msg": "Input should be 'Pendiente', 'En curso' or 'Terminada'", "input": "Finalizada", "ctx": {"expected": "'Pendiente', 'En curso' or 'Terminada'"}}]}; persistido=Pendiente.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida. También aplica a "pendiente" en minúsculas y a cadena vacía.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3.
- Capa: API.

### CP-MOV-03

- ID: CP-MOV-03
- Funcionalidad: Mover tarea
- Objetivo: Verificar la respuesta al intentar mover una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 99999.
- Datos de entrada: PATCH /api/tasks/99999/status con {"status": "En curso"}.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404; respuesta={"detail": "Tarea no encontrada"}.
- Estado: Aprobado.
- Observaciones: Identificador válido como número pero inexistente.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3.
- Capa: API.

### CP-MOV-04

- ID: CP-MOV-04
- Funcionalidad: Mover tarea
- Objetivo: Verificar el rechazo de un identificador no numérico en la ruta.
- Precondiciones: API en ejecución.
- Datos de entrada: PATCH /api/tasks/abc/status con {"status": "En curso"}.
- Procedimiento: Enviar la petición y registrar el código de respuesta.
- Resultado esperado: HTTP 422 por error de validación del parámetro de ruta; no se modifica ninguna tarea.
- Resultado obtenido: HTTP 422; respuesta={"detail": [{"type": "int_parsing", "loc": ["path", "task_id"], "msg": "Input should be a valid integer, unable to parse string as an integer", "input": "abc"}]}.
- Estado: Aprobado.
- Observaciones: Clase inválida de identificador.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF3.
- Capa: API.

### CP-ELI-01

- ID: CP-ELI-01
- Funcionalidad: Eliminar tarea
- Objetivo: Verificar la eliminación de una tarea existente.
- Precondiciones: Existe una tarea con identificador conocido.
- Datos de entrada: DELETE /api/tasks/{id}.
- Procedimiento: Enviar la petición y luego consultar GET /api/tasks.
- Resultado esperado: HTTP 204 sin cuerpo; la tarea ya no aparece en el listado.
- Resultado obtenido: HTTP 204; cuerpo=''; listado=[].
- Estado: Aprobado.
- Observaciones: Clase de equivalencia válida.
- Técnica: Caja negra - clase de equivalencia válida.
- Requisito: RF4.
- Capa: API.

### CP-ELI-02

- ID: CP-ELI-02
- Funcionalidad: Eliminar tarea
- Objetivo: Verificar la respuesta al intentar eliminar una tarea inexistente.
- Precondiciones: No existe una tarea con identificador 99999.
- Datos de entrada: DELETE /api/tasks/99999.
- Procedimiento: Enviar la petición y registrar el código y el detalle de la respuesta.
- Resultado esperado: HTTP 404 con detalle "Tarea no encontrada".
- Resultado obtenido: HTTP 404; respuesta={"detail": "Tarea no encontrada"}.
- Estado: Aprobado.
- Observaciones: Clase de equivalencia inválida.
- Técnica: Caja negra - clase de equivalencia inválida.
- Requisito: RF4.
- Capa: API.

### CP-LIS-01

- ID: CP-LIS-01
- Funcionalidad: Listar tareas y persistencia
- Objetivo: Verificar el listado vacío y la persistencia de las tareas creadas.
- Precondiciones: Base de datos sin tareas y API en ejecución.
- Datos de entrada: Sin datos inicialmente; luego dos tareas válidas.
- Procedimiento: Consultar GET /api/tasks, crear dos tareas y volver a consultar.
- Resultado esperado: El primer listado es un arreglo vacío; el segundo contiene las dos tareas ordenadas por id y con todos sus campos.
- Resultado obtenido: vacío HTTP 200 []; con datos HTTP 200 [{"id": 41, "title": "Primera tarea", "status": "Pendiente", "created_at": "2026-10-30T03:05:36.699928Z"}, {"id": 42, "title": "Segunda tarea", "status": "Pendiente", "created_at": "2026-10-30T03:05:36.740958Z"}].
- Estado: Aprobado.
- Observaciones: Verifica el flujo normal de consulta y la persistencia en SQLite.
- Técnica: Caja negra - flujo normal.
- Requisito: RF1, RF2 y persistencia.
- Capa: API.

### CP-UI-01

- ID: CP-UI-01
- Funcionalidad: Crear tarea desde la interfaz
- Objetivo: Verificar el alta desde el formulario y la actualización visual del tablero.
- Precondiciones: Backend y frontend en ejecución; tablero cargado.
- Datos de entrada: Título "Tarea desde interfaz".
- Procedimiento: Escribir el título, presionar "Agregar" y recargar la página.
- Resultado esperado: La tarjeta aparece en "Pendiente", el contador aumenta, el campo se limpia y la tarea persiste tras recargar.
- Resultado obtenido: Tarjeta visible=True; input=''; contador=1; persistió=True.
- Estado: Aprobado.
- Observaciones: Flujo válido de interfaz.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF1, RF2.
- Capa: Interfaz.

### CP-UI-02

- ID: CP-UI-02
- Funcionalidad: Crear tarea desde la interfaz
- Objetivo: Verificar la validación del formulario ante un título vacío o compuesto solo por espacios.
- Precondiciones: Backend y frontend en ejecución; tablero cargado.
- Datos de entrada: "     " en el campo de título.
- Procedimiento: Presionar "Agregar" y observar la interfaz y la pestaña de red.
- Resultado esperado: Se muestra el mensaje "El título es obligatorio y no puede contener solo espacios."; no se crea la tarjeta y no se envía la petición a la API.
- Resultado obtenido: error='El título es obligatorio y no puede contener solo espacios.'; tarjetas=0; POST=0.
- Estado: Aprobado.
- Observaciones: Clase inválida y valor límite inferior en la interfaz.
- Técnica: Caja negra - clase de equivalencia inválida y valor límite.
- Requisito: RF1.
- Capa: Interfaz.

### CP-UI-03

- ID: CP-UI-03
- Funcionalidad: Mover tarea desde la interfaz
- Objetivo: Verificar el movimiento de una tarjeta entre columnas.
- Precondiciones: Existe una tarea en la columna "Pendiente".
- Datos de entrada: Arrastrar la tarjeta de "Pendiente" a "En curso".
- Procedimiento: Arrastrar y soltar la tarjeta, observar la interfaz y recargar la página.
- Resultado esperado: La tarjeta se muestra en "En curso", los contadores se actualizan, la API responde 200 y el cambio persiste tras recargar.
- Resultado obtenido: En curso=True; Pendiente=0; PATCH=1; persistió=True.
- Estado: Aprobado.
- Observaciones: Flujo de interfaz con integración a la API.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF3.
- Capa: Interfaz.

### CP-UI-04

- ID: CP-UI-04
- Funcionalidad: Mover tarea desde la interfaz
- Objetivo: Verificar que soltar una tarjeta en su misma columna no genera un movimiento.
- Precondiciones: Existe una tarea en la columna "Pendiente".
- Datos de entrada: Arrastrar y soltar la tarjeta dentro de la misma columna.
- Procedimiento: Realizar el arrastre dentro de la columna y observar la pestaña de red.
- Resultado esperado: La tarjeta permanece en su lugar, no se envía PATCH y no se muestra ningún error.
- Resultado obtenido: PATCH=0; tarjeta en Pendiente=1.
- Estado: Aprobado.
- Observaciones: Condición de borde de la interfaz.
- Técnica: Caja negra - condición de borde.
- Requisito: RF3.
- Capa: Interfaz.

### CP-UI-05

- ID: CP-UI-05
- Funcionalidad: Eliminar tarea desde la interfaz
- Objetivo: Verificar la eliminación de una tarjeta desde el tablero.
- Precondiciones: Existe una tarea visible en el tablero.
- Datos de entrada: Presionar el botón "Eliminar" de la tarjeta.
- Procedimiento: Presionar "Eliminar", observar la interfaz y recargar la página.
- Resultado esperado: La tarjeta desaparece, el contador disminuye, la API responde 204 y la tarea no reaparece tras recargar.
- Resultado obtenido: tarjetas restantes=0; DELETE=1; tras recarga=0.
- Estado: Aprobado.
- Observaciones: Flujo de interfaz con integración a la API.
- Técnica: Caja negra - flujo normal de interfaz.
- Requisito: RF4.
- Capa: Interfaz.

### CP-CB-01

- ID: CP-CB-01
- Funcionalidad: Validar título en el backend
- Objetivo: Cubrir las decisiones de `validate_title` para un título válido, uno vacío después de quitar espacios y uno que supera los 100 caracteres.
- Precondiciones: Función de validación importable desde `backend/app/schemas.py`.
- Datos de entrada: "  Tarea válida  "; ""; "     "; "a" repetido 101 veces.
- Procedimiento: Invocar el validador con cada dato y registrar el valor devuelto o la excepción.
- Resultado esperado: El primer dato devuelve "Tarea válida"; la cadena vacía y la de solo espacios lanzan error de título vacío; la de 101 caracteres lanza error de longitud.
- Resultado obtenido: válido='Tarea válida'; vacío='Value error, El título no puede estar vacío ni contener solo espacios'; espacios='Value error, El título no puede estar vacío ni contener solo espacios'; 101='Value error, El título no puede superar los 100 caracteres'; None='Input should be a valid string'.
- Estado: Aprobado.
- Observaciones: Cubre las decisiones D2 y D3. La rama `value is None` es defensiva y no es alcanzable desde la API.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF1 y restricciones del título.
- Capa: Backend (unidad).

### CP-CB-02

- ID: CP-CB-02
- Funcionalidad: Actualizar estado en el repositorio
- Objetivo: Cubrir el camino de `update_task_status` con una tarea existente y con una tarea inexistente.
- Precondiciones: Base SQLite temporal con una tarea de identificador conocido.
- Datos de entrada: (id_existente, "En curso") y (99999, "En curso").
- Procedimiento: Invocar `repository.update_task_status` con cada par de datos.
- Resultado esperado: El primer caso devuelve un diccionario con el estado actualizado; el segundo devuelve `None`.
- Resultado obtenido: creada=Pendiente; actualizada=En curso; inexistente=None.
- Estado: Aprobado.
- Observaciones: Cubre `cursor.rowcount == 0` en sus dos resultados.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF3.
- Capa: Backend (unidad).

### CP-CB-03

- ID: CP-CB-03
- Funcionalidad: Eliminar tarea en el repositorio
- Objetivo: Cubrir `delete_task` con una tarea existente y con una tarea inexistente.
- Precondiciones: Base SQLite temporal con una tarea de identificador conocido.
- Datos de entrada: id_existente y 99999.
- Procedimiento: Invocar `repository.delete_task` con cada identificador.
- Resultado esperado: El primer caso devuelve `True`; el segundo devuelve `False`; la tarea existente ya no está en la base.
- Resultado obtenido: primera=True; segunda=False; inexistente=False; restantes=0.
- Estado: Aprobado.
- Observaciones: Cubre `cursor.rowcount > 0` en sus dos resultados.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF4.
- Capa: Backend (unidad).

### CP-CB-04

- ID: CP-CB-04
- Funcionalidad: Validar formulario en el frontend
- Objetivo: Cubrir `handleSubmit` con un título vacío, uno que supera los 100 caracteres y uno válido.
- Precondiciones: Aplicación completa en ejecución (backend y frontend); la petición POST se intercepta para simular un error de API.
- Datos de entrada: ""; "     "; "a" repetido 101 veces; "Tarea válida"; "Tarea con error" con la API interceptada para responder HTTP 500.
- Procedimiento: Ejecutar el formulario real con cada dato, incluida una ejecución con la API interceptada para responder HTTP 500, y observar el mensaje y las peticiones emitidas.
- Resultado esperado: El título vacío muestra un error y no emite la petición; el de 101 caracteres muestra un error y no emite; el válido emite la petición y limpia el campo; si la API falla, se muestra el mensaje de error devuelto.
- Resultado obtenido: vacío='El título es obligatorio y no puede contener solo espacios.'; espacios='El título es obligatorio y no puede contener solo espacios.'; len101=101; largo='El título no puede superar los 100 caracteres.'; POST inválidos=0; error API='Error simulado de red'; tarjetas tras error=0; alta válida=True; input=''; POST totales=2.
- Estado: Aprobado.
- Observaciones: El atributo `maxLength` limita el ingreso manual a 100; el valor de 101 se carga programáticamente para ejercitar la rama de validación. Se ejecuta sobre la interfaz real en lugar de aislar el componente, cubriendo las mismas ramas de `handleSubmit`.
- Técnica: Caja blanca - cobertura de decisiones.
- Requisito: RF1.
- Capa: Frontend (unidad).

### CP-CB-05

- ID: CP-CB-05
- Funcionalidad: Mover tarea por arrastre en el frontend
- Objetivo: Cubrir la condición compuesta de `handleDrop` en la columna.
- Precondiciones: Aplicación completa en ejecución y una tarea creada en la columna Pendiente.
- Datos de entrada: Soltar una tarea de la misma columna; soltar una tarea de otra columna; soltar un identificador inválido.
- Procedimiento: Arrastrar la tarjeta con eventos de arrastre reales hacia la misma columna, hacia otra columna y soltar identificadores inválidos; registrar las peticiones PATCH.
- Resultado esperado: La misma columna no emite PATCH; la columna distinta emite un PATCH con el id y el estado correctos; el identificador inválido no emite PATCH y la tarjeta no cambia de columna.
- Resultado obtenido: PATCH misma columna=0; PATCH movimiento=1; PATCH tras ids inválidos=1; En curso=1; Terminada=0.
- Estado: Aprobado.
- Observaciones: Cubre los resultados de `Number.isInteger(taskId) && taskId > 0 && !alreadyInColumn`. Se ejecuta sobre la interfaz real en lugar de aislar el componente, cubriendo las mismas condiciones.
- Técnica: Caja blanca - cobertura de condiciones.
- Requisito: RF3.
- Capa: Frontend (unidad).

## Resumen de cobertura

| Funcionalidad | Casos de caja negra | Casos de caja blanca | Total |
|---------------|---------------------|----------------------|-------|
| Crear tarea | 10 | 2 | 12 |
| Mover tarea | 6 | 2 | 8 |
| Eliminar tarea | 3 | 1 | 4 |
| Listar tareas | 1 | 0 | 1 |
| Total | 20 | 5 | 25 |

| Técnica | Cantidad de casos que la aplican |
|---------|----------------------------------|
| Clases de equivalencia válidas | 8 |
| Clases de equivalencia inválidas | 7 |
| Análisis de valores límite | 4 |
| Flujos normales (API e interfaz) | 4 |
| Caja blanca | 5 |

Algunos casos aplican más de una técnica, por lo que la suma de la segunda tabla supera el total de 25 casos únicos.

## Conclusión de la etapa

Se diseñaron 25 casos de prueba que cubren las cuatro funcionalidades del sistema, los requisitos RF1 a RF4 y las restricciones de título y estado. La caja negra aporta casos de clases de equivalencia y de valores límite sobre la API y la interfaz; la caja blanca permite cubrir las decisiones y condiciones principales del backend y del frontend. El conjunto queda listo para su ejecución y registro en la Etapa 6.

## Próxima etapa

La Etapa 6 consistirá en ejecutar estos casos sobre el sistema desarrollado, registrar el resultado obtenido y el estado de cada uno, y documentar los defectos que aparezcan para su seguimiento en la Etapa 7.
