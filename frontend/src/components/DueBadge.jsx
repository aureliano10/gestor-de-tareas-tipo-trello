import { dueInfo } from "../format.js";

export default function DueBadge({ task }) {
  const info = dueInfo(task.due_date, task.status === "Terminada");
  if (!info) {
    return null;
  }
  return (
    <span className={`badge badge--due badge--${info.tone}`} data-testid="due-badge">
      {info.label}
    </span>
  );
}
