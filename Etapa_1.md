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

## Datos de entrada

1. Para crear: título (obligatorio), descripción y fecha límite (opcionales).
2. Para editar: identificador de la tarea y los nuevos valores de título, descripción y fecha límite.
3. Para mover: identificador de la tarea, estado destino y posición dentro de la columna.
4. Para el checklist: identificador de la tarea o de la subtarea, su título y su estado de completado.
5. Para adjuntar o descargar: identificador de la tarea y el archivo seleccionado.
6. Para eliminar o restaurar: identificador de la tarea.

## Resultados esperados

El sistema debe reflejar visualmente la creación, la edición, el cambio de columna, el reordenamiento, el avance del checklist, la incorporación o eliminación de adjuntos y la eliminación o restauración de la tarjeta, asegurando que todos esos cambios queden guardados.

## Restricciones o condiciones

- El título de la tarea es un campo obligatorio y no puede estar vacío ni contener solo espacios.
- El título no debe superar los 100 caracteres.
- La descripción no debe superar los 500 caracteres.
- Una tarea solo puede existir en un estado válido a la vez ("Pendiente", "En curso" o "Terminada").
- Una tarea no puede finalizarse mientras tenga subtareas pendientes.
- La fecha límite no puede ser anterior al día en que se crea la tarea; en una edición posterior sí se admite una fecha pasada.
- Una tarea admite hasta 3 archivos adjuntos, de 5 MB como máximo y con extensiones permitidas (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.docx`).
- Las tareas se ordenan por estado y por su posición dentro de la columna, sin dejar huecos en la numeración.

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
