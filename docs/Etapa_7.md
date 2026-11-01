# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 7 - Registro y seguimiento de defectos

## Objetivo de la etapa

Registrar todos los defectos detectados durante el desarrollo y la verificación del sistema con una plantilla de reporte uniforme, documentar en cada caso la causa raíz, la corrección aplicada y su verificación, y realizar el seguimiento de los defectos hasta su resolución.

## Alcance

Se registran los defectos identificados a lo largo de la Actividad Integradora: un defecto de severidad Alta en el backend, un defecto de severidad Baja en el frontend y dos defectos de severidad Baja en los propios scripts de prueba. Todos quedaron resueltos y verificados.

Los defectos se originaron en distintas etapas, pero su registro y su seguimiento se centralizan en esta etapa, tal como pide la consigna. No se detectaron defectos funcionales durante la ejecución de la Etapa 6; el defecto de backend afectó datos preexistentes y se manifestó al reutilizar una base creada con el esquema anterior.

## Proceso de registro y seguimiento

Cada defecto encontrado se documenta con una ficha que respeta la siguiente plantilla de reporte:

- **ID del defecto:** identificador único con el formato `DEF-XX`.
- **Fecha:** fecha de detección.
- **Descripción:** resumen del comportamiento observado.
- **Funcionalidad afectada:** módulo o caso de prueba implicado.
- **Pasos para reproducirlo:** secuencia mínima y determinista.
- **Resultado esperado:** comportamiento correcto según los requisitos.
- **Resultado obtenido:** comportamiento real observado.
- **Evidencia:** ubicación de la traza, el fragmento de código o el registro de ejecución.
- **Severidad:** impacto del defecto sobre el sistema.
- **Prioridad:** urgencia de la corrección.
- **Estado:** situación actual dentro del ciclo de vida.

Además, cada ficha incorpora la **causa raíz**, la **corrección aplicada** y la **fecha de cierre**.

Ciclo de vida utilizado para el seguimiento:

| Estado | Significado |
|--------|-------------|
| Nuevo | El defecto fue registrado con su ficha completa. |
| En análisis | Se determinó la causa raíz y el alcance del problema. |
| En corrección | Se aplicó el cambio en el código. |
| Resuelto | La corrección está integrada y a la espera de verificación. |
| Verificado | La corrección se comprobó con casos de prueba y no reapareció. |

Criterios de severidad y prioridad:

- **Severidad Alta:** impide usar una funcionalidad completa o corrompe datos. **Media:** degrada una funcionalidad sin bloquearla. **Baja:** problema visual, de estilo o de la herramienta de prueba.
- **Prioridad Alta:** debe corregirse antes de continuar con el trabajo dependiente. **Media:** se corrige en el corto plazo. **Baja:** puede diferirse sin afectar al usuario.

## Resumen de defectos

| ID | Fecha | Funcionalidad afectada | Severidad | Prioridad | Estado |
|----|-------|------------------------|-----------|-----------|--------|
| DEF-01 | 30/10/2026 | Alta de subtareas y adjuntos (backend) | Alta | Alta | Verificado |
| DEF-02 | 30/10/2026 | Alta de tarea desde la interfaz | Baja | Media | Verificado |
| DEF-03 | 01/11/2026 | Caso de prueba de interfaz CP-UI-09 | Baja | Baja | Verificado |
| DEF-04 | 01/11/2026 | Scripts de prueba de la Etapa 6 | Baja | Baja | Verificado |

## Fichas de defectos

### DEF-01

- ID: DEF-01
- Fecha: 30/10/2026
- Descripción: agregar una subtarea a una tarea existente devolvía HTTP 500. La misma causa afectaba la carga de adjuntos, porque ambas tablas dependen de `tasks`.
- Funcionalidad afectada: checklist de subtareas (y adjuntos, misma causa).
- Pasos para reproducirlo: 1) partir de una base creada con el esquema anterior; 2) iniciar el backend, que ejecuta la migración `_migrate_tasks`; 3) `POST /api/tasks` (responde 201); 4) `POST /api/tasks/{id}/subtasks` (responde 500).
- Resultado esperado: HTTP 201 con la subtarea creada.
- Resultado obtenido: HTTP 500 por `OperationalError: no such table: main.tasks_legacy`.
- Evidencia: `docs/evidencias/etapa_7/def_01_migracion_antes_despues.md` y `docs/evidencias/etapa_7/def_01_traza_error.txt`; traza `ERROR al insertar subtarea -> OperationalError : no such table: main.tasks_legacy`.
- Severidad: Alta.
- Prioridad: Alta.
- Estado: Verificado.
- Causa raíz: la migración `_migrate_tasks` de `backend/app/database.py` recreaba la tabla `tasks` con `ALTER TABLE tasks RENAME TO tasks_legacy`. Al renombrar, SQLite reescribe las claves foráneas de las tablas dependientes (`subtasks` y `attachments`) para que apunten a `tasks_legacy`; al eliminarse esa tabla con `DROP`, las referencias quedaron rotas y todo `INSERT` fallaba.
- Corrección aplicada: migración aditiva con `ALTER TABLE ... ADD COLUMN` y detección por columnas (`REQUIRED_TASK_COLUMNS`), sin renombrar ni recrear `tasks`. Ver `docs/evidencias/etapa_7/def_01_migracion_antes_despues.md`.
- Fecha de cierre: 30/10/2026.

