# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 13 - Pruebas de regresión

## Objetivo de la etapa

Luego de las modificaciones realizadas en la Etapa 12 (un helper nuevo desarrollado con TDD y una refactorización con extracción de lógica duplicada), ejecutar nuevamente un conjunto de pruebas para comprobar que los cambios realizados **no afectaron funcionalidades que antes funcionaban correctamente**. Se documentan las pruebas realizadas antes del cambio (línea base), la modificación realizada, la batería de regresión elegida y los resultados obtenidos.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| pytest | 9.2.0 |
| FastAPI | 0.136.3 |
| Uvicorn | 0.49.0 |
| SQLite | 3.45.1 |
| httpx | 0.28.1 |
| Node.js | v24.14.1 |
| Playwright | 1.64.1, con `channel="chrome"` y modo headless |
| Backend de pruebas | `http://127.0.0.1:8000` con `KANBAN_DB_PATH=/tmp/kanban_etapa6.db` |
| Frontend | `http://127.0.0.1:5173` con Vite |

La corrida se hizo sobre una base y un almacenamiento temporales para no afectar los datos reales del proyecto. Al terminar se restauró el backend normal (con la base real).

## Línea base (estado ANTES del cambio)

Antes de la Etapa 12 el sistema contaba con **104 casos automatizados aprobados**, según las evidencias de las etapas 8, 9, 10 y 11:

| Conjunto | Herramienta | Casos | Aprobados | Evidencia de referencia |
|----------|-------------|-------|-----------|--------------------------|
| Pruebas unitarias | pytest | 18 | 18 | `docs/evidencias/etapa_8/`, `docs/evidencias/etapa_11/` |
| Pruebas de integración | pytest + `TestClient` | 6 | 6 | `docs/evidencias/etapa_9/`, `docs/evidencias/etapa_11/` |
| Subtotal backend | pytest | 24 | 24 | — |
| Casos de API | httpx | 62 | 62 | `docs/evidencias/etapa_10/resultados_api.json` |
| Casos de interfaz | Playwright | 11 | 11 | `docs/evidencias/etapa_10/resultados_ui.json` |
| Casos de caja blanca | Runner propio | 7 | 7 | `docs/evidencias/etapa_10/resultados_caja_blanca.json` |
| Subtotal sistema | — | 80 | 80 | `docs/evidencias/etapa_10/resumen_resultados.json` |

Línea base consolidada: **24/24 en el backend** y **80/80 en la suite de sistema**, es decir **104/104**. Resultados literales de referencia: unitarias `18 passed`, integración `6 passed`, y suite de sistema `80/80 aprobados, 0 fallidos`.

## Modificación realizada (Etapa 12)

La modificación sobre la que se ejecuta la regresión es la de la Etapa 12, siempre sobre lógica interna y **sin cambiar la API pública ni el modelo de datos**:

| N.º | Tipo | Descripción | Riesgo de regresión |
|-----|------|-------------|---------------------|
| 1 | TDD - helper nuevo | Se agregó `is_overdue(due_date, status, today)` en `backend/app/repository.py` y se adoptó en `_task_dict` para calcular el campo `overdue` de cada tarea. | El cálculo del vencimiento es el que ve el usuario en la tarjeta y el que alimenta el filtro `overdue`; un error cambiaría el resultado del listado. |
| 2 | Refactorización | En `update_task` se extrajo `_log_set_changes` para eliminar la lógica duplicada entre etiquetas y enlaces, manteniendo los mensajes del historial idénticos ("Etiqueta eliminada/agregada", "Enlace eliminado/agregado"). | El historial de actividad es observable por API e interfaz; un cambio en los mensajes o en el orden de las entradas rompería casos existentes. |

Ambos cambios tocan rutas usadas por varios requisitos (RF3, RF4, RF5, RF10, RF18, RF19, RF20, RF21, RF22), por lo que la regresión debe cubrir esos flujos de punta a punta.

## Batería de regresión elegida y su justificación

Se reejecutó **toda** la batería automatizada existente, porque es la red de seguridad ya definida y alcanza los dos frentes tocados por el cambio (vencimiento e historial) además del resto del sistema:

| Conjunto | Comando | Casos | Por qué se incluye |
|----------|---------|-------|--------------------|
| Backend (pytest) | `.venv/bin/python -m pytest backend/tests -v` | 25 | Cubre las unitarias (incluido el caso del helper nuevo) y las 6 de integración de punta a punta (routers → schemas → repository → SQLite). Las integraciones ejercitan el vencimiento (`CP-IN-05`) y el historial (`CP-IN-06`). |
| API (httpx) | `.venv/bin/python scripts/etapa_6/ejecutar_api.py` | 62 | Verifica el contrato HTTP real: filtro `overdue`, orden por fecha, historial de actividad con los mensajes de etiquetas (CP-TAG-04), etc. |
| Interfaz (Playwright) | `.venv/bin/python scripts/etapa_6/ejecutar_ui.py` | 11 | Comprueba que la tarjeta muestra la insignia de vencimiento, el tablero y el detalle siguen operativos. |
| Caja blanca | `.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py` | 7 | Cubre ramas de decisión (límites, reglas de negocio y reordenamiento) por invocación directa y sobre la interfaz. |
| Consolidación | `.venv/bin/python scripts/etapa_6/consolidar.py` | — | Reúne los resultados de los tres grupos y produce el resumen 80/80. |

