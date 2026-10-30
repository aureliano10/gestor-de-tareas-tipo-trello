# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino

# Etapa 1 - Análisis del problema

## Problema o necesidad

Necesidad de organizar, gestionar y hacer seguimiento visual del estado de distintas tareas mediante un tablero ágil e intuitivo (estilo Kanban), donde además de mover una actividad entre estados se pueda detallar su contenido, controlar su avance y conservar la documentación asociada.

## Usuarios del sistema

Estudiantes, profesionales independientes y equipos pequeños que requieran organizar su flujo de trabajo diario.

## Objetivo

Desarrollar un pequeño sistema de software gestor de tareas que permita registrar y editar actividades, hacer seguimiento de su avance mediante un checklist, asociarles documentación y cambiar su estado a través de columnas.

## Funcionalidades principales

1. **Crear tarea:** permite registrar una nueva actividad con título obligatorio, descripción y fecha límite opcionales.
2. **Mover tarea:** permite actualizar el estado de la tarea desplazándola entre columnas (Pendiente, En curso, Terminada) y reordenarla dentro de la columna.
3. **Editar tarea:** permite modificar el título, la descripción y la fecha límite de una tarea existente.
4. **Checklist de subtareas:** permite agregar subtareas a una tarea, marcarlas como completadas, desmarcarlas y eliminarlas, mostrando el avance del checklist.
5. **Control de finalización:** impide que una tarea pase a Terminada mientras tenga subtareas pendientes.
6. **Fecha límite y vencimiento:** permite asignar una fecha límite y señala visualmente las tareas vencidas.
7. **Archivos adjuntos:** permite incorporar archivos a una tarea, descargarlos y eliminarlos.
8. **Eliminar tarea con deshacer:** permite quitar una actividad del tablero con confirmación previa y recuperarla durante unos segundos.
9. **Prioridad de la tarea:** permite clasificar cada tarea con una prioridad Baja, Media o Alta, con Media por defecto.
10. **Responsable:** permite indicar quién tiene a cargo la tarea mediante un texto libre de hasta 60 caracteres.
11. **Etiquetas:** permite asociar hasta 5 etiquetas por tarea, reutilizables entre tareas y sugeridas a partir de las existentes.
12. **Enlaces:** permite asociar hasta 5 enlaces por tarea, con una URL `http://` o `https://` y un nombre opcional.
13. **Historial de actividad:** registra automáticamente y con fecha cada acción realizada sobre la tarea.
14. **Búsqueda, filtros y orden:** permite buscar tareas por texto, filtrarlas por prioridad, etiqueta y vencimiento, y ordenar el listado.
15. **Alta enriquecida:** permite cargar en el alta subtareas, etiquetas, enlaces, prioridad y responsable.

## Datos de entrada

1. Para crear: título (obligatorio); descripción, fecha límite, prioridad, responsable, etiquetas, enlaces y subtareas (opcionales).
2. Para editar: identificador de la tarea y los nuevos valores de título, descripción, fecha límite, prioridad, responsable, etiquetas y enlaces.
3. Para mover: identificador de la tarea, estado destino y posición dentro de la columna.
4. Para el checklist: identificador de la tarea o de la subtarea, su título y su estado de completado.
5. Para adjuntar o descargar: identificador de la tarea y el archivo seleccionado.
6. Para eliminar o restaurar: identificador de la tarea.
7. Para clasificar: prioridad, responsable, etiquetas y enlaces de la tarea.
8. Para consultar: texto de búsqueda, filtros (prioridad, etiqueta y vencimiento) y criterio de orden del listado.

## Resultados esperados

El sistema debe reflejar visualmente la creación, la edición, el cambio de columna, el reordenamiento, el avance del checklist, la incorporación o eliminación de adjuntos y la eliminación o restauración de la tarjeta, asegurando que todos esos cambios queden guardados. Además, debe mostrar la prioridad, el responsable, las etiquetas y los enlaces de cada tarea, permitir buscar y filtrar el listado, y conservar un historial de las acciones realizadas sobre cada tarea.

## Restricciones o condiciones

