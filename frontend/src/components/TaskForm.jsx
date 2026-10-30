import { useEffect, useRef, useState } from "react";
import { getTags } from "../api.js";
import {
  ALLOWED_EXTENSIONS,
  MAX_ATTACHMENTS,
  MAX_ATTACHMENT_BYTES,
  extensionOf,
  formatSize,
  todayISO,
} from "../format.js";
import TaskFields, {
  DEFAULT_PRIORITY,
  MAX_ASSIGNEE_LENGTH,
  validateTaskInput,
} from "./TaskFields.jsx";

const MAX_TAGS = 5;
const MAX_TAG_LENGTH = 30;
const MAX_SUBTASKS = 20;
const MAX_SUBTASK_LENGTH = 100;
const MAX_LINKS = 5;
const MAX_LINK_URL_LENGTH = 500;
const MAX_LINK_LABEL_LENGTH = 60;

const EMPTY_TASK = {
  title: "",
  description: "",
  dueDate: "",
  priority: DEFAULT_PRIORITY,
  assignee: "",
};

function isValidLink(url) {
  return /^https?:\/\//i.test(url);
}

function validateExtras({ assignee, tags, subtasks, links, files }) {
  if ((assignee ?? "").trim().length > MAX_ASSIGNEE_LENGTH) {
    return `El responsable no puede superar los ${MAX_ASSIGNEE_LENGTH} caracteres.`;
  }
  if (tags.length > MAX_TAGS) {
    return `Una tarea no puede tener más de ${MAX_TAGS} etiquetas.`;
  }
  if (subtasks.length > MAX_SUBTASKS) {
    return `Una tarea no puede tener más de ${MAX_SUBTASKS} subtareas.`;
  }
  if (links.length > MAX_LINKS) {
    return `Una tarea no puede tener más de ${MAX_LINKS} enlaces.`;
  }
  if (files.length > MAX_ATTACHMENTS) {
    return `Hasta ${MAX_ATTACHMENTS} archivos adjuntos.`;
  }
  return "";
}

