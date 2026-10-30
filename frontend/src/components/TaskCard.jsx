import DueBadge from "./DueBadge.jsx";

export default function TaskCard({ task, onOpen, onDelete }) {
  function handleDragStart(event) {
    event.dataTransfer.setData("text/plain", String(task.id));
    event.dataTransfer.effectAllowed = "move";
    event.currentTarget.classList.add("task--dragging");
  }

  function handleDragEnd(event) {
    event.currentTarget.classList.remove("task--dragging");
  }

  const hasChecklist = task.subtask_total > 0;
  const hasTags = task.tags && task.tags.length > 0;

  return (
    <article
      className={`task${task.overdue ? " task--overdue" : ""}`}
      data-testid="task-card"
      data-task-id={task.id}
      draggable="true"
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onOpen(task.id)}
    >
      <p className="task__title" data-testid="task-title">
        {task.title}
      </p>

      {task.description && <p className="task__description">{task.description}</p>}

      <div className="task__badges">
        <span
          className={`badge badge--priority badge--priority-${task.priority.toLowerCase()}`}
          data-testid="priority-badge"
        >
          {task.priority}
        </span>
        <DueBadge task={task} />
        {hasChecklist && (
          <span
            className={`badge badge--checklist${
              task.subtask_done === task.subtask_total ? " badge--complete" : ""
            }`}
            data-testid="checklist-badge"
          >
            {task.subtask_done}/{task.subtask_total} subtareas
          </span>
        )}
        {task.attachments.length > 0 && (
          <span className="badge badge--files" data-testid="files-badge">
            {task.attachments.length}{" "}
            {task.attachments.length === 1 ? "archivo" : "archivos"}
          </span>
        )}
      </div>

      {(task.assignee || hasTags) && (
        <div className="task__meta">
          {task.assignee && (
            <span className="task__assignee" data-testid="task-assignee">
              {task.assignee}
            </span>
          )}
          {hasTags && (
            <div className="task__tags">
              {task.tags.map((tag) => (
                <span key={tag} className="tag-chip" data-testid="task-tag">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="task__footer">
        <span className="task__id">#{task.id}</span>
        <div className="task__actions">
          <button
            type="button"
            className="task__action"
            onClick={(event) => {
              event.stopPropagation();
              onOpen(task.id);
            }}
          >
            Abrir
          </button>
          <button
            type="button"
            className="task__action task__action--danger"
            data-testid="task-delete"
            onClick={(event) => {
              event.stopPropagation();
              onDelete(task.id);
            }}
          >
            Eliminar
          </button>
        </div>
      </div>
    </article>
  );
}
