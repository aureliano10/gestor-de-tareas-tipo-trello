import { useRef } from "react";
import { attachmentUrl } from "../api.js";
import { formatSize, isImageFile } from "../format.js";
import { useFocusTrap } from "../useFocusTrap.js";

/** Vista previa de un adjunto (imagen o PDF) en un modal, al estilo Drive. */
export default function AttachmentPreview({ task, attachment, onClose }) {
  const dialogRef = useRef(null);

  useFocusTrap(dialogRef, { onEscape: onClose });

  const previewUrl = attachmentUrl(task.id, attachment.id);
  const downloadUrl = attachmentUrl(task.id, attachment.id, { download: true });
  const isImage = isImageFile(attachment.filename);

  return (
    <div className="overlay" onClick={onClose}>
      <div
        className="modal modal--preview"
        role="dialog"
        aria-modal="true"
        aria-labelledby="preview-title"
        data-testid="attachment-preview"
        ref={dialogRef}
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal__header">
          <div>
            <h2 id="preview-title" className="modal__title">
              {attachment.filename}
            </h2>
            <p className="modal__meta">{formatSize(attachment.size_bytes)}</p>
          </div>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Cerrar vista previa"
            data-testid="preview-close"
          >
            ×
          </button>
        </header>

        <div className="modal__body modal__body--preview">
          {isImage ? (
            <img
              className="preview__image"
              src={previewUrl}
              alt={attachment.filename}
              data-testid="preview-image"
            />
          ) : (
            <iframe
              className="preview__frame"
              src={previewUrl}
              title={attachment.filename}
              data-testid="preview-frame"
            />
          )}
        </div>

        <footer className="modal__footer">
          <a
            className="btn btn--ghost"
            href={previewUrl}
            target="_blank"
            rel="noreferrer"
          >
            Abrir en pestaña
          </a>
          <a
            className="btn"
            href={downloadUrl}
            download={attachment.filename}
            data-testid="preview-download"
          >
            Descargar
          </a>
        </footer>
      </div>
    </div>
  );
}
