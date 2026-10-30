# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 29/10/2026

# Etapa 3 - Desarrollo del sistema

## Objetivo de la etapa

Implementar el sistema gestor de tareas definido en las etapas anteriores, respetando las funcionalidades, los requisitos funcionales y las restricciones establecidas en la Etapa 1, y utilizando el stack tecnológico, la organización del trabajo y la estrategia de pruebas planificadas en la Etapa 2.

## Funcionalidades implementadas

| Funcionalidad | Requisito | Descripción |
|---------------|-----------|-------------|
| Crear tarea | RF1, RF2 | Registra una tarea con título obligatorio, descripción y fecha límite opcionales. El estado inicial es `Pendiente`. |
| Mover y reordenar tarea | RF3, RF4 | Cambia el estado de la tarea entre `Pendiente`, `En curso` y `Terminada` y la reubica dentro de la columna destino. |
| Editar tarea | RF5 | Modifica el título, la descripción y la fecha límite de una tarea existente. |
| Checklist de subtareas | RF6, RF7, RF8 | Agrega subtareas, las marca y desmarca como completadas y las elimina, informando el avance. |
| Control de finalización | RF9 | Impide finalizar una tarea mientras tenga subtareas pendientes (HTTP 409). |
| Fecha límite y vencimiento | RF10 | Registra la fecha límite y calcula el estado `overdue` de cada tarea. |
| Archivos adjuntos | RF11, RF12, RF13 | Sube, descarga y elimina archivos adjuntos con validación de extensión, tamaño y cantidad. |
| Eliminar con deshacer | RF14, RF15 | Elimina una tarea con borrado lógico y permite restaurarla durante unos segundos. |

Las ocho funcionalidades están disponibles tanto en la interfaz visual como en la API REST.

## Arquitectura del sistema

El sistema se organiza en dos aplicaciones independientes que se comunican mediante HTTP:

- **Backend (API REST):** implementado con Python y FastAPI. Expone los endpoints de tareas, subtareas y adjuntos, aplica las validaciones y las reglas de negocio, y persiste la información en SQLite y los adjuntos en disco.
- **Frontend (interfaz):** implementado con React. Consume la API mediante `fetch` y presenta el tablero Kanban con las columnas Pendiente, En curso y Terminada.
- **Base de datos:** SQLite, con las tablas `tasks`, `subtasks` y `attachments`.

Dentro del backend, el código se organiza en capas con una única dirección de dependencia:

`routers` (HTTP) → `schemas` (validación) → `repository` (reglas de negocio y acceso a datos) → `database` (conexión y esquema).

La comunicación entre frontend y backend se resuelve mediante un proxy de desarrollo de Vite hacia `/api`, y el backend habilita CORS para el origen del frontend.

## Estructura del código

| Archivo | Responsabilidad |
|---------|-----------------|
| `backend/app/main.py` | Creación de la aplicación FastAPI, CORS, inicialización de la base y registro de rutas. |
| `backend/app/database.py` | Configuración de SQLite, conexión, restricciones del esquema y migración de bases anteriores. |
| `backend/app/schemas.py` | Modelos Pydantic, constantes de validación y validadores de título, descripción y fecha. |
| `backend/app/repository.py` | Reglas de negocio y acceso a datos: crear, listar, editar, mover, reordenar, eliminar, restaurar, subtareas y adjuntos. |
| `backend/app/routers/tasks.py` | Endpoints de tareas y traducción de errores de dominio a respuestas HTTP. |
| `backend/app/routers/subtasks.py` | Endpoints de subtareas. |
| `backend/app/routers/attachments.py` | Subida, descarga y eliminación de archivos adjuntos. |
| `backend/storage/` | Carpeta donde se guardan los archivos adjuntos (se crea al iniciar la aplicación). |
| `frontend/src/App.jsx` | Estado principal de la aplicación, carga de datos y coordinación de las operaciones. |
| `frontend/src/api.js` | Funciones de comunicación con la API. |
| `frontend/src/format.js` | Formateo de fechas y cálculo de la etiqueta de vencimiento. |
| `frontend/src/components/` | Componentes del tablero: Board, Column, TaskCard, TaskForm, TaskDetailModal, TaskFields, DueBadge, ConfirmDialog y Toast. |
| `frontend/src/styles/app.css` | Estilos visuales del tablero, las tarjetas y los diálogos. |

