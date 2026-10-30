import Column from "./Column.jsx";

export const STATUSES = ["Pendiente", "En curso", "Terminada"];

const EMPTY_HINTS = {
  Pendiente: "Sin tareas pendientes. Arrastrá una tarjeta acá.",
  "En curso": "Nada en curso. Arrastrá una tarjeta acá.",
  Terminada: "Todavía no hay tareas terminadas.",
};

export default function Board({ tasks, onMove, onOpen, onDelete }) {
  return (
    <section className="board" aria-label="Tablero Kanban" data-testid="board">
      {STATUSES.map((status) => (
        <Column
          key={status}
          status={status}
          emptyHint={EMPTY_HINTS[status]}
          tasks={tasks.filter((task) => task.status === status)}
          onMove={onMove}
          onOpen={onOpen}
          onDelete={onDelete}
        />
      ))}
    </section>
  );
}
