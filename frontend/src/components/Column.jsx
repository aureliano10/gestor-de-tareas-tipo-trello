import { useState } from "react";
import TaskCard from "./TaskCard.jsx";

export default function Column({ status, tasks, onMove, onDelete }) {
  const [dragOver, setDragOver] = useState(false);

  function handleDragOver(event) {
    event.preventDefault();
    setDragOver(true);
  }

  function handleDragLeave() {
    setDragOver(false);
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragOver(false);
    const taskId = Number(event.dataTransfer.getData("text/plain"));
    const alreadyInColumn = tasks.some((task) => task.id === taskId);
    if (Number.isInteger(taskId) && taskId > 0 && !alreadyInColumn) {
      onMove(taskId, status);
    }
  }

  return (
    <div
      className={`column${dragOver ? " column--drag-over" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      data-status={status}
    >
      <header className="column__header">
        <h2>{status}</h2>
        <span className="column__count" aria-label={`${tasks.length} tareas`}>
          {tasks.length}
        </span>
      </header>

      <div className="column__tasks">
        {tasks.length === 0 ? (
          <p className="column__empty">Sin tareas</p>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} onDelete={onDelete} />
          ))
        )}
      </div>
    </div>
  );
}
