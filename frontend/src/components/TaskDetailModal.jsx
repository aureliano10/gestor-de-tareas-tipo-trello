import { useRef, useState } from "react";
import { prioritySlug } from "../format.js";
import { useFocusTrap } from "../useFocusTrap.js";
import DetailAttachments from "./DetailAttachments.jsx";
import DetailChecklist from "./DetailChecklist.jsx";
import DetailHistory from "./DetailHistory.jsx";
import DetailLinks from "./DetailLinks.jsx";
import DueBadge from "./DueBadge.jsx";
import TaskFields, { validateTaskInput } from "./TaskFields.jsx";

const STATUSES = ["Pendiente", "En curso", "Terminada"];

function draftFrom(task) {
  return {
    title: task.title,
    description: task.description,
    dueDate: task.due_date ?? "",
    priority: task.priority,
    assignee: task.assignee,
  };
}

export default function TaskDetailModal({
  task,
  onClose,
  onNotify,
  onMove,
  onUpdate,
  onAddSubtask,
  onToggleSubtask,
  onDeleteSubtask,
  onUpload,
  onDeleteAttachment,
  onDelete,
}) {
  const dialogRef = useRef(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(() => draftFrom(task));
  const [formError, setFormError] = useState("");
  const [moveError, setMoveError] = useState("");
  const [saving, setSaving] = useState(false);
  const [moving, setMoving] = useState(false);

  // AUD-01: trampa de foco con restauración al cerrar.
  // AUD-10: Escape no descarta una edición en curso.
  useFocusTrap(dialogRef, {
    onEscape: () => {
      if (!editing) {
        onClose();
      }
    },
  });

  function startEditing() {
    setDraft(draftFrom(task));
    setFormError("");
    setEditing(true);
  }

  async function handleSave(event) {
    event.preventDefault();

    const message = validateTaskInput(draft);
    if (message) {
      setFormError(message);
      return;
    }

    setFormError("");
    setSaving(true);
    try {
      await onUpdate(task.id, draft);
      setEditing(false);
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  }

  // AUD-02 / AUD-29: alternativa de teclado y táctil al drag & drop.
  async function handleStatusChange(event) {
    const status = event.target.value;
    if (status === task.status) {
      return;
    }
    setMoving(true);
    setMoveError("");
    try {
      await onMove(task.id, status, 0);
    } catch (err) {
      setMoveError(err.message);
    } finally {
      setMoving(false);
    }
  }

  return (
    <div className="overlay" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-detail-title"
        data-testid="task-detail"
        ref={dialogRef}
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal__header">
          <div>
            <h2 id="task-detail-title" className="modal__title">
              {task.title}
            </h2>
            <p className="modal__meta">
              Tarea #{task.id}
              {task.overdue && <span className="modal__flag"> · vencida</span>}
            </p>
          </div>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Cerrar detalle"
            data-testid="detail-close"
          >
            ×
          </button>
        </header>

        <div className="modal__body">
          <section className="panel">
            <div className="panel__header">
              <h3>Detalle</h3>
              {!editing && (
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={startEditing}
                  data-testid="edit-start"
                >
                  Editar
                </button>
              )}
            </div>

            <div className="status-control">
              <label htmlFor="detail-status">Estado</label>
              <select
                id="detail-status"
                data-testid="detail-status"
                value={task.status}
                disabled={moving}
                onChange={handleStatusChange}
              >
                {STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            {moveError && (
              <p className="field-error" role="alert" data-testid="move-error">
                {moveError}
              </p>
            )}

            {editing ? (
              <form onSubmit={handleSave} noValidate>
                <TaskFields
                  idPrefix="edit-task"
                  values={draft}
                  onChange={setDraft}
                  disabled={saving}
                />
                <div className="panel__actions">
                  <button
                    type="submit"
                    className="btn"
                    disabled={saving}
                    data-testid="edit-save"
                  >
                    {saving ? "Guardando..." : "Guardar cambios"}
                  </button>
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={() => setEditing(false)}
                    disabled={saving}
                  >
                    Cancelar
                  </button>
                </div>
                {formError && (
                  <p className="field-error" role="alert" data-testid="edit-error">
                    {formError}
                  </p>
                )}
              </form>
            ) : (
              <div className="detail">
                <div className="detail__badges">
                  <span
                    className={`badge badge--priority badge--priority-${prioritySlug(
                      task.priority,
                    )}`}
                    data-testid="detail-priority"
                  >
                    Prioridad: {task.priority}
                  </span>
                  <DueBadge task={task} />
                </div>
                <p className="detail__assignee" data-testid="detail-assignee">
                  Responsable: {task.assignee || "sin asignar"}
                </p>
                <p className="detail__description">
                  {task.description || "Sin descripción."}
                </p>
              </div>
            )}
          </section>

          <DetailChecklist
            task={task}
            onAddSubtask={onAddSubtask}
            onToggleSubtask={onToggleSubtask}
            onDeleteSubtask={onDeleteSubtask}
            onNotify={onNotify}
          />

          <DetailLinks task={task} onUpdate={onUpdate} onNotify={onNotify} />

          <DetailAttachments
            task={task}
            onUpload={onUpload}
            onDeleteAttachment={onDeleteAttachment}
            onNotify={onNotify}
          />

          <DetailHistory task={task} />
        </div>

        <footer className="modal__footer">
          <button
            type="button"
            className="btn btn--danger"
            onClick={() => onDelete(task.id)}
            data-testid="detail-delete"
          >
            Eliminar tarea
          </button>
        </footer>
      </div>
    </div>
  );
}
