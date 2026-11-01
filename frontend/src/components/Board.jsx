import { memo, useMemo } from "react";
import Column from "./Column.jsx";

export const STATUSES = ["Pendiente", "En curso", "Terminada"];

const EMPTY_HINTS = {
  Pendiente: "Sin tareas pendientes. Arrastrá una tarjeta acá.",
  "En curso": "Nada en curso. Arrastrá una tarjeta acá.",
  Terminada: "Todavía no hay tareas terminadas.",
};

function Board({ tasks, onMove, onOpen, onDelete }) {
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
    <section className="board" aria-label="Tablero Kanban" data-testid="board">
      {STATUSES.map((status) => (
        <Column
          key={status}
          status={status}
          emptyHint={EMPTY_HINTS[status]}
          tasks={grouped[status]}
          onMove={onMove}
          onOpen={onOpen}
          onDelete={onDelete}
        />
      ))}
    </section>
  );
}

export default memo(Board);
