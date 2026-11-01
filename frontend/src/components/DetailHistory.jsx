import { formatDateTime } from "../format.js";

/** Panel de historial de actividad del detalle. */
export default function DetailHistory({ task }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h3>Historial</h3>
      </div>

      {task.activity.length === 0 ? (
        <p className="muted">Sin actividad registrada.</p>
      ) : (
        <ol className="timeline" data-testid="activity-timeline">
          {task.activity.map((entry) => (
            <li key={entry.id} className="timeline__item">
              <span className="timeline__dot" aria-hidden="true" />
              <div className="timeline__content">
                <p className="timeline__action">{entry.action}</p>
                {entry.detail && (
                  <p className="timeline__detail">{entry.detail}</p>
                )}
                <time className="timeline__date" dateTime={entry.created_at}>
                  {formatDateTime(entry.created_at)}
                </time>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