La separación en capas busca que el código sea comprensible y que cada parte pueda probarse de forma aislada en las etapas siguientes.

## Modelo de datos

### Tabla `tasks`

| Columna | Tipo | Restricción |
|---------|------|-------------|
| `id` | INTEGER | Clave primaria autoincremental. |
| `title` | TEXT | Obligatorio; `length(trim(title))` entre 1 y 100. |
| `description` | TEXT | Obligatorio (por defecto `''`); longitud máxima 500. |
| `status` | TEXT | Obligatorio (por defecto `Pendiente`); solo valores `Pendiente`, `En curso` o `Terminada`. |
| `due_date` | TEXT | Opcional; si está presente debe tener el formato `AAAA-MM-DD`. |
| `position` | INTEGER | Obligatorio (por defecto 0); no puede ser negativo. |
| `deleted_at` | TEXT | Opcional; si tiene valor, la tarea está eliminada (borrado lógico). |
| `created_at` | TEXT | Obligatorio; fecha y hora de creación en formato ISO 8601. |

### Tabla `subtasks`

| Columna | Tipo | Restricción |
|---------|------|-------------|
| `id` | INTEGER | Clave primaria autoincremental. |
| `task_id` | INTEGER | Obligatorio; referencia a `tasks(id)` con `ON DELETE CASCADE`. |
| `title` | TEXT | Obligatorio; `length(trim(title))` entre 1 y 100. |
| `done` | INTEGER | Obligatorio (por defecto 0); solo valores 0 o 1. |
| `created_at` | TEXT | Obligatorio; fecha y hora de creación en formato ISO 8601. |

### Tabla `attachments`

| Columna | Tipo | Restricción |
|---------|------|-------------|
| `id` | INTEGER | Clave primaria autoincremental. |
| `task_id` | INTEGER | Obligatorio; referencia a `tasks(id)` con `ON DELETE CASCADE`. |
| `filename` | TEXT | Obligatorio; nombre original del archivo. |
| `stored_name` | TEXT | Obligatorio; nombre interno con el que se guarda en `storage/`. |
| `content_type` | TEXT | Obligatorio (por defecto `application/octet-stream`). |
| `size_bytes` | INTEGER | Obligatorio; mayor que 0 y menor o igual a 5 MB. |
| `created_at` | TEXT | Obligatorio; fecha y hora de subida en formato ISO 8601. |

El estado `overdue` (vencido) no se almacena: se calcula cada vez que se devuelve una tarea, comparando su fecha límite con la fecha actual y verificando que no esté terminada. El estado de una tarea se guarda únicamente en la columna `status`, de modo que una tarea no puede tener dos estados a la vez.

## Validaciones y reglas de negocio

