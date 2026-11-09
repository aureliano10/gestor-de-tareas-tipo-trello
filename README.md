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
- **Base de datos:** SQLite en desarrollo local y Turso (libSQL) en Vercel.
- **Adjuntos:** disco local en desarrollo y Vercel Blob en producción.

## Estructura del proyecto

```
backend/
  app/
    main.py                # Aplicación FastAPI y configuración
    database.py            # Conexión SQLite/Turso, restricciones e inicialización
    storage.py             # Almacenamiento de adjuntos (disco local o Vercel Blob)
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
scripts/etapa_6/           # Scripts de ejecución de los casos de prueba de sistema
scripts/etapa_8/           # Runner de las pruebas unitarias (pytest)
scripts/etapa_9/           # Runner de las pruebas de integración (pytest)
```

## Requisitos previos

- Python 3.12 o superior.
- Node.js 20.19 o superior (o 22.12 o superior), requerido por Vite 8.

## Instalación y ejecución

### 1. Backend

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
bash backend/run_backend.sh
```

Forma manual, sin el script (equivale a lo que hace `run_backend.sh`):

```bash
cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload
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

## Despliegue en Vercel

El backend se despliega como servicio de Vercel y necesita una base de datos y un almacenamiento que sobrevivan entre invocaciones. Sin ellos, cada instancia usaría un `/tmp` distinto y las tareas o los adjuntos desaparecerían.

1. **Crear la base de datos Turso**: en el panel de Vercel, entra en **Storage → Create Database → Turso Cloud** (o créala en [turso.tech](https://turso.tech) y copia la URL `libsql://...` y un token).
2. **Crear el almacenamiento de adjuntos**: en **Storage → Create → Blob**, elige acceso **privado** (no se puede cambiar después) y copia el token de lectura/escritura.
3. **Configurar las variables de entorno** del proyecto en Vercel (**Settings → Environment Variables**) para Production, Preview y Development:

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `TURSO_DATABASE_URL` | Sí en producción | URL `libsql://...` de la base de datos. |
| `TURSO_AUTH_TOKEN` | Sí en producción | Token de acceso a Turso. |
| `BLOB_READ_WRITE_TOKEN` | Sí en producción | Token del almacén Blob privado. |
| `KANBAN_ALLOW_EPHEMERAL` | No | `1` permite arrancar en Vercel sin Turso usando `/tmp` (solo para una demo desechable). |

4. **Redesplegar** el proyecto. El endpoint `/api/health` debe responder `database: "turso"` y `storage: "blob"`.

En local no hace falta configurar nada: si no existen `TURSO_DATABASE_URL` ni `BLOB_READ_WRITE_TOKEN`, se usa SQLite y el disco local. Para forzar el almacenamiento local aunque las variables existan, define `KANBAN_STORAGE=local`.

## Análisis estático

Con el entorno virtual activado, desde la raíz del proyecto:

```bash
pip install -r backend/requirements-dev.txt
ruff check backend scripts
python -m compileall backend/app
```

Para el frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Pruebas

Las dependencias de lint y de pruebas (pytest, httpx y Playwright) se instalan con el archivo de desarrollo, ya que no forman parte de las dependencias de ejecución del backend:

```bash
pip install -r backend/requirements-dev.txt
```

Pruebas de backend (unitarias e integración) con pytest, sin necesidad de levantar el servidor:

```bash
.venv/bin/python -m pytest backend/tests -v
```

Casos de sistema (API con httpx, interfaz con Playwright y caja blanca). Requieren el backend y el frontend levantados:

```bash
.venv/bin/python scripts/etapa_6/ejecutar_api.py
.venv/bin/python scripts/etapa_6/ejecutar_ui.py
.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py
```

Cada runner guarda sus resultados en `docs/evidencias/etapa_6/`.

Pruebas unitarias del frontend con [Vitest](https://vitest.dev/) y [Testing Library](https://testing-library.com/), sin necesidad de levantar ningún servidor:

```bash
cd frontend
npm run test       # ejecuta la suite una vez
npm run coverage   # ejecuta la suite y genera el reporte de cobertura
```

El reporte de cobertura se guarda en `frontend/coverage/`. La cobertura del backend se mide con `pytest-cov`:

```bash
cd backend
../.venv/bin/python -m pytest tests --cov=app --cov-report=term-missing
```

## Integración continua

El repositorio incluye un flujo de trabajo de **GitHub Actions** en [`.github/workflows/ci.yml`](.github/workflows/ci.yml) que se ejecuta en cada `push` y en cada `pull request`. Está compuesto por tres trabajos independientes:

| Trabajo | Entorno | Qué ejecuta |
|---------|---------|-------------|
| `backend` | Python 3.12 | `ruff check backend scripts` y las pruebas de pytest (unitarias e integración) con cobertura (`--cov=app`). Publica el reporte JSON de cobertura como artefacto. |
| `frontend` | Node.js 22 | `npm ci`, `npm run lint`, `npm run build` y `npm run coverage` (Vitest). Publica el reporte de cobertura como artefacto. |
| `e2e` | Python 3.12 + Node.js 22 | Instala Chromium de Playwright, levanta el backend (con base SQLite y almacenamiento en rutas temporales) y el frontend, y corre la suite de sistema de la Etapa 6: pruebas de API, de interfaz y de caja blanca. Publica las evidencias como artefacto. |

Para reproducir el trabajo `e2e` en un entorno local, los scripts de la suite respetan la variable de entorno `PLAYWRIGHT_CHANNEL` (`chrome` por defecto; en CI se usa `chromium`, el navegador incluido de Playwright). El backend de la suite puede apuntar a una base temporal con `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH`, de modo que no toca los datos de desarrollo.

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servicio e indicación de la base de datos (`sqlite`/`turso`) y del almacenamiento (`local`/`blob`) en uso |
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
- Cada tarea admite hasta 3 archivos adjuntos, de 4 MB como máximo, con extensión `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt` o `.docx`.
- La prioridad debe ser `Baja`, `Media` o `Alta`; si no se indica, se usa `Media`.
- El responsable es opcional y admite hasta 60 caracteres.
- Cada tarea admite hasta 5 etiquetas, de hasta 30 caracteres cada una, que se reutilizan entre tareas sin distinguir mayúsculas; las existentes se ofrecen como sugerencias en `GET /api/tags`.
- Cada tarea admite hasta 5 enlaces; la URL debe comenzar con `http://` o `https://`, no superar los 500 caracteres y no repetirse dentro de la tarea; el nombre es opcional y admite hasta 60 caracteres.
- El alta de una tarea admite hasta 20 subtareas cargadas junto con los demás datos.
- Cada tarea conserva un historial de actividad automático; la API devuelve las últimas 20 acciones, de la más reciente a la más antigua.
- El título se recorta antes de guardarse y las posiciones dentro de una columna se mantienen sin huecos.
- Las operaciones sobre tareas, subtareas o adjuntos inexistentes responden con HTTP 404.
- Los datos inválidos responden con HTTP 422; superar los límites de etiquetas, enlaces o subtareas responde con HTTP 409.
