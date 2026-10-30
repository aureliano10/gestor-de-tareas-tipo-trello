import { useRef, useState } from "react";
import TaskCard from "./TaskCard.jsx";

/**
 * Calcula la posición de inserción a partir de la altura del puntero.
 * Se excluye la tarjeta arrastrada para que el índice coincida con la lista
 * destino que arma el backend (que tampoco la incluye).
 */
function dropIndex(container, taskId, clientY) {
  const cards = [...container.querySelectorAll("[data-task-id]")].filter(
    (card) => Number(card.dataset.taskId) !== taskId,
  );

  let index = 0;
  for (const card of cards) {
    const rect = card.getBoundingClientRect();
    if (clientY > rect.top + rect.height / 2) {
      index += 1;
    }
  }
  return index;
}

export default function Column({
  status,
  tasks,
  emptyHint,
  onMove,
  onOpen,
  onDelete,
}) {
  const [dragOver, setDragOver] = useState(false);
  const dragDepth = useRef(0);

  function handleDragEnter(event) {
    event.preventDefault();
    dragDepth.current += 1;
    setDragOver(true);
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }

  function handleDragLeave() {
    dragDepth.current -= 1;
    if (dragDepth.current <= 0) {
      dragDepth.current = 0;
      setDragOver(false);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    dragDepth.current = 0;
    setDragOver(false);

    const taskId = Number(event.dataTransfer.getData("text/plain"));
    if (!Number.isInteger(taskId) || taskId <= 0) {
      return;
    }
    onMove(taskId, status, dropIndex(event.currentTarget, taskId, event.clientY));
  }

  return (
    <div
      className={`column${dragOver ? " column--drag-over" : ""}`}
      data-testid="column"
      data-status={status}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <header className="column__header">
        <h2>{status}</h2>
        <span className="column__count" aria-label={`${tasks.length} tareas`}>
          {tasks.length}
        </span>
      </header>

      <div className="column__tasks">
        {tasks.length === 0 ? (
          <p className="column__empty">{emptyHint}</p>
        ) : (
          tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onOpen={onOpen}
              onDelete={onDelete}
            />
          ))
        )}
      </div>
    </div>
  );
}