- El título de la tarea es un campo obligatorio y no puede estar vacío ni contener solo espacios.
- El título no debe superar los 100 caracteres.
- La descripción no debe superar los 500 caracteres.
- Una tarea solo puede existir en un estado válido a la vez ("Pendiente", "En curso" o "Terminada").
- Una tarea no puede finalizarse mientras tenga subtareas pendientes.
- La fecha límite no puede ser anterior al día en que se crea la tarea; en una edición posterior sí se admite una fecha pasada.
- Una tarea admite hasta 3 archivos adjuntos, de 5 MB como máximo y con extensiones permitidas (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.docx`).
- La prioridad de una tarea debe ser uno de los valores "Baja", "Media" o "Alta"; si no se indica, se asume "Media".
- El responsable es opcional y no puede superar los 60 caracteres.
- Cada tarea admite hasta 5 etiquetas, de hasta 30 caracteres cada una, que se reutilizan entre tareas sin distinguir mayúsculas.
- Cada tarea admite hasta 5 enlaces; la URL debe comenzar con `http://` o `https://` y no superar los 500 caracteres, no puede repetirse dentro de la misma tarea y el nombre es opcional y de hasta 60 caracteres.
- El alta de una tarea admite hasta 20 subtareas cargadas junto con los demás datos.
- El historial de actividad se registra automáticamente y devuelve las últimas 20 acciones, de la más reciente a la más antigua.
- Las tareas se ordenan por estado y por su posición dentro de la columna, sin dejar huecos en la numeración; el listado puede reordenarse por prioridad, fecha límite o fecha de creación.

## Requisitos funcionales

**RF1:** El sistema debe permitir ingresar un título y registrar una tarea nueva, con descripción y fecha límite opcionales.
**RF2:** El sistema debe asignar por defecto el estado "Pendiente" a toda tarea recién creada.
**RF3:** El sistema debe permitir actualizar el estado de una tarea existente.
**RF4:** El sistema debe permitir reordenar las tareas dentro de una misma columna.
**RF5:** El sistema debe permitir editar el título, la descripción y la fecha límite de una tarea existente.
**RF6:** El sistema debe permitir registrar subtareas dentro de una tarea.
**RF7:** El sistema debe permitir marcar y desmarcar una subtarea como completada.
**RF8:** El sistema debe permitir eliminar una subtarea.
**RF9:** El sistema debe impedir que una tarea se finalice mientras tenga subtareas pendientes.
**RF10:** El sistema debe permitir asignar una fecha límite y señalar las tareas vencidas.
**RF11:** El sistema debe permitir adjuntar archivos a una tarea.
**RF12:** El sistema debe permitir descargar los archivos adjuntos de una tarea.
**RF13:** El sistema debe permitir eliminar un archivo adjunto de una tarea.
**RF14:** El sistema debe permitir eliminar un registro de tarea.
**RF15:** El sistema debe permitir recuperar una tarea eliminada.
**RF16:** El sistema debe permitir asignar a cada tarea una prioridad ("Baja", "Media" o "Alta"), por defecto "Media".
**RF17:** El sistema debe permitir registrar el responsable de una tarea como texto libre de hasta 60 caracteres, de forma opcional.
**RF18:** El sistema debe permitir asociar hasta 5 etiquetas por tarea, de hasta 30 caracteres cada una, reutilizables entre tareas y ofrecidas como sugerencias a partir de las existentes.
**RF19:** El sistema debe permitir asociar hasta 5 enlaces por tarea, con una URL `http://` o `https://` y un nombre opcional, sin admitir enlaces repetidos dentro de la misma tarea.
**RF20:** El sistema debe registrar automáticamente con fecha las acciones realizadas sobre cada tarea y devolver las últimas 20 en su historial de actividad.
**RF21:** El sistema debe permitir buscar tareas por texto en el título o la descripción y filtrarlas por prioridad, etiqueta y vencimiento.
**RF22:** El sistema debe permitir ordenar el listado de tareas por posición, prioridad, fecha límite o fecha de creación.
**RF23:** El sistema debe permitir cargar en el alta de una tarea sus subtareas, etiquetas, enlaces, prioridad y responsable.
