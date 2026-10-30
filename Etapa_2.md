# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 29/10/2026

# Etapa 2 - Diseño y planificación

## Objetivo de la etapa

Definir el alcance funcional del sistema, las tecnologías que se van a utilizar, la forma de organizar el trabajo entre los integrantes y la estrategia de verificación y validación que guiará el desarrollo de la Etapa 3 y las actividades posteriores.

## Funcionalidades que serán desarrolladas

| # | Funcionalidad | Requisitos | Descripción |
|---|---------------|-----------|-------------|
| 1 | Crear tarea | RF1, RF2 | Registrar una actividad con título obligatorio, descripción y fecha límite opcionales. Toda tarea nueva nace en estado `Pendiente`. |
| 2 | Mover y reordenar tarea | RF3, RF4 | Cambiar el estado de la tarea entre las columnas `Pendiente`, `En curso` y `Terminada` y reordenarla dentro de la columna. |
| 3 | Editar tarea | RF5 | Modificar el título, la descripción y la fecha límite de una tarea existente. |
| 4 | Checklist de subtareas | RF6, RF7, RF8 | Agregar subtareas, marcarlas como completadas, desmarcarlas y eliminarlas, mostrando el avance del checklist. |
| 5 | Control de finalización | RF9 | Impedir que una tarea pase a `Terminada` mientras tenga subtareas pendientes. |
| 6 | Fecha límite y vencimiento | RF10 | Asignar una fecha límite y señalar visualmente las tareas vencidas. |
| 7 | Archivos adjuntos | RF11, RF12, RF13 | Incorporar archivos a una tarea, descargarlos y eliminarlos. |
| 8 | Eliminar tarea con deshacer | RF14, RF15 | Quitar una actividad del tablero con confirmación previa y recuperarla durante unos segundos. |

Las funcionalidades 2, 5 y 6 se relacionan entre sí: el estado de la tarea, el bloqueo de la finalización y la fecha límite forman parte del seguimiento del avance de cada actividad.

## Alcance del sistema

El sistema es un tablero de tareas tipo Kanban con tres columnas fijas (`Pendiente`, `En curso` y `Terminada`). Cada tarea se representa con una tarjeta que puede arrastrarse entre columnas y abrirse para ver su detalle. En el detalle se editan los datos de la tarea, se gestiona su checklist de subtareas y se administran sus archivos adjuntos. Las funcionalidades de fecha límite, vencimiento, eliminación con confirmación y deshacer complementan el uso diario del tablero.

Quedan fuera del alcance de esta entrega la autenticación de usuarios, la colaboración en tiempo real y el historial de cambios, que se evalúan como posibles extensiones futuras.

## Requisitos funcionales

Los requisitos RF1 a RF15 fueron definidos en la Etapa 1. En esta etapa se agrupan por funcionalidad tal como muestra la tabla anterior, de modo que cada requisito queda asociado a una funcionalidad concreta y puede trazarse hasta los casos de prueba de la Etapa 5.

## Integrantes responsables de cada tarea

Para ser eficientes y aprovechar nuestros puntos fuertes, dividimos las tareas principales de desarrollo, aunque el diseño de casos de prueba lo haremos en conjunto:

- **Aureliano Eichhorn:** diseño de la base de datos (SQLite), desarrollo de la API REST (FastAPI) con las reglas de negocio, validaciones y manejo de errores, e implementación de los scripts de ejecución de pruebas sobre la API.
- **Nicolás Delfino:** desarrollo de la interfaz gráfica (React), conexión con la API mediante `fetch`, implementación de las interacciones del tablero (arrastre, edición, checklist, adjuntos y deshacer) y ejecución de las pruebas de interfaz.

Ambos integramos y revisamos el código del otro antes de darlo por terminado, y diseñamos y revisamos juntos los casos de prueba.

## Tecnologías y herramientas

- **Frontend:** React 19, JavaScript (sin TypeScript), CSS y Vite como empaquetador y servidor de desarrollo.
- **Backend:** Python 3.12, FastAPI y Pydantic para los modelos y las validaciones.
- **Base de datos:** SQLite, elegida por su simplicidad y rapidez para este alcance, con restricciones `CHECK` como última barrera de integridad.
- **Entorno de desarrollo:** Visual Studio Code.

