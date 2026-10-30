# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino

# Etapa 3 - Desarrollo del sistema

## Objetivo de la etapa

Implementar el sistema gestor de tareas definido en las etapas anteriores, respetando las funcionalidades, los requisitos funcionales y las restricciones establecidas en la Etapa 1, y utilizando el stack tecnológico planificado en la Etapa 2.

## Funcionalidades implementadas

| Funcionalidad | Requisito | Descripción |
|---------------|-----------|-------------|
| Crear tarea | RF1, RF2 | Permite registrar una tarea mediante un título. Se asigna automáticamente el estado `Pendiente`. |
| Mover tarea | RF3 | Permite actualizar el estado de una tarea entre `Pendiente`, `En curso` y `Terminada`. |
| Eliminar tarea | RF4 | Permite borrar una tarea existente del registro. |

Las tres funcionalidades se encuentran disponibles tanto en la interfaz visual como en la API REST.

## Arquitectura del sistema

El sistema se organiza en dos aplicaciones independientes que se comunican mediante HTTP:

- **Backend (API REST):** implementado con Python y FastAPI. Expone los endpoints de tareas, aplica las validaciones y persiste la información en SQLite.
- **Frontend (interfaz):** implementado con React. Consume la API mediante `fetch` y presenta el tablero Kanban con las columnas Pendiente, En curso y Terminada.
- **Base de datos:** SQLite, con una tabla `tasks` que almacena identificador, título, estado y fecha de creación.

La comunicación entre frontend y backend se resuelve mediante un proxy de desarrollo de Vite hacia `/api`, y el backend habilita CORS para el origen del frontend.

## Estructura del código

| Archivo | Responsabilidad |
|---------|-----------------|
| `backend/app/main.py` | Creación de la aplicación FastAPI, CORS, inicialización de la base y registro de rutas. |
| `backend/app/database.py` | Configuración de SQLite, conexión y creación de la tabla `tasks`. |
| `backend/app/schemas.py` | Modelos Pydantic y validación del título y del estado. |
| `backend/app/repository.py` | Operaciones de acceso a datos: crear, listar, obtener, actualizar y eliminar. |
| `backend/app/routers/tasks.py` | Definición de los endpoints REST y manejo de errores HTTP. |
| `frontend/src/App.jsx` | Estado principal de la aplicación y coordinación de las operaciones. |
| `frontend/src/api.js` | Funciones de comunicación con la API. |
| `frontend/src/components/` | Componentes del tablero: Board, Column, TaskCard y TaskForm. |
| `frontend/src/styles/app.css` | Estilos visuales del tablero y formulario. |

La separación en capas (rutas, validaciones, repositorio y base de datos) busca que el código sea comprensible y que cada parte pueda probarse de forma aislada en las etapas siguientes.

## Validación de datos de entrada

| Dato | Regla aplicada | Capa |
|------|----------------|------|
| Título al crear | Obligatorio, no vacío y no compuesto solo por espacios. | Frontend y backend |
| Título al crear | Longitud máxima de 100 caracteres. | Frontend y backend |
| Título al crear | Se eliminan los espacios al inicio y al final antes de guardar. | Backend |
| Estado al mover | Debe ser uno de los valores `Pendiente`, `En curso` o `Terminada`. | Frontend y backend |
| Identificador al mover o eliminar | La tarea debe existir. | Backend |

Las validaciones se aplican en el backend como fuente de verdad, ya que la API puede ser consumida sin pasar por la interfaz. El frontend además valida antes de enviar para dar una respuesta inmediata al usuario.

## Manejo de errores

| Situación | Respuesta del sistema |
|-----------|-----------------------|
| Título vacío o con solo espacios | HTTP 422 con mensaje de validación. |
| Título de más de 100 caracteres | HTTP 422 con mensaje de validación. |
| Estado no permitido | HTTP 422 con mensaje de validación. |
| Intento de mover una tarea inexistente | HTTP 404 con el detalle "Tarea no encontrada". |
| Intento de eliminar una tarea inexistente | HTTP 404 con el detalle "Tarea no encontrada". |
| Error de conexión con la API | Mensaje de error visible en la interfaz. |

## Endpoints implementados

| Método | Ruta | Descripción | Códigos de respuesta |
|--------|------|-------------|----------------------|
| GET | `/api/health` | Verifica que el servicio esté activo. | 200 |
| GET | `/api/tasks` | Devuelve la lista de tareas. | 200 |
| POST | `/api/tasks` | Crea una tarea nueva con estado `Pendiente`. | 201, 422 |
| PATCH | `/api/tasks/{id}/status` | Actualiza el estado de una tarea. | 200, 404, 422 |
| DELETE | `/api/tasks/{id}` | Elimina una tarea. | 204, 404 |

## Interfaz de usuario

El frontend presenta:

- Un formulario para crear tareas, con validación y contador máximo de caracteres.
- Un tablero con tres columnas: Pendiente, En curso y Terminada.
- Tarjetas arrastrables entre columnas para actualizar el estado.
- Un botón de eliminación en cada tarjeta.
- Mensajes de error visibles ante fallas de validación o de conexión.

## Control de versiones

El proyecto se gestiona con Git. Para esta etapa se registró:

- La estructura inicial del repositorio.
- El backend con la API, validaciones y persistencia.
- El frontend con el tablero y la integración con la API.
- La documentación de la etapa.

Los entregables de la etapa se registran en un commit identificable, de modo que los avances de cada integrante queden trazados para las etapas de verificación y pruebas.

## Evidencias de funcionamiento

Durante el desarrollo se verificó el funcionamiento del sistema completo:

| Verificación | Resultado |
|--------------|-----------|
| Servicio activo (`GET /api/health`) | `{"status": "ok"}` |
| Creación de una tarea válida | HTTP 201, tarea con estado `Pendiente`. |
| Creación con título de solo espacios | HTTP 422. |
| Actualización a `En curso` | HTTP 200, estado actualizado. |
| Actualización con estado inválido | HTTP 422. |
| Eliminación de una tarea existente | HTTP 204. |
| Eliminación de una tarea inexistente | HTTP 404. |
| Compilación del frontend | `vite build` finalizado correctamente. |
| Acceso a la interfaz y proxy hacia la API | HTTP 200 y respuesta correcta de la API. |

## Conclusión de la etapa

Se completó el desarrollo del sistema con las tres funcionalidades principales, las validaciones definidas en la Etapa 1 y el manejo de situaciones correctas e incorrectas. El código quedó organizado en capas y el sistema puede ejecutarse de punta a punta, lo que habilita las actividades de verificación y pruebas de las etapas siguientes.
