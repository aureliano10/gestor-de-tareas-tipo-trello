import { useRef, useState } from "react";
import { attachmentUrl } from "../api.js";
import {
  ALLOWED_EXTENSIONS,
  MAX_ATTACHMENTS,
  MAX_ATTACHMENT_BYTES,
  MAX_ATTACHMENT_MB,
  extensionOf,
  formatSize,
  isImageFile,
  isPreviewableFile,
} from "../format.js";
import AttachmentPreview from "./AttachmentPreview.jsx";

const UNDO_WINDOW_MS = 7000;

/** Panel de archivos adjuntos del detalle. */
export default function DetailAttachments({
  task,
  onUpload,
  onDeleteAttachment,
  onNotify,
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState(null);
  // AUD-35: se recuerda el archivo recién subido para poder restaurarlo.
  const uploadedFiles = useRef(new Map());

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    const extension = extensionOf(file.name);
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setError(
        `Formato no permitido. Se aceptan: ${ALLOWED_EXTENSIONS.join(", ")}.`,
      );
      return;
    }
    if (file.size === 0) {
      setError("El archivo está vacío.");
      return;
    }
    if (file.size > MAX_ATTACHMENT_BYTES) {
      setError(`El archivo supera el tamaño máximo de ${MAX_ATTACHMENT_MB} MB.`);
      return;
    }

    setError("");
    setBusy(true);
    try {
      const before = new Set(task.attachments.map((item) => item.id));
      const updated = await onUpload(task.id, file);
      const created = updated?.attachments?.find((item) => !before.has(item.id));
      if (created) {
        uploadedFiles.current.set(created.id, file);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(attachment) {
    setError("");
    setBusy(true);
    try {
      await onDeleteAttachment(task.id, attachment.id);
      const file = uploadedFiles.current.get(attachment.id);
      uploadedFiles.current.delete(attachment.id);
      onNotify?.(`Quitaste "${attachment.filename}".`, {
        actionLabel: file ? "Deshacer" : undefined,
        duration: UNDO_WINDOW_MS,
        onAction: file ? () => onUpload(task.id, file) : undefined,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const uploadDisabled = task.attachments.length >= MAX_ATTACHMENTS;

  return (
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
          {task.attachments.map((attachment) => {
            const previewable = isPreviewableFile(attachment.filename);
            const image = isImageFile(attachment.filename);
            const label =
              extensionOf(attachment.filename).slice(1).toUpperCase() || "AR";
            const open = () => setPreview(attachment);
            return (
              <li key={attachment.id} className="attachment-card">
                <span
                  className={`attachment-card__thumb${
                    image ? " attachment-card__thumb--image" : ""
                  }`}
                  aria-hidden="true"
                  onClick={previewable ? open : undefined}
                >
                  {image ? (
                    <img
                      src={attachmentUrl(task.id, attachment.id)}
                      alt=""
                      loading="lazy"
                    />
                  ) : (
                    label
                  )}
                </span>
                <div className="attachment-card__info">
                  {previewable ? (
                    <button
                      type="button"
                      className="attachments__name attachments__name--button"
                      onClick={open}
                      data-testid={`attachment-preview-${attachment.id}`}
                    >
                      {attachment.filename}
                    </button>
                  ) : (
                    <a
                      className="attachments__name"
                      href={attachmentUrl(task.id, attachment.id, {
                        download: true,
                      })}
                      download={attachment.filename}
                    >
                      {attachment.filename}
                    </a>
                  )}
                  <span className="attachments__meta">
                    {formatSize(attachment.size_bytes)}
                  </span>
                </div>
                <button
                  type="button"
                  className="icon-button"
                  onClick={() => handleDelete(attachment)}
                  disabled={busy}
                  aria-label={`Quitar ${attachment.filename}`}
                >
                  ×
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <label className={`upload${uploadDisabled ? " upload--disabled" : ""}`}>
        <input
          type="file"
          accept={ALLOWED_EXTENSIONS.join(",")}
          disabled={uploadDisabled || busy}
          data-testid="attachment-input"
          onChange={handleFileChange}
        />
        <span>
          {uploadDisabled ? "Límite de archivos alcanzado" : "Adjuntar archivo"}
        </span>
      </label>

      {error && (
        <p className="field-error" role="alert" data-testid="attachment-error">
          {error}
        </p>
      )}
      <p className="hint">
        Hasta {MAX_ATTACHMENTS} archivos de {MAX_ATTACHMENT_MB} MB. Formatos:{" "}
        {ALLOWED_EXTENSIONS.join(", ")}. Las imágenes se optimizan a WebP.
      </p>

      {preview && (
        <AttachmentPreview
          task={task}
          attachment={preview}
          onClose={() => setPreview(null)}
        />
      )}
    </section>
  );
}