## Estructura prevista del proyecto

```
backend/app/        API REST, validaciones y acceso a datos
backend/storage/    Archivos adjuntos almacenados en disco
frontend/src/       Interfaz del tablero y comunicación con la API
docs/               Documentación de cada etapa y evidencias
scripts/etapa_6/    Scripts de ejecución de los casos de prueba
```

## Repositorio utilizado

Utilizaremos Git para el control de versiones de forma local y GitHub como repositorio remoto, manejando ramas separadas para integrar el código de cada integrante (backend y frontend). La documentación de cada etapa se registra en un commit identificable, de modo que los avances queden trazados para las etapas de verificación y pruebas.

## Estrategia de pruebas

La estrategia será de abajo hacia arriba. Empezaremos probando los endpoints de la API para asegurar que la lógica de negocio y las inserciones en la base de datos funcionen correctamente de forma aislada. Una vez que la API sea estable, pasaremos a probar la interfaz, verificando que las validaciones visuales, las interacciones y la integración completa del sistema (cliente-servidor) respondan a los requisitos.

Como el alcance incluye funcionalidades con varias capas (checklist, adjuntos y deshacer), las pruebas se complementarán con un análisis estático del código y con una revisión del manejo de errores, para detectar fallas antes de la ejecución formal de los casos.

## Tipos de pruebas que serán aplicadas

- **Pruebas unitarias:** sobre las funciones del backend que validan y aplican reglas de negocio (por ejemplo, la validación del título o el bloqueo de la finalización con subtareas pendientes).
- **Pruebas de integración:** para asegurar que FastAPI interactúa correctamente con SQLite (guardar, actualizar, reordenar, eliminar y restaurar) y con el sistema de archivos (subida y descarga de adjuntos).
- **Pruebas de caja blanca:** análisis de los caminos lógicos de las funciones y los endpoints (por ejemplo, qué responde el código al intentar eliminar una tarea inexistente o al finalizar una tarea con subtareas pendientes).
- **Pruebas de caja negra:** sobre la API y sobre los componentes de React, aplicando partición de equivalencia y valores límite (por ejemplo, un título vacío, un título de 101 caracteres, un estado no permitido, un adjunto de extensión no admitida).
- **Pruebas de sistema:** recorrer el flujo completo en la interfaz visual como lo haría un usuario final, incluyendo el arrastre de tarjetas, el checklist, la descarga de adjuntos y el deshacer.

## Herramientas de testing y automatización

- **Ruff** y **compileall:** análisis estático y verificación de compilación del backend.
- **ESLint** y **Vite build:** análisis estático y verificación de compilación del frontend.
- **httpx:** cliente HTTP en Python para automatizar las pruebas contra la API REST.
- **Playwright:** automatización del navegador (Google Chrome) para las pruebas de interfaz.

## Verificación y Validación

- **Aspectos a verificar (durante el desarrollo):** revisaremos constantemente el código de ambos y chequearemos que se respeten los requisitos funcionales y las restricciones planteadas en la Etapa 1 (por ejemplo, que no se admitan tareas sin título en ninguna capa del sistema, que no se pueda finalizar una tarea con subtareas pendientes y que los adjuntos cumplan las restricciones de tamaño, cantidad y extensión).
- **Aspectos a validar (al finalizar el desarrollo):** evaluaremos el sistema de punta a punta simulando escenarios de uso real para comprobar si el producto terminado cumple con su objetivo inicial de ser una herramienta "ágil e intuitiva" para hacer el seguimiento visual de actividades.

## Conclusión de la etapa

Se definieron las ocho funcionalidades que dará el sistema, los responsables de cada parte, las tecnologías, la estrategia y los tipos de pruebas que se aplicarán. Con este marco quedan preparadas las condiciones para desarrollar el sistema en la Etapa 3 y verificar que cumpla con los requisitos acordados.

## Próxima etapa

La Etapa 3 consistirá en el desarrollo del sistema de acuerdo con lo planificado en esta etapa.
