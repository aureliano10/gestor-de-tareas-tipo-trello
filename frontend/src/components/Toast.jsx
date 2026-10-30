export default function Toast({ message, actionLabel, onAction, onClose }) {
  return (
    <div className="toast" role="status" data-testid="toast">
      <span className="toast__message">{message}</span>
      {actionLabel && (
        <button
          type="button"
          className="toast__action"
          onClick={onAction}
          data-testid="toast-action"
        >
          {actionLabel}
        </button>
      )}
      <button
        type="button"
        className="toast__close"
        onClick={onClose}
        aria-label="Cerrar aviso"
      >
        ×
      </button>
    </div>
  );
}
