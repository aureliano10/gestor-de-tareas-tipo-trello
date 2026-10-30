# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 29/10/2026

# Etapa 4 - Verificación del software

## Objetivo de la etapa

Realizar actividades de verificación sobre los requisitos, el diseño, el código y la documentación del sistema, registrar los problemas encontrados y aplicar las correcciones correspondientes, comprobando luego que las correcciones hayan quedado resueltas.

## Alcance

Esta etapa es de **verificación estática**: se revisa que el producto se esté construyendo correctamente. No se ejecutan todavía los casos de prueba formales ni se realiza la validación con usuarios, actividades que corresponden a las etapas 5 a 10.

Se revisaron:

- Los requisitos funcionales y las restricciones definidos en la Etapa 1.
- La coherencia entre el diseño planificado en la Etapa 2 y la implementación real.
- El código del backend y del frontend.
- La documentación del repositorio.
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

| Requisito o restricción | Implementación verificada | Resultado |
|-------------------------|---------------------------|-----------|
| RF1: registrar una tarea nueva | Endpoint `POST /api/tasks`, repositorio y formulario `TaskForm`. | Cumple |
| RF2: estado inicial `Pendiente` | Valor por defecto en `repository.create_task` y en la tabla `tasks`. | Cumple |
| RF3: actualizar el estado de una tarea | Endpoint `PATCH /api/tasks/{id}/status` y arrastre entre columnas. | Cumple |
| RF4: eliminar una tarea | Endpoint `DELETE /api/tasks/{id}` y botón en cada tarjeta. | Cumple |
| Título obligatorio y no vacío | Validación Pydantic, validación en el formulario y `CHECK` en SQLite. | Cumple |
| Título de hasta 100 caracteres | Validación Pydantic, `maxLength` en el formulario y `CHECK` en SQLite. | Cumple |
| Estados válidos únicamente | Tipo `Literal`, validación de la API y `CHECK` en SQLite. | Cumple |
| Persistencia de los cambios | Tabla `tasks` en SQLite y operaciones del repositorio. | Cumple |

No se detectaron requisitos sin implementación ni funcionalidades implementadas que no estuvieran previstas.

## 2. Revisión del diseño

| Aspecto planificado en Etapa 2 | Verificación realizada | Resultado |
|--------------------------------|-------------------------|-----------|
| Frontend con React, JavaScript y CSS | Proyecto Vite con React y hoja de estilos propia. | Cumple |
| Backend con Python y FastAPI | Aplicación FastAPI con routers y modelos Pydantic. | Cumple |
| Base de datos SQLite | Tabla `tasks` creada y utilizada por el repositorio. | Cumple |
| Separación de responsabilidades | Capas de rutas, esquemas, repositorio y base de datos. | Cumple |
| Control de versiones con Git | Repositorio con commits por etapa. | Cumple parcialmente |
| Ramas separadas para frontend y backend | El trabajo se realizó sobre la rama `main`. | No cumple |

La desviación sobre las ramas se registra como el hallazgo VER-08 y se documenta su tratamiento.

## 3. Revisión de código

### Backend

Se revisó:

- Que las consultas SQL usen parámetros y no concatenación de cadenas.
- Que las conexiones se cierren correctamente y se confirme o revierta la transacción.
- Que las validaciones del título y del estado se apliquen antes de llegar a la base de datos.
- Que las operaciones sobre tareas inexistentes respondan con HTTP 404.
- Que los datos inválidos respondan con HTTP 422.
- Que la configuración de CORS permita el origen del frontend.

Resultado: sin problemas de seguridad en las consultas; se detectó que la base de datos no aplicaba restricciones de integridad propias (VER-01).

### Frontend

Se revisó:

- Que el formulario valide antes de enviar y muestre errores claros.
- Que el estado de carga y los errores se manejen en la interfaz.
- Que las operaciones exitosas actualicen el estado local sin recargar la página.
- Que la comunicación con la API sea coherente con los códigos HTTP del backend.
- Que el arrastre entre columnas no genere operaciones innecesarias.

Resultado: se detectaron mensajes de error duplicados (VER-02), una petición innecesaria al soltar en la misma columna (VER-03), un error que permanecía visible al editar (VER-04) y un prefijo técnico en los mensajes de validación (VER-05).

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

El análisis estático no detectó errores de sintaxis ni problemas de estilo. Los hallazgos de esta etapa provinieron de la inspección manual y de la revisión de consistencia.

## 5. Revisión de documentación

Se comparó el `README.md` y el documento de la Etapa 3 con el comportamiento real del sistema.

| Aspecto revisado | Resultado |
|------------------|-----------|
| Comandos de instalación y ejecución | Correctos. |
| Endpoints documentados | Coinciden con la API implementada. |
| Reglas de negocio | Coinciden con las validaciones del sistema. |
| Versión de Node.js requerida | Inexacta (VER-06). |
| Instrucciones de análisis estático | Ausentes (VER-07). |
| Restricciones de integridad en la base | No estaban reflejadas en la Etapa 3 (VER-09). |

## Registro de hallazgos

