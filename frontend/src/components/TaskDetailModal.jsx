import { useEffect, useState } from "react";
import { attachmentUrl } from "../api.js";
import {
  ALLOWED_EXTENSIONS,
  MAX_ATTACHMENTS,
  MAX_ATTACHMENT_BYTES,
  extensionOf,
  formatSize,
} from "../format.js";
import DueBadge from "./DueBadge.jsx";
import TaskFields, { validateTaskInput } from "./TaskFields.jsx";

function draftFrom(task) {
  return {
    title: task.title,
    description: task.description,
    dueDate: task.due_date ?? "",
  };
}

export default function TaskDetailModal({
  task,
  onClose,
  onUpdate,
  onAddSubtask,
  onToggleSubtask,
  onDeleteSubtask,
  onUpload,
  onDeleteAttachment,
  onDelete,
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(() => draftFrom(task));
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const [subtaskTitle, setSubtaskTitle] = useState("");
  const [subtaskError, setSubtaskError] = useState("");

  const [attachError, setAttachError] = useState("");

  useEffect(() => {
    function handleKey(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

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

  async function handleAddSubtask(event) {
    event.preventDefault();
    const clean = subtaskTitle.trim();

    if (!clean) {
      setSubtaskError("La subtarea necesita un título.");
      return;
    }
    if (clean.length > 100) {
      setSubtaskError("El título de la subtarea no puede superar los 100 caracteres.");
      return;
    }

    setSubtaskError("");
    try {
      await onAddSubtask(task.id, clean);
      setSubtaskTitle("");
    } catch (err) {
      setSubtaskError(err.message);
    }
  }

  async function handleToggleSubtask(subtaskId, done) {
    setSubtaskError("");
    try {
      await onToggleSubtask(subtaskId, done);
    } catch (err) {
      setSubtaskError(err.message);
    }
  }

  async function handleDeleteSubtask(subtaskId) {
    setSubtaskError("");
    try {
      await onDeleteSubtask(subtaskId);
    } catch (err) {
      setSubtaskError(err.message);
    }
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    const extension = extensionOf(file.name);
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setAttachError(`Formato no permitido. Se aceptan: ${ALLOWED_EXTENSIONS.join(", ")}.`);
      return;
    }
    if (file.size === 0) {
      setAttachError("El archivo está vacío.");
      return;
    }
    if (file.size > MAX_ATTACHMENT_BYTES) {
      setAttachError("El archivo supera el tamaño máximo de 5 MB.");
      return;
    }

    setAttachError("");
    try {
      await onUpload(task.id, file);
    } catch (err) {
      setAttachError(err.message);
    }
  }

  async function handleDeleteAttachment(attachmentId) {
    setAttachError("");
    try {
      await onDeleteAttachment(task.id, attachmentId);
    } catch (err) {
      setAttachError(err.message);
    }
  }

  const progress =
    task.subtask_total > 0
      ? Math.round((task.subtask_done / task.subtask_total) * 100)
      : 0;
  const uploadDisabled = task.attachments.length >= MAX_ATTACHMENTS;

  return (
    <div className="overlay" onClick={onClose} role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-detail-title"
        data-testid="task-detail"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal__header">
          <div>
            <h2 id="task-detail-title" className="modal__title">
              {task.title}
            </h2>
            <p className="modal__meta">
              Tarea #{task.id} · {task.status}
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
                <DueBadge task={task} />
                <p className="detail__description">
                  {task.description || "Sin descripción."}
                </p>
              </div>
            )}
          </section>

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
                        onChange={(event) =>
                          handleToggleSubtask(subtask.id, event.target.checked)
                        }
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
                      onClick={() => handleDeleteSubtask(subtask.id)}
                      aria-label={`Eliminar subtarea ${subtask.title}`}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <form className="inline-form" onSubmit={handleAddSubtask} noValidate>
              <input
                type="text"
                value={subtaskTitle}
                maxLength={100}
                placeholder="Nueva subtarea"
                data-testid="subtask-input"
                onChange={(event) => {
                  setSubtaskTitle(event.target.value);
                  setSubtaskError("");
                }}
              />
              <button type="submit" className="btn" data-testid="subtask-add">
                Agregar
              </button>
            </form>

            {subtaskError && (
              <p className="field-error" role="alert" data-testid="subtask-error">
                {subtaskError}
              </p>
            )}
            <p className="hint">
              Una tarea con subtareas pendientes no se puede marcar como Terminada.
            </p>
          </section>

          <section className="panel">
            <div className="panel__header">
              <h3>
                Archivos adjuntos
                <span className="panel__counter">
                  {task.attachments.length}/{MAX_ATTACHMENTS}
                </span>
              </h3>
            </div>

            {task.attachments.length === 0 ? (
              <p className="muted">Sin archivos adjuntos.</p>
            ) : (
              <ul className="attachments">
                {task.attachments.map((attachment) => (
                  <li key={attachment.id} className="attachments__item">
                    <a
                      className="attachments__name"
                      href={attachmentUrl(task.id, attachment.id)}
                      download={attachment.filename}
                    >
                      {attachment.filename}
                    </a>
                    <span className="attachments__meta">
                      {formatSize(attachment.size_bytes)}
                    </span>
                    <button
                      type="button"
                      className="icon-button"
                      onClick={() => handleDeleteAttachment(attachment.id)}
                      aria-label={`Quitar ${attachment.filename}`}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <label className={`upload${uploadDisabled ? " upload--disabled" : ""}`}>
              <input
                type="file"
                accept={ALLOWED_EXTENSIONS.join(",")}
                disabled={uploadDisabled}
                data-testid="attachment-input"
                onChange={handleFileChange}
              />
              <span>
                {uploadDisabled
                  ? "Límite de archivos alcanzado"
                  : "Adjuntar archivo"}
              </span>
            </label>

            {attachError && (
              <p className="field-error" role="alert" data-testid="attachment-error">
                {attachError}
              </p>
            )}
            <p className="hint">
              Hasta {MAX_ATTACHMENTS} archivos de 5 MB. Formatos:{" "}
              {ALLOWED_EXTENSIONS.join(", ")}.
            </p>
          </section>
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
