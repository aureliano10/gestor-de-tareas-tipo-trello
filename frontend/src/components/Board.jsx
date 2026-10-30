import Column from "./Column.jsx";

export const STATUSES = ["Pendiente", "En curso", "Terminada"];

export default function Board({ tasks, onMove, onDelete }) {
  return (
    <section className="board" aria-label="Tablero Kanban">
      {STATUSES.map((status) => (
        <Column
          key={status}
          status={status}
          tasks={tasks.filter((task) => task.status === status)}
          onMove={onMove}
          onDelete={onDelete}
        />
      ))}
    </section>
  );
}