| Dato o regla | Regla aplicada | Capa |
|--------------|----------------|------|
| Título al crear o editar | Obligatorio, no vacío y no compuesto solo por espacios. | Frontend, backend y base de datos |
| Título al crear o editar | Longitud máxima de 100 caracteres. | Frontend, backend y base de datos |
| Título al crear o editar | Se eliminan los espacios al inicio y al final antes de guardar. | Backend |
| Descripción | Longitud máxima de 500 caracteres; opcional. | Frontend, backend y base de datos |
| Estado inicial | Toda tarea nueva se crea en `Pendiente`. | Backend |
| Estado al mover | Debe ser uno de los valores `Pendiente`, `En curso` o `Terminada`. | Backend y base de datos |
| Finalización | Una tarea no puede pasar a `Terminada` si tiene subtareas pendientes. | Backend |
| Reapertura automática | Al agregar una subtarea pendiente a una tarea terminada, o al desmarcar una subtarea de una tarea terminada, la tarea vuelve a `En curso`. | Backend |
| Fecha límite al crear | No puede ser anterior a la fecha actual. | Frontend y backend |
| Fecha límite al editar | Sí se admite una fecha anterior a la actual. | Backend |
| Vencimiento | Calculado como fecha límite pasada y tarea no terminada. | Backend |
| Adjuntos: extensión | Solo `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt` y `.docx`. | Frontend y backend |
| Adjuntos: tamaño | Máximo 5 MB por archivo. | Frontend y backend |
| Adjuntos: cantidad | Máximo 3 archivos por tarea. | Backend |
| Reordenamiento | Las posiciones dentro de una columna se mantienen entre 0 y n-1, sin huecos. | Backend |
| Eliminación | Borrado lógico con `deleted_at`, que permite restaurar la tarea. | Backend |
| Integridad en la base | Restricciones `CHECK` de título, descripción, estado, fecha, posición y tamaño, y claves foráneas con borrado en cascada. | Base de datos |
| Identificador al operar | La tarea, subtarea o adjunto debe existir y no estar eliminado. | Backend |

Las validaciones se aplican en el backend como fuente de verdad, ya que la API puede ser consumida sin pasar por la interfaz. El frontend además valida antes de enviar para dar una respuesta inmediata al usuario. La base de datos mantiene restricciones `CHECK` como última barrera de integridad.

## Manejo de errores

| Situación | Respuesta del sistema |
|-----------|-----------------------|
| Título vacío, con solo espacios o de más de 100 caracteres | HTTP 422 con mensaje de validación. |
| Descripción de más de 500 caracteres | HTTP 422 con mensaje de validación. |
| Fecha límite anterior a la actual al crear | HTTP 422 con mensaje de validación. |
| Estado no permitido o posición negativa | HTTP 422 con mensaje de validación. |
| Intento de finalizar una tarea con subtareas pendientes | HTTP 409 con el detalle `No se puede finalizar: la tarea tiene N subtareas pendientes`. |
| Adjunto con extensión no permitida | HTTP 415 con el detalle de los formatos aceptados. |
| Adjunto vacío | HTTP 422 con el detalle `El archivo está vacío`. |
| Adjunto de más de 5 MB | HTTP 413 con el detalle `El archivo supera el tamaño máximo de 5 MB`. |
| Cuarto adjunto en una misma tarea | HTTP 409 con el detalle del límite de 3 archivos. |
| Operación sobre una tarea, subtarea o adjunto inexistente | HTTP 404 con el detalle correspondiente. |
| Identificador no numérico en la ruta | HTTP 422 por error de validación del parámetro. |
| Error de conexión con la API | Mensaje de error visible en la interfaz. |

## Endpoints implementados

| Método | Ruta | Descripción | Códigos de respuesta |
|--------|------|-------------|----------------------|
| GET | `/api/health` | Verifica que el servicio esté activo. | 200 |
| GET | `/api/tasks` | Devuelve la lista de tareas; acepta `?overdue=true` para ver solo las vencidas. | 200 |
| POST | `/api/tasks` | Crea una tarea nueva con estado `Pendiente`. | 201, 422 |
| PUT | `/api/tasks/{id}` | Edita título, descripción y fecha límite de una tarea. | 200, 404, 422 |
| PATCH | `/api/tasks/{id}/move` | Mueve la tarea de estado o la reordena (`status` y `position`). | 200, 404, 409, 422 |
| POST | `/api/tasks/{id}/restore` | Restaura una tarea eliminada. | 200, 404 |
| DELETE | `/api/tasks/{id}` | Elimina una tarea (borrado lógico). | 204, 404 |
| POST | `/api/tasks/{id}/subtasks` | Agrega una subtarea a la tarea. | 201, 404, 422 |
| PATCH | `/api/subtasks/{id}` | Actualiza el título o el estado de una subtarea. | 200, 404, 422 |
| DELETE | `/api/subtasks/{id}` | Elimina una subtarea. | 204, 404 |
| POST | `/api/tasks/{id}/attachments` | Sube un archivo adjunto (multipart). | 201, 404, 409, 413, 415, 422 |
| GET | `/api/tasks/{id}/attachments/{attachment_id}` | Descarga un archivo adjunto. | 200, 404 |
| DELETE | `/api/tasks/{id}/attachments/{attachment_id}` | Elimina un archivo adjunto. | 204, 404 |

