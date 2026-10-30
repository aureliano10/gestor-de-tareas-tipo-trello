export default function TaskCard({ task, onDelete }) {
  function handleDragStart(event) {
    event.dataTransfer.setData("text/plain", String(task.id));
    event.dataTransfer.effectAllowed = "move";
  }

  return (
    <article className="task" draggable="true" onDragStart={handleDragStart}>
      <p className="task__title">{task.title}</p>
      <div className="task__footer">
        <span className="task__id">#{task.id}</span>
        <button
          type="button"
          className="task__delete"
          onClick={() => onDelete(task.id)}
          aria-label={`Eliminar tarea ${task.title}`}
        >
          Eliminar
        </button>
      </div>
    </article>
  );
}
