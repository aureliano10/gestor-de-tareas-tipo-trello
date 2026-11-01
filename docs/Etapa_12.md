# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 12 - TDD y refactorización

## Objetivo de la etapa

Aplicar el Desarrollo Dirigido por Pruebas (TDD) sobre una funcionalidad interna del sistema, mostrando el proceso completo **Prueba → implementación → ejecución → corrección/refactorización**, y realizar una refactorización sobre código existente explicando el problema del código original, la modificación realizada, por qué mejora el código y qué pruebas se usaron para comprobar que la funcionalidad siguió funcionando. Todos los cambios se hicieron sobre lógica interna, **sin modificar la API pública ni el modelo de datos** documentados en la Etapa 3.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| pytest | 9.2.0 |
| FastAPI | 0.136.3 |
| SQLite | 3.45.1 |
| ruff | 0.17.3 |
| Entorno | `.venv` del repositorio |

Las pruebas se ejecutan desde la raíz del repositorio y son autocontenidas: no requieren servidor en ejecución, porque cada una crea su propia base SQLite temporal con las variables `KANBAN_DB_PATH` y `KANBAN_STORAGE_PATH`.

## Parte 1 - Aplicación de TDD

### Funcionalidad elegida

Se eligió un **helper puro de cálculo de vencimiento**, `is_overdue(due_date, status, today)`, que decide si una tarea está vencida. La regla de negocio es la siguiente: una tarea está vencida cuando tiene fecha límite anterior a hoy **y** su estado no es "Terminada".

Este cálculo existía dentro de la función `_task_dict` del repositorio, escrito en línea y mezclado con el armado del diccionario de la tarea. Al ser lógica pura (no accede a la base ni al reloj salvo por un valor por defecto), es ideal para desarrollarla con TDD: se puede inyectar la fecha de referencia y comprobar la regla de forma aislada.

El helper se agregó al módulo `backend/app/repository.py` y **no** se tocó ningún endpoint, schema ni tabla.

### Momento RED - prueba que falla

Primero se escribió la prueba, **antes** de escribir el código de producción, en el archivo `backend/tests/test_unit_overdue.py`:

```python
def test_cp_un_19_is_overdue_regla_de_vencimiento():
    """Una tarea vence cuando su fecha es anterior a hoy y no está terminada."""
    today = "2026-11-01"

    # Vencida: fecha anterior a hoy y tarea no finalizada.
    assert is_overdue("2026-10-31", "Pendiente", today) is True
    assert is_overdue("2026-10-31", "En curso", today) is True

    # No vencida: la fecha de hoy o una futura no vencen.
    assert is_overdue("2026-11-01", "Pendiente", today) is False
    assert is_overdue("2026-11-02", "Pendiente", today) is False

    # No vencida: una tarea terminada nunca se marca como vencida.
    assert is_overdue("2026-10-31", "Terminada", today) is False

    # No vencida: sin fecha límite.
    assert is_overdue(None, "Pendiente", today) is False
```

Como el helper todavía no existía, la corrida falló al importarlo (RED). Salida real de `pytest backend/tests/test_unit_overdue.py -v`:

```text
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
_____________ ERROR collecting backend/tests/test_unit_overdue.py ______________
ImportError while importing test module '.../backend/tests/test_unit_overdue.py'.
backend/tests/test_unit_overdue.py:10: in <module>
    from app.repository import is_overdue
E   ImportError: cannot import name 'is_overdue' from 'app.repository'
=========================== short test summary info ============================
ERROR backend/tests/test_unit_overdue.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.27s ===============================
```

### Momento GREEN - la implementación mínima

Se implementó **lo mínimo** para que la prueba pasara. El helper no calcula nada más que lo exigido por la especificación y deja inyectar la fecha de hoy para poder probarlo de forma aislada:

```python
def is_overdue(
    due_date: Optional[str], status: str, today: Optional[str] = None
) -> bool:
    """Indica si una tarea está vencida.

    Una tarea está vencida cuando tiene fecha límite anterior a hoy y su
    estado no es "Terminada". El parámetro ``today`` permite inyectar la
    fecha de referencia (formato ISO) para comprobar la regla de forma
    aislada, sin depender del reloj del sistema.
    """
    if not due_date or status == DONE_STATUS:
        return False
    return due_date < (today or _today_iso())
```

