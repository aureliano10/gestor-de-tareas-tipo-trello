# Cobertura de pruebas (backend y frontend)

**Materia:** Verificación y Validación de Software
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

## Objetivo

Medir la cobertura real de las pruebas automatizadas del proyecto, es decir, qué
proporción del código se ejecuta efectivamente durante la suite de pruebas.

Se midió por separado:

- la cobertura del **backend** (paquete `app`) alcanzada por las 25 pruebas
  automatizadas con pytest de `backend/tests`;
- la cobertura del **frontend** (React) alcanzada por las pruebas unitarias de
  módulos y componentes incorporadas con Vitest.

El propósito es obtener un número verificable y reproducible, identificar los
huecos de cobertura y explicar por qué existen.

## Herramientas

| Componente | Herramienta | Versión | Rol |
|------------|-------------|---------|-----|
| Backend | `pytest-cov` (sobre `coverage.py`) | 7.1.0 (coverage 7.17.0) | Mide statements cubiertos por la suite de pytest y genera reportes `term-missing` y JSON. |
| Frontend | `vitest` | 5.0.5 | Runner de pruebas unitarias para React, integrado con la configuración de Vite. |
| Frontend | `@vitest/coverage-v8` | 5.0.5 | Proveedor de cobertura basado en el motor V8 de Node (provider `v8`). |
| Frontend | `@testing-library/react` + `jsdom` | 16.3.3 / 29.1.1 | Renderizan los componentes en un DOM simulado (entorno `jsdom`). |

`pytest-cov` se agregó a `backend/requirements-dev.txt`. Las dependencias de
test del frontend se agregaron como `devDependencies` en `frontend/package.json`.

## Procedimiento y comandos

### Backend

Instalación de la dependencia (ya incluida en `requirements-dev.txt`):

```bash
.venv/bin/pip install -r backend/requirements-dev.txt
```

Medición de la cobertura de `backend/tests` sobre el paquete `app`, desde
`backend/`:

```bash
../.venv/bin/python -m pytest tests \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=json:../docs/evidencias/cobertura/backend_coverage.json \
  | tee ../docs/evidencias/cobertura/backend_cobertura.txt
```

### Frontend

Configuración en `frontend/vite.config.js`:

```js
test: {
  environment: "jsdom",
  include: ["src/**/*.{test,spec}.{js,jsx}"],
  coverage: {
    provider: "v8",
    reporter: ["text", "json"],
    reportsDirectory: "coverage",
    include: ["src/**/*.{js,jsx}"],
  },
},
```

Scripts agregados a `frontend/package.json`:

```json
"test": "vitest run",
"coverage": "vitest run --coverage"
```

Ejecución de las pruebas y de la cobertura, desde `frontend/`:

```bash
npm ci            # verifica que el lockfile esté sincronizado
npm run test      # vitest run
npm run coverage  # vitest run --coverage
```

La salida real se guardó en `docs/evidencias/cobertura/frontend_cobertura.txt`
y el reporte JSON en `docs/evidencias/cobertura/frontend_coverage.json` (origen:
`frontend/coverage/coverage-final.json`).

## Resultados

### Backend

Suite ejecutada: 25 pruebas (13 unitarias, 12 de integración; todas aprobadas).
Métrica por archivo: **statements** (el reporte no separa ramas).

| Archivo | Statements | No cubiertos | Cobertura |
|---------|-----------:|-------------:|----------:|
| `app/__init__.py` | 0 | 0 | 100% |
| `app/database.py` | 63 | 0 | 100% |
| `app/main.py` | 18 | 1 | 94% |
| `app/repository.py` | 322 | 73 | 77% |
| `app/routers/__init__.py` | 0 | 0 | 100% |
| `app/routers/attachments.py` | 51 | 16 | 69% |
| `app/routers/subtasks.py` | 22 | 5 | 77% |
| `app/routers/tags.py` | 6 | 0 | 100% |
| `app/routers/tasks.py` | 56 | 20 | 64% |
| `app/schemas.py` | 238 | 11 | 95% |
| **Total** | **776** | **126** | **84%** |

### Frontend

Suite ejecutada: 56 pruebas en 5 archivos (todas aprobadas). Global y por
archivo probado; el resto de los componentes no ejecutados por la suite
unitaria aparecen con 0%.

| Archivo | % Stmts | % Branch | % Funcs | % Lines |
|---------|--------:|---------:|--------:|--------:|
| **Global (todo `src/`)** | **33.78** | **39.17** | **23.38** | **35.17** |
| `src/format.js` | 100 | 100 | 100 | 100 |
| `src/links.js` | 100 | 100 | 100 | 100 |
| `src/useFocusTrap.js` | 97.14 | 84.00 | 100 | 97.14 |
| `src/components/TaskFields.jsx` | 85.71 | 71.42 | 66.66 | 85.71 |
| `src/components/TaskForm.jsx` | 70.17 | 65.95 | 48.57 | 72.28 |
| `src/components/TaskCard.jsx` | 66.66 | 96.29 | 62.50 | 66.66 |
| `src/components/DueBadge.jsx` | 75.00 | 50.00 | 100 | 75.00 |
| Resto de componentes y `App.jsx`, `api.js`, `main.jsx` | 0 | 0 | 0 | 0 |