export default function TaskForm({ onCreate, onUpload }) {
  const [values, setValues] = useState(EMPTY_TASK);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [suggestions, setSuggestions] = useState([]);
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState("");
  const [tagError, setTagError] = useState("");

  const [subtasks, setSubtasks] = useState([]);
  const [subtaskInput, setSubtaskInput] = useState("");
  const [subtaskError, setSubtaskError] = useState("");

  const [links, setLinks] = useState([]);
  const [linkUrl, setLinkUrl] = useState("");
  const [linkLabel, setLinkLabel] = useState("");
  const [linkError, setLinkError] = useState("");

  const [files, setFiles] = useState([]);
  const [fileError, setFileError] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    let active = true;
    getTags()
      .then((names) => {
        if (active) {
          setSuggestions(names);
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  function resetForm() {
    setValues(EMPTY_TASK);
    setTags([]);
    setTagInput("");
    setTagError("");
    setSubtasks([]);
    setSubtaskInput("");
    setSubtaskError("");
    setLinks([]);
    setLinkUrl("");
    setLinkLabel("");
    setLinkError("");
    setFiles([]);
    setFileError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function commitTag(raw) {
    const clean = raw.trim();
    setTagInput("");
    if (!clean) {
      return;
    }
    if (clean.length > MAX_TAG_LENGTH) {
      setTagError(`La etiqueta no puede superar los ${MAX_TAG_LENGTH} caracteres.`);
      return;
    }
    if (tags.some((tag) => tag.toLowerCase() === clean.toLowerCase())) {
      setTagError("");
      return;
    }
    if (tags.length >= MAX_TAGS) {
      setTagError(`Una tarea no puede tener más de ${MAX_TAGS} etiquetas.`);
      return;
    }
    setTagError("");
    setTags([...tags, clean]);
  }

  function handleTagKeyDown(event) {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      commitTag(tagInput);
    } else if (event.key === "Backspace" && !tagInput && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  }

  function removeTag(tag) {
    setTags(tags.filter((item) => item !== tag));
    setTagError("");
  }

  function addSubtaskItem() {
    const clean = subtaskInput.trim();
    if (!clean) {
      setSubtaskError("La subtarea necesita un título.");
      return;
    }
    if (clean.length > MAX_SUBTASK_LENGTH) {
      setSubtaskError(
        `El título de la subtarea no puede superar los ${MAX_SUBTASK_LENGTH} caracteres.`,
      );
      return;
    }
    if (subtasks.length >= MAX_SUBTASKS) {
      setSubtaskError(`Una tarea no puede tener más de ${MAX_SUBTASKS} subtareas.`);
      return;
    }
    setSubtaskError("");
    setSubtasks([...subtasks, clean]);
    setSubtaskInput("");
  }

  function removeSubtaskItem(index) {
    setSubtasks(subtasks.filter((_, position) => position !== index));
  }

  function addLink() {
    const url = linkUrl.trim();
    const label = linkLabel.trim();
    if (!url) {
      setLinkError("Ingresá una URL para el enlace.");
      return;
    }
    if (!isValidLink(url)) {
      setLinkError("El enlace debe comenzar con http:// o https://.");
      return;
    }
    if (url.length > MAX_LINK_URL_LENGTH) {
      setLinkError(`El enlace no puede superar los ${MAX_LINK_URL_LENGTH} caracteres.`);
      return;
    }
    if (label.length > MAX_LINK_LABEL_LENGTH) {
      setLinkError(
        `El nombre del enlace no puede superar los ${MAX_LINK_LABEL_LENGTH} caracteres.`,
      );
      return;
    }
    if (links.some((link) => link.url.toLowerCase() === url.toLowerCase())) {
      setLinkError("El enlace ya está agregado a la tarea.");
      return;
    }
    if (links.length >= MAX_LINKS) {
      setLinkError(`Una tarea no puede tener más de ${MAX_LINKS} enlaces.`);
      return;
    }
    setLinkError("");
    setLinks([...links, { url, label }]);
    setLinkUrl("");
    setLinkLabel("");
  }

  function removeLink(index) {
    setLinks(links.filter((_, position) => position !== index));
    setLinkError("");
  }

  function handleFileChange(event) {
    const selected = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (selected.length === 0) {
      return;
    }

    const next = [...files];
    let message = "";
    for (const file of selected) {
      if (next.length >= MAX_ATTACHMENTS) {
        message = `Hasta ${MAX_ATTACHMENTS} archivos adjuntos.`;
        break;
      }
      if (!ALLOWED_EXTENSIONS.includes(extensionOf(file.name))) {
        message = `Formato no permitido (${file.name}). Se aceptan: ${ALLOWED_EXTENSIONS.join(", ")}.`;
        continue;
      }
      if (file.size === 0) {
        message = `El archivo ${file.name} está vacío.`;
        continue;
      }
      if (file.size > MAX_ATTACHMENT_BYTES) {
        message = `El archivo ${file.name} supera el tamaño máximo de 5 MB.`;
        continue;
      }
      next.push(file);
    }
    setFiles(next);
    setFileError(message);
  }

  function removeFile(index) {
    setFiles(files.filter((_, position) => position !== index));
    setFileError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const message = validateTaskInput(values) || validateExtras({ ...values, tags, subtasks, links, files });
    if (message) {
      setError(message);
      return;
    }

    setError("");
    setSubmitting(true);

    let created;
    try {
      created = await onCreate({
        title: values.title,
        description: values.description,
        dueDate: values.dueDate,
        priority: values.priority,
        assignee: values.assignee,
        subtasks,
        tags,
        links,
      });
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
      return;
    }

    resetForm();

    if (onUpload) {
      const failed = [];
      for (const file of files) {
        try {
          await onUpload(created.id, file);
        } catch (err) {
          failed.push(`${file.name} (${err.message})`);
        }
      }
      if (failed.length > 0) {
        setError(`La tarea se creó, pero no se pudieron adjuntar: ${failed.join(", ")}.`);
      }
    }

    setSubmitting(false);
  }

  return (
    <form
      className="task-form"
      onSubmit={handleSubmit}
      noValidate
      data-testid="task-form"
    >
      <h2 className="task-form__heading">Nueva tarea</h2>

      <TaskFields
        idPrefix="new-task"
        values={values}
        onChange={setValues}
        disabled={submitting}
        minDueDate={todayISO()}
      />

      <div className="extras">
        <details className="extras__section">
          <summary className="extras__summary">
            Etiquetas
            {tags.length > 0 && (
              <span className="extras__count">
                {tags.length}/{MAX_TAGS}
              </span>
            )}
          </summary>
          <div className="extras__body">
            {tags.length > 0 && (
              <div className="chips">
                {tags.map((tag) => (
                  <span key={tag} className="chip" data-testid="new-task-tag-chip">
                    {tag}
                    <button
                      type="button"
                      className="chip__remove"
                      aria-label={`Quitar etiqueta ${tag}`}
                      onClick={() => removeTag(tag)}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
            <input
              type="text"
              className="extras__input"
              data-testid="new-task-tag-input"
              value={tagInput}
              maxLength={MAX_TAG_LENGTH}
              placeholder="Escribí una etiqueta y presioná Enter"
              list="new-task-tag-suggestions"
              onChange={(event) => {
                setTagInput(event.target.value);
                setTagError("");
              }}
              onKeyDown={handleTagKeyDown}
            />
            <datalist id="new-task-tag-suggestions">
              {suggestions.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
            <p className="hint">
              Hasta {MAX_TAGS} etiquetas. Presioná Enter o coma para agregar.
            </p>
            {tagError && (
              <p className="field-error" role="alert" data-testid="new-task-tag-error">
                {tagError}
              </p>
            )}
          </div>
        </details>

        <details className="extras__section">
          <summary className="extras__summary">
            Checklist inicial
            {subtasks.length > 0 && (
              <span className="extras__count">
                {subtasks.length}/{MAX_SUBTASKS}
              </span>
            )}
          </summary>
          <div className="extras__body">
            {subtasks.length > 0 && (
              <ul className="draft-list">
                {subtasks.map((title, index) => (
                  <li key={`${title}-${index}`} className="draft-item">
                    <span
                      className="draft-item__text"
                      data-testid="new-task-subtask-item"
                    >
                      {title}
                    </span>
                    <button
                      type="button"
                      className="icon-button"
                      aria-label={`Quitar ${title}`}
                      onClick={() => removeSubtaskItem(index)}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="inline-form">
              <input
                type="text"
                data-testid="new-task-subtask-input"
                value={subtaskInput}
                maxLength={MAX_SUBTASK_LENGTH}
                placeholder="Nuevo ítem del checklist"
                onChange={(event) => {
                  setSubtaskInput(event.target.value);
                  setSubtaskError("");
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addSubtaskItem();
                  }
                }}
              />
              <button
                type="button"
                className="btn"
                data-testid="new-task-subtask-add"
                onClick={addSubtaskItem}
              >
                Agregar
              </button>
            </div>
            <p className="hint">Hasta {MAX_SUBTASKS} ítems.</p>
            {subtaskError && (
              <p className="field-error" role="alert" data-testid="new-task-subtask-error">
                {subtaskError}
              </p>
            )}
          </div>
        </details>

        <details className="extras__section">
          <summary className="extras__summary">
            Enlaces
            {links.length > 0 && (
              <span className="extras__count">
                {links.length}/{MAX_LINKS}
              </span>
            )}
          </summary>
          <div className="extras__body">
            {links.length > 0 && (
              <ul className="draft-list">
                {links.map((link, index) => (
                  <li key={`${link.url}-${index}`} className="draft-item">
                    <span className="draft-item__text" data-testid="new-task-link-item">
                      {link.label || link.url}
                    </span>
                    {link.label && (
                      <span className="draft-item__meta">{link.url}</span>
                    )}
                    <button
                      type="button"
                      className="icon-button"
                      aria-label={`Quitar enlace ${link.url}`}
                      onClick={() => removeLink(index)}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="link-row">
              <input
                type="text"
                className="extras__input"
                data-testid="new-task-link-url"
                value={linkUrl}
                maxLength={MAX_LINK_URL_LENGTH}
                placeholder="https://ejemplo.com"
                onChange={(event) => {
                  setLinkUrl(event.target.value);
                  setLinkError("");
                }}
              />
              <input
                type="text"
                className="extras__input"
                data-testid="new-task-link-label"
                value={linkLabel}
                maxLength={MAX_LINK_LABEL_LENGTH}
                placeholder="Nombre (opcional)"
                onChange={(event) => {
                  setLinkLabel(event.target.value);
                  setLinkError("");
                }}
              />
              <button
                type="button"
                className="btn btn--ghost"
                data-testid="new-task-link-add"
                onClick={addLink}
              >
                Agregar enlace
              </button>
            </div>
            <p className="hint">
              Hasta {MAX_LINKS} enlaces. Deben empezar con http:// o https://.
            </p>
            {linkError && (
              <p className="field-error" role="alert" data-testid="new-task-link-error">
                {linkError}
              </p>
            )}
          </div>
        </details>

        <details className="extras__section">
          <summary className="extras__summary">
            Adjuntos
            {files.length > 0 && (
              <span className="extras__count">
                {files.length}/{MAX_ATTACHMENTS}
              </span>
            )}
          </summary>
          <div className="extras__body">
            {files.length > 0 && (
              <ul className="draft-list">
                {files.map((file, index) => (
                  <li key={`${file.name}-${index}`} className="draft-item">
                    <span className="draft-item__text" data-testid="new-task-file-item">
                      {file.name}
                    </span>
                    <span className="draft-item__meta">{formatSize(file.size)}</span>
                    <button
                      type="button"
                      className="icon-button"
                      aria-label={`Quitar ${file.name}`}
                      onClick={() => removeFile(index)}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <input
              ref={fileInputRef}
              type="file"
              className="extras__file"
              multiple
              accept={ALLOWED_EXTENSIONS.join(",")}
              data-testid="new-task-attachment-input"
              onChange={handleFileChange}
            />
            <p className="hint">
              Hasta {MAX_ATTACHMENTS} archivos de 5 MB. Formatos:{" "}
              {ALLOWED_EXTENSIONS.join(", ")}.
            </p>
            {fileError && (
              <p className="field-error" role="alert" data-testid="new-task-file-error">
                {fileError}
              </p>
            )}
          </div>
        </details>
      </div>

      <div className="task-form__actions">
        <button
          type="submit"
          className="btn"
          data-testid="task-submit"
          disabled={submitting}
        >
          {submitting ? "Agregando..." : "Agregar tarea"}
        </button>
      </div>

      {error && (
        <p className="task-form__error" role="alert" data-testid="task-form-error">
          {error}
        </p>
      )}
    </form>
  );
}
