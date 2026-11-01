const DAY_MS = 24 * 60 * 60 * 1000;

export const MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024;
export const MAX_ATTACHMENTS = 3;
export const ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx"];

function parseISODate(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function daysUntil(iso) {
  const due = parseISODate(iso);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((due - today) / DAY_MS);
}

export function todayISO() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

export function formatDate(iso) {
  return parseISODate(iso).toLocaleDateString("es-AR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(0)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function extensionOf(filename) {
  const index = filename.lastIndexOf(".");
  return index === -1 ? "" : filename.slice(index).toLowerCase();
}

export function formatDateTime(iso) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Identificador estable de la clase CSS de prioridad (badge--priority-*). */
export function prioritySlug(priority) {
  return String(priority ?? "").toLowerCase();
}

/**
 * Describe la fecha límite y su urgencia.
 * `tone` alimenta el estilo: "overdue" | "today" | "soon" | "normal".
 */
export function dueInfo(iso, isFinished) {
  if (!iso) {
    return null;
  }
  const diff = daysUntil(iso);

  if (isFinished) {
    const label = diff < 0 ? `Venció el ${formatDate(iso)}` : `Vence el ${formatDate(iso)}`;
    return { label, tone: "normal" };
  }
  if (diff < -1) {
    return { label: `Vencida hace ${Math.abs(diff)} días`, tone: "overdue" };
  }
  if (diff === -1) {
    return { label: "Vencida ayer", tone: "overdue" };
  }
  if (diff === 0) {
    return { label: "Vence hoy", tone: "today" };
  }
  if (diff === 1) {
    return { label: "Vence mañana", tone: "soon" };
  }
  if (diff <= 3) {
    return { label: `Vence en ${diff} días`, tone: "soon" };
  }
  return { label: `Vence el ${formatDate(iso)}`, tone: "normal" };
}
