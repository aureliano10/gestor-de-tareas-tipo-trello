# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 30/10/2026

# Etapa 4 - Verificación del software

## Objetivo de la etapa

Realizar actividades de verificación sobre los requisitos, el diseño, el código y la documentación del sistema, registrar los problemas encontrados y aplicar las correcciones correspondientes, comprobando luego que las correcciones hayan quedado resueltas.

## Alcance

Esta etapa es de **verificación estática**: se revisa que el producto se esté construyendo correctamente. No se ejecutan todavía los casos de prueba formales ni se realiza la validación con usuarios, actividades que corresponden a las etapas 5 a 10.

Se revisaron:

- Los requisitos funcionales y las restricciones definidos en la Etapa 1.
- La coherencia entre el diseño planificado en la Etapa 2 y la implementación real.
- El código del backend (rutas, esquemas, repositorio y base de datos).
- El código del frontend (estado principal y componentes).
- La documentación del repositorio (`README.md` y etapas anteriores).
- La consistencia entre requisitos y funcionalidades implementadas.

## Herramientas y configuración

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| Ruff | 0.17.3 | Análisis estático, errores y estilo en Python. |
| compileall | Python 3.12 | Verificación de compilación de los módulos Python. |
| ESLint | 9.39.5 | Análisis estático de JavaScript y React. |
| Vite build | 8.3.5 | Verificación de compilación del frontend. |

Configuraciones agregadas:

- `ruff.toml` en la raíz, con reglas `E`, `F`, `I` y `B`.
- `frontend/eslint.config.js` con configuración plana para React y hooks.
- Script `npm run lint` en `frontend/package.json`.
- `backend/requirements-dev.txt` con la dependencia de Ruff.

Comandos ejecutados:

```bash
ruff check backend
python -m compileall backend/app
npm run lint
npm run build
```

## 1. Verificación de requisitos

| Requisito | Implementación verificada | Resultado |
|-----------|---------------------------|-----------|
| RF1: registrar una tarea nueva | Endpoint `POST /api/tasks`, `repository.create_task` y formulario `TaskForm`. | Cumple |
| RF2: estado inicial `Pendiente` | Valor por defecto en `create_task` y `DEFAULT 'Pendiente'` en la tabla `tasks`. | Cumple |
| RF3: actualizar el estado de una tarea | Endpoint `PATCH /api/tasks/{id}/move`, `repository.move_task` y arrastre entre columnas. | Cumple |
| RF4: reordenar las tareas dentro de una columna | Campo `position`, funciones `_apply_move` y `_recalculate_positions`, y soltado dentro de la misma columna. | Cumple |
| RF5: editar título, descripción y fecha límite | Endpoint `PUT /api/tasks/{id}`, esquema `TaskUpdate` y edición dentro del detalle de la tarea. | Cumple |
| RF6: registrar subtareas en una tarea | Endpoint `POST /api/tasks/{id}/subtasks` y formulario del checklist. | Cumple |
| RF7: marcar y desmarcar subtareas | Endpoint `PATCH /api/subtasks/{id}` y casillas del checklist. | Cumple |
| RF8: eliminar subtareas | Endpoint `DELETE /api/subtasks/{id}` y botón de cada ítem. | Cumple |
| RF9: impedir finalizar una tarea con subtareas pendientes | `PendingSubtasksError` en `repository.move_task`, que la API traduce a HTTP 409. | Cumple |
| RF10: asignar fecha límite y señalar tareas vencidas | Campo `due_date`, validación en `TaskCreate` y estado `overdue` calculado en `_task_dict` y mostrado con la etiqueta de vencimiento. | Cumple |
| RF11: adjuntar archivos a una tarea | Endpoint `POST /api/tasks/{id}/attachments` (multipart) con validación de extensión, tamaño y cantidad. | Cumple |
| RF12: descargar los archivos adjuntos | Endpoint `GET /api/tasks/{id}/attachments/{attachment_id}` con `FileResponse`. | Cumple |
| RF13: eliminar archivos adjuntos | Endpoint `DELETE /api/tasks/{id}/attachments/{attachment_id}`, que borra también el archivo físico. | Cumple |
| RF14: eliminar un registro de tarea | Endpoint `DELETE /api/tasks/{id}` con confirmación previa en la interfaz. | Cumple |
| RF15: recuperar una tarea eliminada | Endpoint `POST /api/tasks/{id}/restore` y aviso con la acción "Deshacer". | Cumple |