Criterio de aprobación: un caso aprobado requiere que **todas** sus comprobaciones se cumplan; si alguna falla, el caso queda Fallido. La regresión se considera satisfactoria si ningún caso que antes aprobaba pasa a fallar.

## Resultados obtenidos

### Pruebas de backend (pytest)

Salida real de la corrida (evidencia completa en `docs/evidencias/etapa_13/pytest_regresion.txt`):

```text
$ .venv/bin/python -m pytest backend/tests -v
...
======================== 25 passed, 1 warning in 1.25s =========================
```

| Subconjunto | Línea base | Regresión | Resultado |
|-------------|------------|-----------|-----------|
| Pruebas unitarias | 18/18 | 19/19 | Aprobado |
| Pruebas de integración | 6/6 | 6/6 | Aprobado |
| **Total backend** | **24/24** | **25/25** | **Aprobado** |

El aviso (`StarletteDeprecationWarning` del `TestClient`) no afecta el resultado. Las **24 pruebas preexistentes siguen aprobadas** y se incorpora `CP-UN-19` (el caso del helper desarrollado con TDD).

### Suite de sistema (API + interfaz + caja blanca)

Salida real de la consolidación (evidencia completa en `docs/evidencias/etapa_13/suite_consolidada.txt`):

```text
$ .venv/bin/python scripts/etapa_6/consolidar.py
Actualizado: /home/marucha/Documentos/final_aimar/docs/Etapa_5.md
Total: 80/80 aprobados, 0 fallidos
  api: 62/62
  ui: 11/11
  caja_blanca: 7/7
```

| Grupo | Línea base | Regresión | Resultado |
|-------|------------|-----------|-----------|
| API (httpx) | 62/62 | 62/62 | Aprobado |
| Interfaz (Playwright) | 11/11 | 11/11 | Aprobado |
| Caja blanca | 7/7 | 7/7 | Aprobado |
| **Total sistema** | **80/80** | **80/80** | **Aprobado** |

### Resumen de la regresión

| Conjunto | Antes | Después | Fallidos | Veredicto |
|----------|-------|---------|----------|-----------|
| Backend (pytest) | 24/24 | 25/25 | 0 | Sin regresiones |
| Sistema (API + UI + caja blanca) | 80/80 | 80/80 | 0 | Sin regresiones |
| **Total** | **104/104** | **105/105** | **0** | **Sin regresiones** |

Los casos directamente relacionados con los cambios se comportaron igual que en la línea base: el campo `overdue` se listó y filtró correctamente (CP-IN-05, CP-FEC-01/02, CP-ORD-01/02) y el historial de etiquetas conservó sus mensajes (CP-TAG-04, CP-IN-06, CP-HIS-01/02).

## Conclusión

La regresión se aprobó en su totalidad: **25/25 casos de backend** y **80/80 casos de sistema**, sin ningún caso que antes aprobara y ahora falle. El helper `is_overdue` y la refactorización `_log_set_changes` de la Etapa 12 **no introdujeron regresiones**: el comportamiento observable del sistema (API pública, modelo de datos, campo de vencimiento, historial de actividad y tablero) se mantuvo idéntico, y el único cambio en el conteo es la suma del caso nuevo de TDD (`CP-UN-19`). La batería de regresión reejecutada queda como evidencia real en `docs/evidencias/etapa_13/`.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Corrida de pytest (backend) | `docs/evidencias/etapa_13/pytest_regresion.txt` |
| Salida de los 62 casos de API | `docs/evidencias/etapa_13/suite_api.txt` |
| Salida de los 11 casos de interfaz | `docs/evidencias/etapa_13/suite_ui.txt` |
| Salida de los 7 casos de caja blanca | `docs/evidencias/etapa_13/suite_caja_blanca.txt` |
| Salida consolidada de la suite | `docs/evidencias/etapa_13/suite_consolidada.txt` |
| Resultados de API | `docs/evidencias/etapa_13/resultados_api.json` |
| Resultados de interfaz | `docs/evidencias/etapa_13/resultados_ui.json` |
| Resultados de caja blanca | `docs/evidencias/etapa_13/resultados_caja_blanca.json` |
| Resumen consolidado | `docs/evidencias/etapa_13/resumen_resultados.json` |

Nota: la ejecución de la suite de sistema **regenera** por diseño los archivos de `docs/evidencias/etapa_6/` (los resultados y capturas de la corrida de esa etapa). Los artefactos de la Etapa 6 se restauraron a su versión ya documentada, y se guardó en `docs/evidencias/etapa_13/` una copia de los resultados de esta corrida de regresión.

## Reproducibilidad

1. **Backend (sin servidor):** desde la raíz, `.venv/bin/python -m pytest backend/tests -v`.
2. **Suite de sistema:** detener el backend en curso con `pkill -f "uvicorn app.main:app"`.
3. Iniciar el backend de pruebas desde `backend/`:
   `KANBAN_DB_PATH=/tmp/kanban_etapa6.db KANBAN_STORAGE_PATH=/tmp/kanban_etapa6_storage ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
   y verificar `GET /api/health`.
4. Con el frontend en `http://127.0.0.1:5173`, ejecutar desde la raíz:
   `.venv/bin/python scripts/etapa_6/ejecutar_api.py`,
   `.venv/bin/python scripts/etapa_6/ejecutar_ui.py`,
   `.venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py` y
   `.venv/bin/python scripts/etapa_6/consolidar.py`.
5. Restaurar el backend normal desde `backend/`:
   `../.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
   (sin `KANBAN_DB_PATH`) y verificar el health en 200.
