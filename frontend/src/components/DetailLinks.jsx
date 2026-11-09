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

/** Clasifica el enlace para mostrar un ícono acorde (video, docs o genérico). */
function linkKind(url) {
  let host = "";
  try {
    host = new URL(url).hostname.replace(/^www\./, "").toLowerCase();
  } catch {
    return "link";
  }
  if (/(youtube\.com|youtu\.be)$/.test(host)) {
    return "video";
  }
  if (
    /(docs|developer|mdn|github|gitlab|stackoverflow|stackexchange|readthedocs|wikipedia|python)/.test(
      host,
    )
  ) {
    return "docs";
  }
  return "link";
}

/** Devuelve solo el dominio, para mostrarlo como dato secundario del enlace. */
function linkHost(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function LinkIcon({ kind }) {
  if (kind === "video") {
    return (
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
        <path d="M8 5v14l11-7z" fill="currentColor" />
      </svg>
    );
  }
  if (kind === "docs") {
    return (
      <svg
        viewBox="0 0 24 24"
        width="16"
        height="16"
        aria-hidden="true"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M6 3h7l5 5v13H6z" />
        <path d="M13 3v5h5" />
        <path d="M9 13h6M9 17h4" />
      </svg>
    );
  }
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1" />
      <path d="M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1" />
    </svg>
  );
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
            <li key={link.id} className="link-card">
              <span className="link-card__icon" aria-hidden="true">
                <LinkIcon kind={linkKind(link.url)} />
              </span>
              <div className="link-card__info">
                <a
                  className="links__name"
                  href={link.url}
                  target="_blank"
                  rel="noreferrer"
                  title={link.url}
                >
                  {link.label || link.url}
                </a>
                {link.label && (
                  <span className="links__url">{linkHost(link.url)}</span>
                )}
              </div>
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