| Restricción | Implementación verificada | Resultado |
|-------------|---------------------------|-----------|
| Título obligatorio y no vacío ni con solo espacios | Validación Pydantic, validación del formulario y `CHECK` en SQLite. | Cumple |
| Título de hasta 100 caracteres | Validación Pydantic, `maxLength` en el formulario y `CHECK` en SQLite. | Cumple |
| Descripción de hasta 500 caracteres | Validación Pydantic, `maxLength` en el formulario y `CHECK` en SQLite. | Cumple |
| Estados válidos únicamente | Tipo `Literal`, validación de la API y `CHECK` en SQLite. | Cumple |
| Fecha límite no anterior a hoy al crear | Validación en `TaskCreate` y atributo `min` del campo de fecha. Al editar sí se admite una fecha pasada. | Cumple |
| Hasta 3 adjuntos por tarea, de 5 MB y con extensiones permitidas | Validación en el router, validación previa en el detalle y `CHECK` de tamaño en SQLite. | Cumple |
| Posiciones sin huecos dentro de cada columna | Reindexado a 0..n-1 en `_recalculate_positions` y `_apply_move`. | Cumple |
| Persistencia de los cambios | Tablas `tasks`, `subtasks` y `attachments` en SQLite y operaciones del repositorio. | Cumple |

No se detectaron requisitos sin implementación ni funcionalidades implementadas que no estuvieran previstas en la Etapa 1.

## 2. Revisión del diseño

| Aspecto planificado en Etapa 2 | Verificación realizada | Resultado |
|--------------------------------|-------------------------|-----------|
| Frontend con React, JavaScript y CSS | Proyecto Vite con React y hoja de estilos propia. | Cumple |
| Backend con Python y FastAPI | Aplicación FastAPI con routers separados y modelos Pydantic. | Cumple |
| Base de datos SQLite | Tablas `tasks`, `subtasks` y `attachments` con claves foráneas. | Cumple |
| Separación de responsabilidades | Capas de rutas, esquemas, repositorio y base de datos. | Cumple |
| Archivos adjuntos | Almacenamiento en disco referenciado desde la base, con nombre único por archivo. | Cumple |
| Control de versiones con Git | Repositorio con commits por etapa. | Cumple parcialmente |
| Ramas separadas para frontend y backend | El trabajo se realizó sobre la rama `main`. | No cumple |

La desviación sobre las ramas se registra como el hallazgo VER-08 y se documenta su tratamiento.

## 3. Revisión de código

### Backend

Se revisó:

- Que las consultas SQL usen parámetros y no concatenación de cadenas.
- Que las conexiones se cierren correctamente y se confirme o revierta la transacción.
- Que las validaciones se apliquen antes de llegar a la base de datos.
- Que las operaciones sobre tareas, subtareas o adjuntos inexistentes respondan con HTTP 404.
- Que los datos inválidos respondan con HTTP 422.
- Que las reglas de negocio se concentren en el repositorio y no se dupliquen en las rutas.
- Que el nombre con el que se guarda un adjunto lo genere el servidor y no provenga del cliente.
- Que la configuración de CORS permita el origen del frontend.

Resultado: sin problemas de seguridad en las consultas; se detectó que la base de datos no aplicaba restricciones de integridad propias (VER-01), que una subtarea podía romper la regla de finalización (VER-02) y que el límite de tamaño de los adjuntos estaba definido dos veces (VER-03).

### Frontend

Se revisó:

- Que el formulario valide antes de enviar y muestre errores claros.
- Que el estado de carga y los errores se manejen en la interfaz.
- Que las operaciones exitosas actualicen el estado local sin recargar la página.
- Que la comunicación con la API sea coherente con los códigos HTTP del backend, incluido el 409 al finalizar con subtareas pendientes.
- Que el arrastre calcule la posición de destino sin contar la tarjeta que se está moviendo.
- Que la eliminación pida confirmación y que el aviso de deshacer se cierre solo.
- Que los eventos de teclado no se pisen entre componentes superpuestos.