## Interpretación de los huecos de cobertura

### Backend

Los módulos con lógica pura y de persistencia quedan prácticamente cubiertos:
`database.py` (100%), `schemas.py` (95%) y `tags.py` (100%). La mayor cantidad
de líneas sin cubrir está en la lógica de negocio y HTTP:

- **`routers/tasks.py` (64%)** y **`routers/attachments.py` (69%)**: buena parte
  de los caminos son respuestas de error (404, 409, 413, 415) y rutas de
  descarga/eliminación de adjuntos que la suite de pytest no ejercita en todos
  sus casos. Esas rutas sí se validan en la **suite de sistema de la Etapa 6**
  (62 casos de API con httpx), que no forma parte de esta medición de pytest-cov.
- **`repository.py` (77%)**: las líneas faltantes corresponden a variantes de
  consulta, a la reconstrucción del historial de actividad y a ramas de error
  que se disparan desde los endpoints. Muchas de esas ramas se cubren con los
  casos de API y de caja blanca de la Etapa 6, no desde las pruebas unitarias y
  de integración medidas aquí.
- **`main.py` (94%)**: queda una línea sin cubrir (el arranque directo del
  servidor), que no se ejecuta al usar el `TestClient` en las pruebas.

### Frontend

La cobertura global (33.78% de statements) es baja porque Vitest mide **todo**
`src/` y sólo los módulos con pruebas unitarias aportan cobertura:

- **`format.js` y `links.js` (100%)**: funciones puras de fechas, tamaños y
  validación de enlaces, con todas sus ramas cubiertas.
- **`useFocusTrap.js` (97.14%)**: la única línea no cubierta es la guarda
  `if (!container)`, imposible de excitar cuando el `ref` siempre está montado.
- **`TaskForm.jsx`, `TaskFields.jsx` y `TaskCard.jsx`**: los porcentajes reflejan
  las ramas de borradores (archivos, límites) y de edición que no se ejercitan en
  todos sus caminos; la interacción completa de esos componentes ya se valida
  de punta a punta con Playwright en la Etapa 6.
- El resto (`App.jsx`, `api.js`, `Board.jsx`, `Column.jsx`, los componentes de
  detalle, `TaskDetailModal.jsx`, `Toast.jsx`, `ErrorBoundary.jsx` y `main.jsx`)
  no tiene pruebas unitarias: se cubren por las **11 pruebas de interfaz de la
  Etapa 6** y por la verificación manual, que Vitest no contabiliza.

## Relación con los tipos de prueba de las etapas previas

| Etapa | Tipo de prueba | Herramienta | Cómo se relaciona con la cobertura medida |
|-------|----------------|-------------|-------------------------------------------|
| Etapa 6 | Sistema (API, UI, caja blanca) | httpx + Playwright | Ejercita routers, reglas de negocio e interfaz de punta a punta. No se contabiliza en pytest-cov ni en Vitest, por lo que explica huecos de `repository.py`, `routers/*` y componentes de React. |
| Etapa 8 | Unitarias | pytest | Base principal de la cobertura de backend sobre `schemas.py` y funciones de dominio. |
| Etapa 9 | Integración | pytest | Recorre capas completas (router → schemas → repository → SQLite), impulsando la cobertura de `repository.py`, `database.py` y `tasks.py`. |
| Etapa 13 | Regresión | pytest + suite de sistema | Reejecuta las pruebas previas; aporta a las mismas métricas que la Etapa 8/9. |

En conjunto, la cobertura de backend (84%) refleja lo que ejecutan las pruebas
automatizadas de pytest; los caminos de error y las variantes de consulta que
quedan afuera están cubiertos por la suite de sistema, que es de naturaleza
distinta y no se integra a esta medición.

## Conclusión

- **Backend:** 84% de statements (776 medidos, 126 sin cubrir). Los módulos con
  lógica pura y de datos están casi completos; los huecos se concentran en
  caminos de error y variantes de consulta que las pruebas de sistema cubren
  aparte.
- **Frontend:** se partió de **0%** (no existían pruebas unitarias). Con las
  pruebas agregadas, los módulos puros alcanzan el **100%** y los componentes
  bajo prueba entre 66% y 86%, con una cobertura global de 33.78% de statements
  sobre todo `src/`.
- La medición es reproducible con los comandos de este documento y las
  evidencias quedan registradas en `docs/evidencias/cobertura/`.
- Trabajo futuro sugerido: ampliar las pruebas unitarias del frontend a los
  componentes de detalle y al cliente `api.js`, y añadir a la medición de
  backend las rutas de error hoy cubiertas sólo por la suite de sistema.