### DEF-02

- ID: DEF-02
- Fecha: 30/10/2026
- Descripción: el botón de alta de tarea se mostraba sin estilo.
- Funcionalidad afectada: alta de tarea desde la interfaz.
- Pasos para reproducirlo: 1) abrir el tablero en `http://127.0.0.1:5173`; 2) observar el botón de envío del formulario "Nueva tarea"; 3) compararlo con el resto de los botones de la interfaz.
- Resultado esperado: botón con el estilo primario del sistema.
- Resultado obtenido: botón crudo del navegador, visualmente inconsistente con el resto de la interfaz.
- Evidencia: `docs/evidencias/etapa_7/def_02_y_03_evidencia.md`.
- Severidad: Baja.
- Prioridad: Media.
- Estado: Verificado.
- Causa raíz: el `<button type="submit">` de `frontend/src/components/TaskForm.jsx` no tenía atributo `className`, por lo que el navegador aplicaba su estilo por defecto.
- Corrección aplicada: se agregó la clase del botón primario (`className="btn"`), consistente con el resto de la interfaz.
- Fecha de cierre: 30/10/2026.

### DEF-03

- ID: DEF-03
- Fecha: 01/11/2026
- Descripción: el caso de interfaz CP-UI-09 fallaba por un locator compuesto mal construido dentro del script (provocaba timeout), no por un defecto del sistema.
- Funcionalidad afectada: caso de prueba de interfaz CP-UI-09 (prioridad y responsable).
- Pasos para reproducirlo: 1) dar de alta una tarea con prioridad "Alta" y responsable "Ana"; 2) ejecutar el caso CP-UI-09 con el locator compuesto anterior; 3) observar el timeout al ubicar la tarjeta.
- Resultado esperado: el caso debía ubicar la tarjeta y leer la insignia de prioridad y el responsable.
- Resultado obtenido: timeout del locator; el sistema se comportaba correctamente.
- Evidencia: `docs/evidencias/etapa_7/def_02_y_03_evidencia.md`; resultado vigente en `docs/evidencias/etapa_6/resultados_ui.json`.
- Severidad: Baja.
- Prioridad: Baja.
- Estado: Verificado.
- Causa raíz: el locator estaba construido a mano dentro del script y no resolvía el elemento, por lo que Playwright agotaba el tiempo de espera.
- Corrección aplicada: se usó el helper `task_in` del arnés `scripts/etapa_6/ui_helpers.py`, que compone el locator de forma consistente con el resto de los casos.
- Fecha de cierre: 01/11/2026.

### DEF-04

- ID: DEF-04
- Fecha: 01/11/2026
- Descripción: líneas que excedían el límite de longitud de Ruff en los scripts de prueba nuevos.
- Funcionalidad afectada: scripts de prueba de la Etapa 6 (`scripts/etapa_6/`).
- Pasos para reproducirlo: 1) ejecutar Ruff sobre `scripts/etapa_6/`; 2) observar los avisos por líneas demasiado largas en los casos nuevos.
- Resultado esperado: los scripts debían respetar el límite de líneas de Ruff.
- Resultado obtenido: avisos de línea larga en `ejecutar_api.py` y `ejecutar_ui.py`.
- Evidencia: `docs/evidencias/etapa_7/def_04_ruff.txt` (`git show c60e4ef --stat`).
- Severidad: Baja.
- Prioridad: Baja.
- Estado: Verificado.
- Causa raíz: los casos de prueba agregados en la Etapa 7 se escribieron con líneas más largas que el límite configurado.
- Corrección aplicada: se ajustaron las líneas que excedían el límite (43 en `ejecutar_api.py` y 4 en `ejecutar_ui.py`), en el commit `c60e4ef`.
- Fecha de cierre: 01/11/2026.

## Seguimiento de defectos