Resultado: se detectaron mensajes de error duplicados (VER-10), que la tecla Escape cerraba dos capas a la vez (VER-04) y una etiqueta de vencimiento incorrecta para tareas finalizadas (VER-05).

## 4. Análisis estático

| Ejecución | Momento | Resultado |
|-----------|---------|-----------|
| `ruff check backend` | Inicial | Sin hallazgos. |
| `python -m compileall backend/app` | Inicial | Compilación correcta. |
| `npm run lint` | Inicial | Sin hallazgos. |
| `npm run build` | Inicial | Compilación correcta. |
| `ruff check backend` | Final | Sin hallazgos. |
| `python -m compileall backend/app` | Final | Compilación correcta. |
| `npm run lint` | Final | Sin hallazgos. |
| `npm run build` | Final | Compilación correcta. |

El análisis estático no detectó errores de sintaxis ni problemas de estilo en ninguna de las dos instancias. Los hallazgos de esta etapa provinieron de la inspección manual del código y de la revisión de consistencia entre capas.

## 5. Revisión de documentación

Se comparó el `README.md` con el comportamiento real del sistema.

| Aspecto revisado | Resultado |
|------------------|-----------|
| Comandos de instalación y ejecución | Correctos. |
| Endpoints documentados | Estaban desactualizados (VER-07). |
| Funcionalidades descritas | Incompletas (VER-07). |
| Reglas de negocio | Incompletas (VER-07, VER-09). |
| Versión de Node.js requerida | Inexacta (VER-06). |
| Instrucciones de análisis estático | Presentes, pero sin la dependencia de desarrollo (VER-07). |
| Restricciones de integridad en la base | No estaban reflejadas en la Etapa 3 (VER-09). |

## Registro de hallazgos

| ID | Aspecto | Descripción | Severidad | Acción realizada | Estado |
|----|---------|-------------|-----------|------------------|--------|
| VER-01 | Código / Base de datos | Las tablas no aplicaban restricciones de integridad para título, descripción, estado y tamaño de adjuntos; solo la API los validaba. | Media | Se agregaron restricciones `CHECK` y una migración automática para bases con el esquema anterior. | Corregido |
| VER-02 | Código / Reglas de negocio | Al desmarcar una subtarea de una tarea `Terminada`, la tarea quedaba finalizada con subtareas pendientes, contradiciendo la regla que aplica el propio sistema al moverla. | Media | El repositorio reabre la tarea (`En curso`) cuando se desmarca una subtarea. | Corregido |
| VER-03 | Código / Base de datos | El tamaño máximo de adjunto estaba escrito dos veces: como constante en `schemas.py` y como valor fijo en el `CHECK` de SQLite; podían desincronizarse. | Baja | `database.py` deriva los límites desde `schemas.py`, que queda como única fuente. | Corregido |
| VER-04 | Código / Interfaz | Con el diálogo de confirmación abierto sobre el detalle de una tarea, la tecla Escape cerraba el diálogo y el detalle al mismo tiempo. | Baja | El diálogo escucha el evento en fase de captura y detiene la propagación. | Corregido |
| VER-05 | Código / Interfaz | La etiqueta de vencimiento de una tarea finalizada mostraba "Venció el ..." aunque la fecha límite todavía no hubiera pasado. | Baja | La etiqueta distingue si la fecha ya pasó o no. | Corregido |
| VER-06 | Documentación | El `README.md` indicaba "Node.js 20 o superior", pero Vite 8 requiere Node.js 20.19 o superior (o 22.12 o superior). | Media | Se corrigió la versión requerida. | Corregido |
| VER-07 | Documentación | El `README.md` no documentaba los endpoints de subtareas, adjuntos y restauración, ni todas las funcionalidades y reglas del sistema. | Baja | Se completaron las secciones de funcionalidades, endpoints y reglas de negocio. | Corregido |
| VER-08 | Diseño / Git | La Etapa 2 preveía ramas separadas para frontend y backend, pero el trabajo se realizó sobre `main`. | Media | Se documenta la desviación y se mantiene una convención de commits por etapa sobre `main`. | Aceptado |
| VER-09 | Documentación | La Etapa 3 no reflejaba que la base de datos también aplica restricciones de integridad ni el modelo de datos completo. | Baja | Se actualizó la etapa con el modelo de datos y las restricciones. | Corregido |
| VER-10 | Código / Interfaz | Al fallar la creación de una tarea, el error se mostraba dos veces: en el aviso general y en el formulario. | Baja | Tanto el formulario como el detalle manejan su propio error, y el aviso general queda para las acciones del tablero. | Corregido |

