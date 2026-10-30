# Tablero de Tareas - Actividad Integradora

Sistema gestor de tareas tipo Kanban desarrollado para la materia **Verificación y Validación de Software** (Tercer Año "TSDS").

**Integrantes:** Aureliano Eichhorn y Nicolás Delfino.

## Funcionalidades

- Crear tareas con título obligatorio (máximo 100 caracteres), descripción y fecha límite opcionales.
- Mover tareas entre las columnas **Pendiente**, **En curso** y **Terminada**, y reordenarlas dentro de cada columna.
- Editar el título, la descripción, la fecha límite, la prioridad, el responsable, las etiquetas y los enlaces de una tarea.
- Asignar una prioridad (**Baja**, **Media** o **Alta**, por defecto **Media**) y un responsable (texto libre de hasta 60 caracteres).
- Asociar hasta 5 etiquetas por tarea (de hasta 30 caracteres, reutilizables y sugeridas desde las existentes) y hasta 5 enlaces (con URL `http://` o `https://` y un nombre opcional).
- Agregar un checklist de subtareas, marcarlas como completadas y eliminarlas.
- Impedir que una tarea se finalice mientras tenga subtareas pendientes.
- Señalar las tareas vencidas a partir de su fecha límite.
- Adjuntar archivos a una tarea y descargarlos o eliminarlos.
- Buscar tareas por texto y filtrarlas por prioridad, etiqueta y vencimiento, con orden por posición, prioridad, fecha límite o creación.
- Registrar un historial de actividad por tarea y cargar subtareas, etiquetas, enlaces, prioridad y responsable al crear la tarea.
- Eliminar tareas con confirmación previa y deshacer la eliminación durante unos segundos.

## Tecnologías

- **Frontend:** React + JavaScript + CSS (Vite).
- **Backend:** Python + FastAPI.
- **Base de datos:** SQLite.

## Estructura del proyecto

```
backend/
  app/
    main.py                # Aplicación FastAPI y configuración
    database.py            # Conexión, restricciones e inicialización de SQLite
    schemas.py             # Modelos y validaciones (Pydantic)
    repository.py          # Acceso a datos y reglas de negocio
    routers/
      tasks.py             # Endpoints REST de tareas
      subtasks.py          # Endpoints REST de subtareas
      attachments.py       # Endpoints REST de archivos adjuntos
      tags.py              # Endpoint de consulta de etiquetas
  requirements.txt
  storage/                 # Archivos adjuntos (se crea al iniciar la aplicación)
frontend/
  src/
    App.jsx
    api.js
    format.js
    components/            # Board, Column, TaskCard, TaskForm, TaskDetailModal, ...
    styles/app.css
  package.json
docs/                      # Documentación de cada etapa
scripts/etapa_6/           # Scripts de ejecución de los casos de prueba
```

## Requisitos previos

- Python 3.12 o superior.
- Node.js 20.19 o superior (o 22.12 o superior), requerido por Vite 8.

## Instalación y ejecución

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.
Documentación interactiva: `http://127.0.0.1:8000/docs`.

### 2. Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

## Análisis estático

Con el entorno virtual activado, desde la raíz del proyecto:

```bash
pip install -r backend/requirements-dev.txt
ruff check backend
python -m compileall backend/app
```

Para el frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servicio |
| GET | `/api/tasks` | Lista las tareas; acepta los filtros `?q=`, `?priority=`, `?tag=` y `?overdue=true`, y el orden `?sort=` (`position`, `priority`, `due` o `created`) |
| POST | `/api/tasks` | Crea una tarea (admite `priority`, `assignee`, `subtasks`, `tags` y `links`) |
| PUT | `/api/tasks/{id}` | Edita el título, la descripción, la fecha límite, la prioridad, el responsable, las etiquetas y los enlaces |
| PATCH | `/api/tasks/{id}/move` | Mueve la tarea de estado o la reordena (`status` y `position`) |
| DELETE | `/api/tasks/{id}` | Elimina una tarea |
| POST | `/api/tasks/{id}/restore` | Restaura una tarea eliminada |
| GET | `/api/tags` | Devuelve los nombres de las etiquetas existentes |
| POST | `/api/tasks/{id}/subtasks` | Agrega una subtarea a la tarea |
| PATCH | `/api/subtasks/{id}` | Actualiza el título o el estado de una subtarea |
| DELETE | `/api/subtasks/{id}` | Elimina una subtarea |
| POST | `/api/tasks/{id}/attachments` | Sube un archivo adjunto (multipart) |
| GET | `/api/tasks/{id}/attachments/{attachment_id}` | Descarga un archivo adjunto |
| DELETE | `/api/tasks/{id}/attachments/{attachment_id}` | Elimina un archivo adjunto |

## Reglas de negocio

- El título es obligatorio, no puede estar vacío ni contener solo espacios, y no puede superar los 100 caracteres.
- La descripción no puede superar los 500 caracteres.
- Toda tarea nueva se crea con estado `Pendiente`.
- Los estados válidos son `Pendiente`, `En curso` y `Terminada`.
- Una tarea no puede pasar a `Terminada` mientras tenga subtareas pendientes (HTTP 409).
- Al agregar una subtarea pendiente o al desmarcar una subtarea de una tarea finalizada, la tarea vuelve a `En curso`.
- Al crear una tarea, la fecha límite no puede ser anterior a hoy; al editarla sí se admite una fecha pasada.
- Una tarea está vencida cuando su fecha límite ya pasó y la tarea no está terminada. Es un estado calculado, no almacenado.
- Cada tarea admite hasta 3 archivos adjuntos, de 5 MB como máximo, con extensión `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt` o `.docx`.
- La prioridad debe ser `Baja`, `Media` o `Alta`; si no se indica, se usa `Media`.
- El responsable es opcional y admite hasta 60 caracteres.
- Cada tarea admite hasta 5 etiquetas, de hasta 30 caracteres cada una, que se reutilizan entre tareas sin distinguir mayúsculas; las existentes se ofrecen como sugerencias en `GET /api/tags`.
- Cada tarea admite hasta 5 enlaces; la URL debe comenzar con `http://` o `https://`, no superar los 500 caracteres y no repetirse dentro de la tarea; el nombre es opcional y admite hasta 60 caracteres.
- El alta de una tarea admite hasta 20 subtareas cargadas junto con los demás datos.
- Cada tarea conserva un historial de actividad automático; la API devuelve las últimas 20 acciones, de la más reciente a la más antigua.
- El título se recorta antes de guardarse y las posiciones dentro de una columna se mantienen sin huecos.
- Las operaciones sobre tareas, subtareas o adjuntos inexistentes responden con HTTP 404.
- Los datos inválidos responden con HTTP 422; superar los límites de etiquetas, enlaces o subtareas responde con HTTP 409.
