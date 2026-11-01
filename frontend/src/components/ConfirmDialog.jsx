import { useRef } from "react";
import { useFocusTrap } from "../useFocusTrap.js";

export default function ConfirmDialog({
  title,
  message,
  confirmLabel = "Confirmar",
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null);

  useFocusTrap(dialogRef, { onEscape: onCancel });

  return (
    <div className="overlay" onClick={onCancel}>
      <div
        className="dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby="confirm-message"
        data-testid="confirm-dialog"
        ref={dialogRef}
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="confirm-title" className="dialog__title">
          {title}
        </h2>
        <p id="confirm-message" className="dialog__message">
          {message}
        </p>
        <div className="dialog__actions">
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onCancel}
            data-testid="confirm-cancel"
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn btn--danger"
            onClick={onConfirm}
            data-testid="confirm-accept"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