## Correcciones aplicadas

| ID | Archivos modificados | Detalle de la corrección |
|----|----------------------|--------------------------|
| VER-01 | `backend/app/database.py` | Se agregaron `CHECK` para título, descripción, estado, fecha y tamaño de adjuntos. Se incorporó una migración que reconstruye la tabla si existe el esquema anterior. |
| VER-02 | `backend/app/repository.py` | `update_subtask` reabre la tarea a `En curso` cuando se desmarca una subtarea de una tarea finalizada. |
| VER-03 | `backend/app/database.py` | Los límites de título, descripción y adjuntos se toman de `schemas.py` en lugar de repetirse como valores fijos. |
| VER-04 | `frontend/src/components/ConfirmDialog.jsx` | El manejo de Escape se registra en fase de captura y detiene la propagación del evento. |
| VER-05 | `frontend/src/format.js` | `dueInfo` elige entre "Venció el ..." y "Vence el ..." según la fecha de una tarea finalizada. |
| VER-06 | `README.md` | Se precisó la versión de Node.js compatible con Vite 8. |
| VER-07 | `README.md` | Se documentaron todas las funcionalidades, los endpoints y las reglas de negocio. |
| VER-09 | `docs/Etapa_3.md`, `docs/Etapa_3.docx` | Se agregó el modelo de datos completo y la restricción de integridad en la base de datos. |
| VER-10 | `frontend/src/App.jsx` | La creación de tareas delega el error al formulario y el aviso general queda para las acciones del tablero. |

## Reverificación

### Verificación estática

| Verificación | Resultado |
|--------------|-----------|
| `ruff check backend` | Sin hallazgos. |
| `python -m compileall backend/app` | Compilación correcta. |
| `npm run lint` | Sin hallazgos. |
| `npm run build` | Compilación correcta. |

### Restricciones de integridad en la base de datos

Ejecutado sobre bases temporales (`docs/evidencias/etapa_4/sqlite_final.txt`).

| Verificación | Resultado |
|--------------|-----------|
| Inserción directa de título vacío | Rechazada por la restricción `CHECK`. |
| Inserción directa de título de 101 caracteres | Rechazada por la restricción `CHECK`. |
| Inserción directa de estado inválido | Rechazada por la restricción `CHECK`. |
| Inserción directa de descripción de 501 caracteres | Rechazada por la restricción `CHECK`. |
| Inserción directa de fecha con formato inválido | Rechazada por la restricción `CHECK`. |
| Adjunto de tamaño cero o mayor a 5 MB | Rechazado por la restricción `CHECK`. |
| Adjunto asociado a una tarea inexistente | Rechazado por la clave foránea. |
| Migración de una base con el esquema anterior | Los datos se conservaron, la tabla quedó con `CHECK` y con las columnas nuevas. |

### Verificación funcional de la API

Ejecutado contra el backend en funcionamiento (`docs/evidencias/etapa_4/api_final.txt`).