Transición de estado de cada defecto:

| ID | Nuevo | En análisis | En corrección | Resuelto | Verificado |
|----|-------|-------------|---------------|----------|------------|
| DEF-01 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 01/11/2026 |
| DEF-02 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 30/10/2026 | 01/11/2026 |
| DEF-03 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 |
| DEF-04 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 | 01/11/2026 |

Comprobación de cada corrección:

- **DEF-01:** la migración aditiva se ejecuta al iniciar el backend sin renombrar `tasks`, por lo que las altas de subtareas y adjuntos vuelven a responder HTTP 201. La funcionalidad quedó cubierta por los casos `CP-SUB-01` y `CP-SUB-04` (checklist) y `CP-ADJ-01` a `CP-ADJ-06` y `CP-CB-04` (adjuntos), que pasaron en la corrida del 01/11/2026.
- **DEF-02:** el botón de alta se renderiza con la clase primaria y el flujo de alta funcionó en la interfaz, comprobado por `CP-UI-01` (alta desde el formulario) y `CP-UI-09` (alta con prioridad y responsable).
- **DEF-03:** el caso `CP-UI-09` pasó con el helper `task_in`; el registro de `docs/evidencias/etapa_6/resultados_ui.json` muestra `insignia='Alta'; responsable='Ana'` y la corrida figura como APROBADO en `docs/evidencias/etapa_6/ejecucion.log`.
- **DEF-04:** los scripts quedaron sin avisos de línea larga y la corrida completa volvió a ejecutarse sin errores de estilo, reproduciendo el resultado de 80/80 casos aprobados.

La corrida del 01/11/2026 ejecutó los 80 casos de la Etapa 6 (62 de API, 11 de interfaz y 7 de caja blanca) con 100% de aprobación, lo que confirma que las correcciones no introdujeron regresiones.

## Métricas

| Métrica | Valor |
|---------|-------|
| Defectos registrados | 4 |
| Defectos resueltos | 4 |
| Defectos verificados | 4 |
| Defectos abiertos | 0 |

Defectos por severidad:

| Severidad | Cantidad |
|-----------|----------|
| Alta | 1 |
| Media | 0 |
| Baja | 3 |
| **Total** | **4** |

Defectos por prioridad:

| Prioridad | Cantidad |
|-----------|----------|
| Alta | 1 |
| Media | 1 |
| Baja | 2 |
| **Total** | **4** |

Defectos por estado:

| Estado | Cantidad |
|--------|----------|
| Nuevo | 0 |
| En análisis | 0 |
| En corrección | 0 |
| Resuelto | 0 |
| Verificado | 4 |
| **Total** | **4** |

Defectos por origen:

| Origen | Cantidad |
|--------|----------|
| Backend (datos y esquema) | 1 |
| Frontend (estilo) | 1 |
| Scripts de prueba | 2 |
| **Total** | **4** |

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Comparación antes/después de la migración (DEF-01) | `docs/evidencias/etapa_7/def_01_migracion_antes_despues.md` |
| Traza del error y reproducción (DEF-01) | `docs/evidencias/etapa_7/def_01_traza_error.txt` |
| Evidencia del botón y del locator (DEF-02 y DEF-03) | `docs/evidencias/etapa_7/def_02_y_03_evidencia.md` |
| Estilo de los scripts (DEF-04) | `docs/evidencias/etapa_7/def_04_ruff.txt` |
| Resultados y log de la corrida que verifica las correcciones | `docs/evidencias/etapa_6/resultados_ui.json` y `docs/evidencias/etapa_6/ejecucion.log` |

Todas las evidencias se basan en fragmentos de código obtenidos del historial de Git y en registros de ejecución; no se incluyen capturas de pantalla inventadas.

## Conclusión de la etapa

Se registraron cuatro defectos con la plantilla exigida y se realizó su seguimiento hasta la resolución y verificación. El defecto de mayor impacto (DEF-01) fue un problema de migración de esquema en el backend, con causa raíz identificada y corregido mediante una migración aditiva; los tres restantes fueron de severidad Baja (un defecto de estilo en el frontend y dos defectos de los propios scripts de prueba). Al cierre de la etapa no quedan defectos abiertos: los cuatro están verificados con casos de prueba que hoy pasan y la corrida completa de la Etapa 6 mantiene un 100% de aprobación, sin regresiones.

## Próxima etapa

La etapa siguiente consistirá en la elaboración del informe final de la Actividad Integradora, integrando los requisitos, el diseño, el desarrollo y los resultados de verificación y validación, con el registro de defectos como insumo para las conclusiones.
