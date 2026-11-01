import { describe, it, expect } from "vitest";
import {
  ALLOWED_EXTENSIONS,
  MAX_ATTACHMENTS,
  MAX_ATTACHMENT_BYTES,
  daysUntil,
  dueInfo,
  extensionOf,
  formatDate,
  formatDateTime,
  formatSize,
  prioritySlug,
  todayISO,
} from "./format.js";

/** Fecha ISO (YYYY-MM-DD) desplazada `days` días respecto de hoy, en hora local. */
function isoOffset(days) {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() + days);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

describe("constantes de adjuntos", () => {
  it("expone los límites y las extensiones permitidas", () => {
    expect(MAX_ATTACHMENTS).toBe(3);
    expect(MAX_ATTACHMENT_BYTES).toBe(5 * 1024 * 1024);
    expect(ALLOWED_EXTENSIONS).toContain(".pdf");
    expect(ALLOWED_EXTENSIONS).toContain(".docx");
  });
});

describe("formatSize", () => {
  it("usa bytes por debajo de 1 KB", () => {
    expect(formatSize(0)).toBe("0 B");
    expect(formatSize(1023)).toBe("1023 B");
  });

  it("usa KB por debajo de 1 MB", () => {
    expect(formatSize(1024)).toBe("1 KB");
    expect(formatSize(2 * 1024)).toBe("2 KB");
  });

  it("usa MB con un decimal a partir de 1 MB", () => {
    expect(formatSize(1024 * 1024)).toBe("1.0 MB");
    expect(formatSize(1536 * 1024)).toBe("1.5 MB");
  });
});

describe("extensionOf", () => {
  it("devuelve la extensión en minúsculas", () => {
    expect(extensionOf("Informe.PDF")).toBe(".pdf");
    expect(extensionOf("carpeta.archivo.TXT")).toBe(".txt");
  });

  it("devuelve cadena vacía cuando no hay extensión", () => {
    expect(extensionOf("sinextension")).toBe("");
  });
});

describe("prioritySlug", () => {
  it("normaliza la prioridad a minúsculas", () => {
    expect(prioritySlug("Alta")).toBe("alta");
    expect(prioritySlug("Media")).toBe("media");
  });

  it("devuelve cadena vacía ante valores ausentes", () => {
    expect(prioritySlug(null)).toBe("");
    expect(prioritySlug(undefined)).toBe("");
  });
});

describe("todayISO", () => {
  it("devuelve la fecha de hoy en formato ISO", () => {
    expect(todayISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(todayISO()).toBe(isoOffset(0));
  });
});

describe("daysUntil", () => {
  it("calcula la diferencia de días respecto de hoy", () => {
    expect(daysUntil(isoOffset(0))).toBe(0);
    expect(daysUntil(isoOffset(1))).toBe(1);
    expect(daysUntil(isoOffset(-3))).toBe(-3);
    expect(daysUntil(isoOffset(10))).toBe(10);
  });
});

describe("formatDate", () => {
  it("formatea una fecha ISO en formato local", () => {
    const out = formatDate("2026-03-15");
    expect(out).toContain("2026");
    expect(out).toContain("15");
  });
});

describe("formatDateTime", () => {
  it("formatea una fecha y hora ISO", () => {
    const out = formatDateTime("2026-03-15T14:30:00Z");
    expect(out).toContain("2026");
  });
});

describe("dueInfo", () => {
  it("devuelve null sin fecha", () => {
    expect(dueInfo("", false)).toBeNull();
    expect(dueInfo(null, false)).toBeNull();
    expect(dueInfo(undefined, false)).toBeNull();
  });

  it("describe la fecha cuando la tarea está terminada", () => {
    const pasada = dueInfo(isoOffset(-5), true);
    expect(pasada.tone).toBe("normal");
    expect(pasada.label).toContain("Venció el");

    const futura = dueInfo(isoOffset(5), true);
    expect(futura.tone).toBe("normal");
    expect(futura.label).toContain("Vence el");
  });

  it("clasifica la urgencia de una tarea pendiente", () => {
    expect(dueInfo(isoOffset(-5), false)).toEqual({
      label: "Vencida hace 5 días",
      tone: "overdue",
    });
    expect(dueInfo(isoOffset(-1), false)).toEqual({
      label: "Vencida ayer",
      tone: "overdue",
    });
    expect(dueInfo(isoOffset(0), false)).toEqual({
      label: "Vence hoy",
      tone: "today",
    });
    expect(dueInfo(isoOffset(1), false)).toEqual({
      label: "Vence mañana",
      tone: "soon",
    });
    expect(dueInfo(isoOffset(3), false)).toEqual({
      label: "Vence en 3 días",
      tone: "soon",
    });
  });

  it("usa la fecha concreta cuando falta más de tres días", () => {
    const lejana = dueInfo(isoOffset(10), false);
    expect(lejana.tone).toBe("normal");
    expect(lejana.label).toContain("Vence el");
  });
});