Salida real de la misma corrida, ahora en verde (GREEN):

```text
backend/tests/test_unit_overdue.py::test_cp_un_19_is_overdue_regla_de_vencimiento PASSED [100%]
============================== 1 passed in 0.15s ===============================
```

### Momento REFACTOR - limpieza y reutilización

Una vez en verde, se limpió el código: en lugar de mantener la misma regla escrita de nuevo dentro de `_task_dict`, se reemplazó la expresión en línea por la llamada al helper ya probado:

```python
        "overdue": is_overdue(due_date, row["status"]),
```

Así la regla de vencimiento queda definida en **un solo lugar** y con sus propias pruebas, y `_task_dict` solo se ocupa de armar el diccionario de la tarea.

## Parte 2 - Refactorización de código existente

### Problema que presentaba el código original

La función `update_task` mezclaba la actualización de datos con el **registro del historial de actividad**. El bloque que calculaba qué etiquetas se habían quitado y cuáles se habían agregado estaba **duplicado** casi textualmente para los enlaces:

- La rama de etiquetas construía dos conjuntos (`new_keys` y `old_keys`), y luego dos bucles `for` para registrar "Etiqueta eliminada" y "Etiqueta agregada".
- La rama de enlaces repetía la misma estructura con `new_urls` y `old_urls`, otros dos bucles y mensajes "Enlace eliminado" y "Enlace agregado".

Ese patrón (comparar el conjunto anterior con el nuevo por clave y registrar altas y bajas) aparecía dos veces dentro de una función que ya era larga, lo que dificultaba la lectura y obligaba a mantener la misma lógica en varios lugares.

### Modificación realizada

Se extrajo un helper único, `_log_set_changes`, que recibe los conjuntos anterior y nuevo (como pares `clave, texto`) y dos plantillas de mensaje, y registra las bajas y las altas:

```python
def _log_set_changes(
    conn,
    task_id: int,
    old_items: list[tuple[str, str]],
    new_items: list[tuple[str, str]],
    removed_message: str,
    added_message: str,
) -> None:
    """Registra las bajas y altas de un conjunto comparando por clave.

    ``old_items`` y ``new_items`` son listas de pares ``(clave, texto)``.
    ``removed_message`` y ``added_message`` son plantillas que reciben el
    texto visible de cada elemento (por ejemplo ``"Etiqueta agregada: {}"``).
    """
    new_keys = {key for key, _ in new_items}
    old_keys = {key for key, _ in old_items}
    for key, display in old_items:
        if key not in new_keys:
            _log_activity(conn, task_id, removed_message.format(display))
    for key, display in new_items:
        if key not in old_keys:
            _log_activity(conn, task_id, added_message.format(display))
```

Las dos ramas de `update_task` quedaron reducidas a preparar los pares y delegar el registro:

```python
        if tags is not None:
            current_tags = _tags_of(conn, task_id)
            _set_tags(conn, task_id, tags)
            _log_set_changes(
                conn,
                task_id,
                [(name.lower(), name) for name in current_tags],
                [(name.lower(), name) for name in tags],
                "Etiqueta eliminada: {}",
                "Etiqueta agregada: {}",
            )
        if normalized_links is not None:
            current_links = _links_of(conn, task_id)
            _set_links(conn, task_id, normalized_links)
            _log_set_changes(
                conn,
                task_id,
                [
                    (link["url"].lower(), link["label"] or link["url"])
                    for link in current_links
                ],
                [(url.lower(), label or url) for url, label in normalized_links],
                "Enlace eliminado: {}",
                "Enlace agregado: {}",
            )
```

El diff completo está guardado como evidencia en `docs/evidencias/etapa_12/refactor_diff.txt`. Los mensajes del historial se mantuvieron **idénticos** ("Etiqueta eliminada: …", "Etiqueta agregada: …", "Enlace eliminado: …", "Enlace agregado: …"), por lo que el comportamiento observable no cambió.

### Por qué la modificación mejora el código