| Caso ejecutado | Resultado |
|----------------|-----------|
| `GET /api/health` | HTTP 200, `{"status": "ok"}`. |
| Crear tarea válida con espacios en los extremos | HTTP 201, título recortado, estado `Pendiente` y posición asignada. |
| Crear tarea con título de 100 caracteres | HTTP 201. |
| Crear tarea con título de 101 caracteres | HTTP 422. |
| Crear tarea con título de solo espacios | HTTP 422. |
| Crear tarea con fecha límite pasada | HTTP 422. |
| Editar una tarea con fecha límite pasada | HTTP 200, admitida la edición. |
| Listar tareas vencidas | La tarea con fecha pasada aparece con `overdue` en verdadero. |
| Agregar una subtarea | HTTP 201, contador de subtareas actualizado. |
| Mover a `Terminada` con una subtarea pendiente | HTTP 409 con el detalle de la cantidad pendiente. |
| Completar la subtarea y mover a `Terminada` | HTTP 200, estado `Terminada`. |
| Desmarcar una subtarea de una tarea finalizada | HTTP 200, la tarea vuelve a `En curso` (corrección de VER-02). |
| Mover con un estado inválido | HTTP 422. |
| Mover una tarea inexistente | HTTP 404. |
| Subir un adjunto con extensión no permitida | HTTP 415. |
| Subir un adjunto vacío | HTTP 422. |
| Subir un adjunto válido | HTTP 201 con el adjunto en la respuesta. |
| Subir un cuarto adjunto | HTTP 409 por el límite de 3 archivos. |
| Descargar un adjunto | HTTP 200 con el contenido del archivo. |
| Descargar un adjunto inexistente | HTTP 404. |
| Eliminar un adjunto | HTTP 204. |
| Eliminar una tarea | HTTP 204. |
| Restaurar la tarea eliminada | HTTP 200 con la tarea y sus adjuntos conservados. |
| Eliminar una tarea inexistente | HTTP 404. |
| Restaurar una tarea que no estaba eliminada | HTTP 404. |

### Verificación de la interfaz

Ejecutado sobre la aplicación servida por Vite con el proxy hacia la API (`docs/evidencias/etapa_4/frontend_final.txt`).

| Verificación | Resultado |
|--------------|-----------|
| Interfaz en `/` | HTTP 200 con el contenedor de la aplicación. |
| Proxy hacia `/api/health` | HTTP 200 con la respuesta de la API. |
| Proxy hacia la creación, el movimiento y la eliminación de tareas | Respuestas 201, 200 y 204. |
| Transformación de los módulos `main.jsx`, `App.jsx` y `TaskDetailModal.jsx` | HTTP 200 en los tres casos. |
| Hoja de estilos con las reglas del checklist | HTTP 200 y reglas presentes. |

Reverificación en el navegador de los hallazgos de interfaz:

| Verificación | Resultado |
|--------------|-----------|
| VER-05: etiqueta de una tarea finalizada con fecha límite futura | Muestra "Vence el ..." en lugar de "Venció el ...". |
| VER-04: Escape con el diálogo de confirmación abierto sobre el detalle | Se cierra solo el diálogo y el detalle permanece abierto. |

## Observaciones no correctivas

| ID | Observación | Tratamiento |
|----|-------------|-------------|
| OBS-01 | El movimiento de tarjetas depende del arrastre, sin alternativa por teclado. | No es un requisito de la actividad; se deja registrado como mejora futura. |
| OBS-02 | La carga de un adjunto lee el archivo completo en memoria antes de validar el tamaño. | Es aceptable con un límite de 5 MB; se registra como mejora si el límite creciera. |
| OBS-03 | Al eliminar una tarea, el archivo del adjunto permanece en el almacenamiento para poder deshacer la operación; no se elimina nunca de forma definitiva. | Es una consecuencia buscada del borrado lógico; se registra como política de conservación de archivos. |

## Conclusión de la etapa

La verificación permitió detectar diez hallazgos. Nueve fueron corregidos y uno fue aceptado y documentado por tratarse de una desviación de proceso. Las correcciones reforzaron la integridad de los datos en la base, la coherencia de las reglas de negocio entre capas, el comportamiento de la interfaz y la exactitud de la documentación. Después de las modificaciones, el análisis estático, la compilación, las pruebas contra la base y las verificaciones funcionales sobre la API y la interfaz volvieron a ejecutarse sin errores, por lo que la etapa se considera cerrada y el sistema queda preparado para el diseño de los casos de prueba.

## Evidencias

Las salidas de las herramientas se encuentran en `docs/evidencias/etapa_4/`:

- `ruff_inicial.txt` y `ruff_final.txt`.
- `compileall_inicial.txt` y `compileall_final.txt`.
- `eslint_inicial.txt` y `eslint_final.txt`.
- `vite_build_inicial.txt` y `vite_build_final.txt`.
- `sqlite_final.txt`.
- `api_final.txt`.
- `frontend_final.txt`.