| ID | Aspecto | Descripción | Severidad | Acción realizada | Estado |
|----|---------|-------------|-----------|------------------|--------|
| VER-01 | Código / Base de datos | La tabla `tasks` no aplicaba restricciones de integridad para título ni estado; solo la API los validaba. | Media | Se agregaron restricciones `CHECK` y una migración automática para bases existentes. | Corregido |
| VER-02 | Código / Interfaz | Al fallar la creación de una tarea, el error se mostraba dos veces: en la alerta general y en el formulario. | Baja | La creación ahora deja el manejo del error únicamente al formulario. | Corregido |
| VER-03 | Código / Interfaz | Soltar una tarjeta en su misma columna generaba una petición `PATCH` innecesaria. | Baja | Se verifica que la tarea no pertenezca ya a la columna destino antes de moverla. | Corregido |
| VER-04 | Código / Interfaz | El mensaje de error del formulario seguía visible mientras el usuario corregía el título. | Baja | El error se limpia al modificar el campo. | Corregido |
| VER-05 | Código / Interfaz | Los mensajes de validación del backend se mostraban con el prefijo técnico "Value error,". | Baja | Se elimina el prefijo antes de mostrar el mensaje. | Corregido |
| VER-06 | Documentación | El README indicaba "Node.js 20 o superior", pero Vite 8 requiere Node.js 20.19 o superior (o 22.12 o superior). | Media | Se corrigió la versión requerida. | Corregido |
| VER-07 | Documentación | El README no documentaba cómo ejecutar el análisis estático ni la dependencia de desarrollo. | Baja | Se agregó la sección de análisis estático y `requirements-dev.txt`. | Corregido |
| VER-08 | Diseño / Git | La Etapa 2 preveía ramas separadas para frontend y backend, pero el trabajo se realizó sobre `main`. | Media | Se documenta la desviación y se mantiene una convención de commits por etapa sobre `main`. | Aceptado |
| VER-09 | Documentación | La Etapa 3 no reflejaba que la base de datos también aplica restricciones de integridad. | Baja | Se actualizó la tabla de validaciones de la Etapa 3. | Corregido |

## Correcciones aplicadas

| ID | Archivos modificados | Detalle de la corrección |
|----|----------------------|--------------------------|
| VER-01 | `backend/app/database.py` | Se agregaron `CHECK` para título no vacío, longitud máxima y estados válidos. Se incorporó una migración que reconstruye la tabla si existe un esquema anterior. |
| VER-02 | `frontend/src/App.jsx` | `handleCreate` ya no registra el error general; el error lo muestra `TaskForm`. |
| VER-03 | `frontend/src/components/Column.jsx` | Se omite el movimiento si la tarea ya está en la columna destino. |
| VER-04 | `frontend/src/components/TaskForm.jsx` | El error se limpia al escribir en el campo de título. |
| VER-05 | `frontend/src/api.js` | Se elimina el prefijo "Value error," de los mensajes de validación. |
| VER-06 | `README.md` | Se precisó la versión de Node.js compatible con Vite 8. |
| VER-07 | `README.md`, `backend/requirements-dev.txt` | Se documentó el análisis estático y se agregó la dependencia de Ruff. |
| VER-09 | `docs/Etapa_3.md`, `docs/Etapa_3.docx` | Se agregó la restricción de integridad en la base de datos. |

## Reverificación

| Verificación | Resultado |
|--------------|-----------|
| `ruff check backend` | Sin hallazgos. |
| `python -m compileall backend/app` | Compilación correcta. |
| `npm run lint` | Sin hallazgos. |
| `npm run build` | Compilación correcta. |
| Migración de una base con esquema anterior | Los datos se conservaron y la tabla quedó con `CHECK`. |
| Inserción directa de título vacío en SQLite | Rechazada por la restricción `CHECK`. |
| Inserción directa de estado inválido en SQLite | Rechazada por la restricción `CHECK`. |
| Prueba funcional de la API | Todos los endpoints respondieron según lo esperado. |
| Interfaz con backend mediante proxy de Vite | HTTP 200 y respuesta correcta de la API. |

Resultados funcionales obtenidos luego de las correcciones:

| Caso ejecutado | Resultado |
|----------------|-----------|
| `GET /api/health` | HTTP 200, `{"status": "ok"}`. |
| Crear tarea válida con espacios en los extremos | HTTP 201, título recortado y estado `Pendiente`. |
| Crear tarea con título de 100 caracteres | HTTP 201. |
| Crear tarea con título de 101 caracteres | HTTP 422. |
| Crear tarea con título de solo espacios | HTTP 422. |
| Actualizar a `En curso` | HTTP 200, estado actualizado. |
| Actualizar con estado inválido | HTTP 422. |
| Actualizar una tarea inexistente | HTTP 404. |
| Eliminar una tarea existente | HTTP 204. |
| Eliminar una tarea inexistente | HTTP 404. |

## Observaciones no correctivas

| ID | Observación | Tratamiento |
|----|-------------|-------------|
| OBS-01 | El movimiento de tarjetas depende del arrastre, sin alternativa por teclado. | No es un requisito de la actividad; se deja registrado como mejora futura. |
| OBS-02 | La eliminación de una tarea no solicita confirmación. | No es un requisito de la actividad; se evalúa como mejora de usabilidad. |
| OBS-03 | El error de validación del backend podría incluir mensajes más específicos por campo si el sistema creciera. | Se mantiene el mensaje actual por ser suficiente para el alcance. |

## Conclusión de la etapa

La verificación permitió detectar nueve hallazgos. Ocho fueron corregidos y uno fue aceptado y documentado por tratarse de una desviación de proceso. Las correcciones reforzaron la integridad de los datos en la base, la coherencia de la interfaz y la exactitud de la documentación. Después de las modificaciones, el análisis estático, la compilación y las verificaciones funcionales volvieron a ejecutarse sin errores, por lo que la etapa se considera cerrada y el sistema queda preparado para el diseño de casos de prueba.

## Evidencias

Las salidas de las herramientas se encuentran en `docs/evidencias/etapa_4/`:

- `ruff_inicial.txt` y `ruff_final.txt`.
- `compileall_inicial.txt` y `compileall_final.txt`.
- `eslint_inicial.txt` y `eslint_final.txt`.
- `vite_build_inicial.txt` y `vite_build_final.txt`.
- `api_final.txt`.
- `frontend_final.txt`.
