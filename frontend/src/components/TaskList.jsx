import { memo, useMemo } from "react";
import { prioritySlug } from "../format.js";
import { STATUSES } from "./Board.jsx";
import DueBadge from "./DueBadge.jsx";

/**
 * Vista alternativa "Lista": misma información que el tablero, en filas densas
 * agrupadas por estado. Permite ver muchas tareas de un vistazo sin reemplazar
 * el tablero Kanban (que sigue siendo la vista principal).
 */
function TaskList({ tasks, onOpen, onDelete }) {
  const grouped = useMemo(() => {
    const result = {};
    for (const status of STATUSES) {
      result[status] = [];
    }
    for (const task of tasks) {
      (result[task.status] ??= []).push(task);
    }
    return result;
  }, [tasks]);

  return (
    <section className="task-list" aria-label="Lista de tareas" data-testid="task-list">
      {STATUSES.map((status) => {
        const group = grouped[status];
        return (
          <div
            className="task-list__group"
            key={status}
            data-status={status}
            data-testid="task-list-group"
          >
            <header className="task-list__group-header">
              <span className="task-list__group-dot" aria-hidden="true" />
              <h2>{status}</h2>
              <span className="column__count" aria-label={`${group.length} tareas`}>
                {group.length}
              </span>
            </header>

            {group.length === 0 ? (
              <p className="task-list__empty">Sin tareas en esta columna.</p>
            ) : (
              <div className="task-list__table-wrap">
                <table className="task-list__table">
                  <thead>
                    <tr>
                      <th scope="col">Tarea</th>
                      <th scope="col">Prioridad</th>
                      <th scope="col">Vencimiento</th>
                      <th scope="col">Responsable</th>
                      <th scope="col">Etiquetas</th>
                      <th scope="col">Subtareas</th>
                      <th scope="col">Archivos</th>
                      <th scope="col">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.map((task) => (
                      <tr
                        key={task.id}
                        className={task.overdue ? "is-overdue" : ""}
                        data-task-id={task.id}
                      >
                        <td className="task-list__title">
                          <button
                            type="button"
                            className="task-list__open"
                            onClick={() => onOpen(task.id)}
                          >
                            <span className="task-list__id">#{task.id}</span> {task.title}
                          </button>
                        </td>
                        <td>
                          <span
                            className={`badge badge--priority badge--priority-${prioritySlug(
                              task.priority,
                            )}`}
                          >
                            {task.priority}
                          </span>
                        </td>
                        <td>
                          <DueBadge task={task} />
                        </td>
                        <td>{task.assignee || "—"}</td>
                        <td>
                          {task.tags && task.tags.length > 0
                            ? task.tags.map((tag) => (
                                <span key={tag} className="tag-chip">
                                  {tag}
                                </span>
                              ))
                            : "—"}
                        </td>
                        <td>
                          {task.subtask_total > 0
                            ? `${task.subtask_done}/${task.subtask_total}`
                            : "—"}
                        </td>
                        <td>{task.attachments.length > 0 ? task.attachments.length : "—"}</td>
                        <td className="task-list__actions">
                          <button type="button" onClick={() => onOpen(task.id)}>
                            Abrir
                          </button>
                          <button
                            type="button"
                            className="danger"
                            onClick={() => onDelete(task.id)}
                          >
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

export default memo(TaskList);
