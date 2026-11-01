import { useState } from "react";

const MAX_SUBTASK_LENGTH = 100;
// AUD-35: ventana de "deshacer" para los borrados secundarios.
const UNDO_WINDOW_MS = 7000;

/** Panel de checklist del detalle (alta, marcado y baja de subtareas). */
export default function DetailChecklist({
  task,
  onAddSubtask,
  onToggleSubtask,
  onDeleteSubtask,
  onNotify,
}) {
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const progress =
    task.subtask_total > 0
      ? Math.round((task.subtask_done / task.subtask_total) * 100)
      : 0;

  async function handleAdd(event) {
    event.preventDefault();
    const clean = title.trim();

    if (!clean) {
      setError("La subtarea necesita un título.");
      return;
    }
    if (clean.length > MAX_SUBTASK_LENGTH) {
      setError(
        `El título de la subtarea no puede superar los ${MAX_SUBTASK_LENGTH} caracteres.`,
      );
      return;
    }

    setError("");
    setBusy(true);
    try {
      await onAddSubtask(task.id, clean);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleToggle(subtask, done) {
    setError("");
    try {
      await onToggleSubtask(subtask.id, done);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(subtask) {
    setError("");
    setBusy(true);
    try {
      await onDeleteSubtask(subtask.id);
      onNotify?.(`Eliminaste la subtarea "${subtask.title}".`, {
        actionLabel: "Deshacer",
        duration: UNDO_WINDOW_MS,
        onAction: () => onAddSubtask(task.id, subtask.title),
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel__header">
        <h3>
          Checklist
          {task.subtask_total > 0 && (
            <span className="panel__counter">
              {task.subtask_done}/{task.subtask_total}
            </span>
          )}
        </h3>
      </div>

      {task.subtask_total > 0 && (
        <div className="progress" role="presentation">
          <div className="progress__bar" style={{ width: `${progress}%` }} />
        </div>
      )}

      {task.subtasks.length === 0 ? (
        <p className="muted">Todavía no hay subtareas.</p>
      ) : (
        <ul className="checklist">
          {task.subtasks.map((subtask) => (
            <li key={subtask.id} className="checklist__item">
              <label className="checklist__label">
                <input
                  type="checkbox"
                  checked={subtask.done}
                  onChange={(event) => handleToggle(subtask, event.target.checked)}
                />
                <span
                  className={
                    subtask.done
                      ? "checklist__text checklist__text--done"
                      : "checklist__text"
                  }
                >
                  {subtask.title}
                </span>
              </label>
              <button
                type="button"
                className="icon-button"
                onClick={() => handleDelete(subtask)}
                disabled={busy}
                aria-label={`Eliminar subtarea ${subtask.title}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      <form className="inline-form" onSubmit={handleAdd} noValidate>
        <input
          type="text"
          value={title}
          maxLength={MAX_SUBTASK_LENGTH}
          placeholder="Nueva subtarea"
          data-testid="subtask-input"
          aria-label="Nueva subtarea"
          onChange={(event) => {
            setTitle(event.target.value);
            setError("");
          }}
        />
        <button
          type="submit"
          className="btn"
          data-testid="subtask-add"
          disabled={busy}
        >
          {busy ? "Agregando..." : "Agregar"}
        </button>
      </form>

      {error && (
        <p className="field-error" role="alert" data-testid="subtask-error">
          {error}
        </p>
      )}
      <p className="hint">
        Una tarea con subtareas pendientes no se puede marcar como Terminada.
      </p>
    </section>
  );
}
