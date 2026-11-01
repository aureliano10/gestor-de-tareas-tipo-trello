# Comandos para levantar el backend

Todos los comandos se ejecutan **desde la raíz del proyecto** (`final_aimar/`).

## 1. Primera vez (crear y preparar el entorno)

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
```

## 2. Levantar el backend

Forma recomendada (usa el script del proyecto):

```bash
bash backend/run_backend.sh
```

Forma manual, sin el script:

```bash
cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` y la documentación interactiva en `http://127.0.0.1:8000/docs`.

## 3. Cambiar host o puerto

```bash
HOST=0.0.0.0 PORT=8080 bash backend/run_backend.sh
```

## 4. Detener el servidor

Presionar `Ctrl + C` en la terminal donde corre.

## 5. Ejecutar las pruebas

Las dependencias de pruebas y lint se instalan aparte de las de ejecución:

```bash
.venv/bin/pip install -r backend/requirements-dev.txt
```

Pruebas de backend (unitarias e integración), sin necesidad de levantar el servidor:

```bash
.venv/bin/python -m pytest backend/tests -v
```

Casos de sistema (API, interfaz y caja blanca), con el backend y el frontend levantados:

```bash
.venv/bin/python scripts/etapa_6/ejecutar_api.py
.venv/bin/python scripts/etapa_6/ejecutar_ui.py
.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py
```

## Notas

- El backend debe levantarse con el directorio de trabajo en `backend/`; por eso el script hace el `cd` por vos. Si usás el comando manual, no te olvides del `cd backend`.
- Las dependencias del backend están en `backend/requirements.txt` (FastAPI, Uvicorn, Pydantic y python-multipart).
- Las dependencias de desarrollo y pruebas (ruff, pytest, httpx y Playwright) están en `backend/requirements-dev.txt`.
