import { useState } from "react";
import {
  MAX_LINKS,
  MAX_LINK_LABEL_LENGTH,
  MAX_LINK_URL_LENGTH,
  validateLink,
} from "../links.js";

const UNDO_WINDOW_MS = 7000;

function linkPayload(links) {
  return links.map((link) => ({ url: link.url, label: link.label }));
}

function taskValues(task, links) {
  return {
    title: task.title,
    description: task.description,
    dueDate: task.due_date ?? "",
    priority: task.priority,
    assignee: task.assignee,
    tags: task.tags,
    links,
  };
}

/** Panel de enlaces del detalle. Reutiliza las reglas de `links.js` (AUD-20). */
export default function DetailLinks({ task, onUpdate, onNotify }) {
  const [url, setUrl] = useState("");
  const [label, setLabel] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function applyLinks(nextLinks) {
    setError("");
    try {
      await onUpdate(task.id, taskValues(task, nextLinks));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }

  async function handleAdd(event) {
    event.preventDefault();
    const message = validateLink({ url, label, existing: task.links });

    if (message) {
      setError(message);
      return;
    }

    setBusy(true);
    const saved = await applyLinks([
      ...linkPayload(task.links),
      { url: url.trim(), label: label.trim() },
    ]);
    setBusy(false);

    if (saved) {
      setUrl("");
      setLabel("");
    }
  }

  async function handleRemove(link) {
    const previous = linkPayload(task.links);
    setBusy(true);
    const saved = await applyLinks(
      previous.filter((item) => item.url !== link.url),
    );
    setBusy(false);

    if (saved) {
      onNotify?.(`Quitaste el enlace "${link.label || link.url}".`, {
        actionLabel: "Deshacer",
        duration: UNDO_WINDOW_MS,
        onAction: () => applyLinks(previous),
      });
    }
  }

  return (
    <section className="panel">
      <div className="panel__header">
        <h3>
          Enlaces
          <span className="panel__counter">
            {task.links.length}/{MAX_LINKS}
          </span>
        </h3>
      </div>

      {task.links.length === 0 ? (
        <p className="muted">Sin enlaces.</p>
      ) : (
        <ul className="links">
          {task.links.map((link) => (
            <li key={link.id} className="links__item">
              <a
                className="links__name"
                href={link.url}
                target="_blank"
                rel="noreferrer"
              >
                {link.label || link.url}
              </a>
              {link.label && <span className="links__url">{link.url}</span>}
              <button
                type="button"
                className="icon-button"
                onClick={() => handleRemove(link)}
                disabled={busy}
                aria-label={`Quitar enlace ${link.url}`}
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
          value={url}
          maxLength={MAX_LINK_URL_LENGTH}
          placeholder="https://ejemplo.com"
          aria-label="URL del enlace"
          data-testid="link-url-input"
          onChange={(event) => {
            setUrl(event.target.value);
            setError("");
          }}
        />
        <input
          type="text"
          value={label}
          maxLength={MAX_LINK_LABEL_LENGTH}
          placeholder="Nombre"
          aria-label="Nombre del enlace"
          data-testid="link-label-input"
          onChange={(event) => {
            setLabel(event.target.value);
            setError("");
          }}
        />
        <button
          type="submit"
          className="btn"
          data-testid="link-add"
          disabled={busy}
        >
          {busy ? "Agregando..." : "Agregar"}
        </button>
      </form>

      {error && (
        <p className="field-error" role="alert" data-testid="link-error">
          {error}
        </p>
      )}
      <p className="hint">
        Hasta {MAX_LINKS} enlaces. Deben empezar con http:// o https://.
      </p>
    </section>
  );
}