| Criterio | Antes | Después |
|----------|-------|---------|
| Duplicación | El mismo patrón de comparación y registro estaba repetido para etiquetas y para enlaces. | Una única implementación en `_log_set_changes` que ambas ramas reutilizan. |
| Cohesión | `update_task` tenía que conocer, además de actualizar, el detalle de cómo calcular las diferencias. | `update_task` delega esa responsabilidad y queda más enfocado en actualizar la tarea. |
| Legibilidad | Cuatro bucles dispersos entre los dos bloques. | Cada rama prepara sus pares y hace una sola llamada; el diff es más corto. |
| Mantenimiento | Un cambio en la forma de registrar el historial obligaba a editar dos lugares. | Se edita un solo lugar. |
| Testeabilidad | La regla de vencimiento no se podía probar aislada porque estaba en línea. | `is_overdue` es una función pura, probada por invocación directa. |

### Qué pruebas se usaron para comprobar que siguió funcionando

- La prueba del helper de TDD: `test_cp_un_19_is_overdue_regla_de_vencimiento` (RED → GREEN).
- La **suite completa** de `pytest backend/tests` (25 casos), que incluye las integraciones que verifican el historial y los mensajes, en particular `test_cp_in_06_historial_de_actividad` y los casos de API que comprueban "Etiqueta eliminada: uno" y "Etiqueta agregada: tres" (CP-TAG-04).
- La **verificación estática** con `ruff check backend scripts`, para asegurar el estilo.

## Verificación final

Todas las pruebas se ejecutan desde la raíz. Resultado real de la suite completa tras el refactor:

```text
$ .venv/bin/python -m pytest backend/tests -v
...
======================== 25 passed, 1 warning in 1.28s =========================
```

El aviso (`StarletteDeprecationWarning` del `TestClient`) no afecta el resultado. Las **24 pruebas preexistentes** (18 unitarias + 6 de integración) siguen en verde, y se sumó el caso de TDD `CP-UN-19`, totalizando **25 aprobadas**.

Verificación de estilo:

```text
$ .venv/bin/ruff check backend scripts
All checks passed!
```

## Resumen de resultados

| Métrica | Valor |
|---------|-------|
| Pruebas preexistentes (Etapas 8 y 9) | 24 |
| Casos nuevos de TDD (`CP-UN-19`) | 1 |
| Casos ejecutados tras el refactor | 25 |
| Pasados | 25 |
| Fallados | 0 |
| ruff | Sin observaciones |

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Corrida RED (prueba que falla) | `docs/evidencias/etapa_12/pytest_red.txt` |
| Corrida GREEN (prueba que pasa) | `docs/evidencias/etapa_12/pytest_green.txt` |
| Suite completa tras el refactor | `docs/evidencias/etapa_12/pytest_final.txt` |
| Diff antes/después del refactor | `docs/evidencias/etapa_12/refactor_diff.txt` |
| Verificación de estilo (ruff) | `docs/evidencias/etapa_12/ruff.txt` |
| Código del helper y de las pruebas | `backend/app/repository.py`, `backend/tests/test_unit_overdue.py` |

## Reproducibilidad

Desde la raíz del repositorio:

1. Correr la prueba del helper de TDD: `.venv/bin/python -m pytest backend/tests/test_unit_overdue.py -v`.
2. Correr la suite completa: `.venv/bin/python -m pytest backend/tests -v`.
3. Verificar el estilo: `.venv/bin/ruff check backend scripts`.

## Conclusión de la etapa

Se aplicó TDD de punta a punta sobre el helper `is_overdue`: se escribió primero la prueba que falla (RED, con la salida real del `ImportError`), se implementó lo mínimo para pasar (GREEN) y se limpió reutilizando el helper en `_task_dict` (REFACTOR). Además se refactorizó una duplicación concreta de `update_task` extrayendo `_log_set_changes`, sin cambiar los mensajes del historial ni la API pública. Las 24 pruebas preexistentes continúan aprobadas, se agregó un caso nuevo y `ruff` quedó sin observaciones, de modo que el comportamiento observable del sistema se mantuvo intacto.

## Próxima etapa

La Etapa 13 consistirá en las pruebas de regresión sobre el código modificado: se documentará la línea base, la modificación introducida y la batería de regresión reejecutada con sus resultados.
