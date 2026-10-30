# Tablero de Tareas - Actividad Integradora

Sistema gestor de tareas tipo Kanban desarrollado para la materia **Verificación y Validación de Software** (Tercer Año "TSDS").

**Integrantes:** Aureliano Eichhorn y Nicolás Delfino.

## Funcionalidades

- Crear tareas con título obligatorio (máximo 100 caracteres).
- Mover tareas entre las columnas **Pendiente**, **En curso** y **Terminada**.
- Eliminar tareas.

## Tecnologías

- **Frontend:** React + JavaScript + CSS (Vite).
- **Backend:** Python + FastAPI.
- **Base de datos:** SQLite.

## Estructura del proyecto

```
backend/
  app/
    main.py          # Aplicación FastAPI y configuración
    database.py      # Conexión e inicialización de SQLite
    schemas.py       # Modelos y validaciones (Pydantic)
    repository.py    # Acceso a datos (CRUD)
    routers/tasks.py # Endpoints REST de tareas
  requirements.txt
frontend/
  src/
    App.jsx
    api.js
    components/      # Board, Column, TaskCard, TaskForm
    styles/app.css
  package.json
docs/                # Documentación de cada etapa
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
| GET | `/api/tasks` | Lista todas las tareas |
| POST | `/api/tasks` | Crea una tarea |
| PATCH | `/api/tasks/{id}/status` | Actualiza el estado de una tarea |
| DELETE | `/api/tasks/{id}` | Elimina una tarea |

## Reglas de negocio

- El título es obligatorio, no puede estar vacío ni contener solo espacios.
- El título no puede superar los 100 caracteres.
- Toda tarea nueva se crea con estado `Pendiente`.
- Los estados válidos son `Pendiente`, `En curso` y `Terminada`.
- Las operaciones sobre tareas inexistentes responden con HTTP 404.
- Los datos inválidos responden con HTTP 422.