Las respuestas de tareas incluyen el detalle completo: subtareas, adjuntos, posición, fecha límite, estado `overdue` y conteo de subtareas realizadas. Las operaciones sobre subtareas y adjuntos devuelven la tarea actualizada, de modo que el frontend puede refrescar la tarjeta con una sola respuesta.

## Interfaz de usuario

El frontend presenta:

- Un formulario para crear tareas, con título obligatorio, descripción y fecha límite opcionales, validación y contador de caracteres.
- Un tablero con tres columnas: Pendiente, En curso y Terminada, con el contador de tareas de cada una.
- Tarjetas arrastrables entre columnas que además permiten reordenarlas dentro de la misma columna.
- Un filtro para ver solo las tareas vencidas.
- Una insignia de vencimiento y un indicador de avance del checklist en cada tarjeta.
- Un detalle de tarea que permite editarla, gestionar el checklist, adjuntar y descargar archivos.
- Un diálogo de confirmación antes de eliminar y un aviso con la opción de deshacer la eliminación.
- Mensajes de error visibles ante fallas de validación o de conexión.

## Control de versiones

El proyecto se gestiona con Git. Para esta etapa se registró:

- La estructura inicial del repositorio.
- El backend con la API, las validaciones, las reglas de negocio y la persistencia.
- El frontend con el tablero, el detalle de tarea y la integración con la API.
- La documentación de la etapa.

Los entregables de la etapa se registran en un commit identificable, de modo que los avances de cada integrante queden trazados para las etapas de verificación y pruebas.

## Evidencias de funcionamiento

Durante el desarrollo se verificó el funcionamiento del sistema completo:

| Verificación | Resultado |
|--------------|-----------|
| Servicio activo (`GET /api/health`) | `{"status": "ok"}` |
| Creación de una tarea válida | HTTP 201, tarea con estado `Pendiente`. |
| Creación con título de solo espacios | HTTP 422. |
| Edición de título, descripción y fecha | HTTP 200, datos actualizados. |
| Movimiento a `En curso` | HTTP 200, estado actualizado. |
| Movimiento con estado inválido | HTTP 422. |
| Finalización con subtareas pendientes | HTTP 409. |
| Alta de subtarea y marcado como completada | HTTP 201 y HTTP 200, con el avance actualizado. |
| Subida de un adjunto válido | HTTP 201, archivo disponible para descargar. |
| Subida de un adjunto con extensión no permitida | HTTP 415. |
| Eliminación de una tarea existente | HTTP 204. |
| Restauración de una tarea eliminada | HTTP 200, tarea visible otra vez. |
| Eliminación de una tarea inexistente | HTTP 404. |
| Compilación del frontend | `vite build` finalizado correctamente. |
| Acceso a la interfaz y proxy hacia la API | HTTP 200 y respuesta correcta de la API. |

## Conclusión de la etapa

Se completó el desarrollo del sistema con las ocho funcionalidades planificadas, las validaciones definidas en la Etapa 1 y el manejo de situaciones correctas e incorrectas, incluyendo los errores de regla de negocio (409), de formato (415) y de tamaño (413). El código quedó organizado en capas, con el modelo de datos documentado y el sistema ejecutable de punta a punta, lo que habilita las actividades de verificación y pruebas de las etapas siguientes.

## Próxima etapa

La Etapa 4 consistirá en la verificación del sistema: revisión de requisitos, diseño y código, y análisis estático con las herramientas configuradas.
