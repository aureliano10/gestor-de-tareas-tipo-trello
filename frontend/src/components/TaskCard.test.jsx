import { describe, it, expect, afterEach, vi } from "vitest";
import { render, cleanup, fireEvent } from "@testing-library/react";
import TaskCard from "./TaskCard.jsx";

afterEach(cleanup);

function makeTask(overrides = {}) {
  return {
    id: 7,
    title: "Preparar informe",
    description: "",
    status: "Pendiente",
    priority: "Media",
    assignee: "",
    due_date: null,
    overdue: false,
    subtask_total: 0,
    subtask_done: 0,
    attachments: [],
    tags: [],
    ...overrides,
  };
}

describe("TaskCard", () => {
  it("muestra el título y la insignia de prioridad", () => {
    const { getByTestId } = render(
      <TaskCard task={makeTask({ priority: "Alta" })} onOpen={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(getByTestId("task-title").textContent).toBe("Preparar informe");
    const badge = getByTestId("priority-badge");
    expect(badge.textContent).toBe("Alta");
    expect(badge.className).toContain("badge--priority-alta");
  });

  it("solo muestra la descripción cuando existe", () => {
    const { queryByText, getByText } = render(
      <TaskCard task={makeTask({ description: "Detalle" })} onOpen={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(getByText("Detalle")).toBeTruthy();
    expect(queryByText("Sin descripción")).toBeNull();
  });

  it("muestra la insignia de checklist con el avance", () => {
    const { getByTestId } = render(
      <TaskCard
        task={makeTask({ subtask_total: 3, subtask_done: 2 })}
        onOpen={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    const badge = getByTestId("checklist-badge");
    expect(badge.textContent).toBe("2/3 subtareas");
    expect(badge.className).not.toContain("badge--complete");
  });

  it("marca el checklist completo en verde", () => {
    const { getByTestId } = render(
      <TaskCard
        task={makeTask({ subtask_total: 2, subtask_done: 2 })}
        onOpen={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    expect(getByTestId("checklist-badge").className).toContain("badge--complete");
  });

  it("no muestra insignia de checklist sin subtareas", () => {
    const { queryByTestId } = render(
      <TaskCard task={makeTask()} onOpen={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(queryByTestId("checklist-badge")).toBeNull();
  });

  it("pluraliza la insignia de archivos", () => {
    const { getByTestId, rerender } = render(
      <TaskCard
        task={makeTask({ attachments: [{ id: 1 }] })}
        onOpen={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    expect(getByTestId("files-badge").textContent).toBe("1 archivo");

    rerender(
      <TaskCard
        task={makeTask({ attachments: [{ id: 1 }, { id: 2 }] })}
        onOpen={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    expect(getByTestId("files-badge").textContent).toBe("2 archivos");
  });

  it("oculta la insignia de archivos sin adjuntos", () => {
    const { queryByTestId } = render(
      <TaskCard task={makeTask()} onOpen={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(queryByTestId("files-badge")).toBeNull();
  });

  it("muestra responsable y etiquetas", () => {
    const { getByTestId, getAllByTestId } = render(
      <TaskCard
        task={makeTask({ assignee: "Ana", tags: ["backend", "pruebas"] })}
        onOpen={vi.fn()}
        onDelete={vi.fn()}
      />,
    );
    expect(getByTestId("task-assignee").textContent).toBe("Ana");
    expect(getAllByTestId("task-tag").map((tag) => tag.textContent)).toEqual([
      "backend",
      "pruebas",
    ]);
  });

  it("agrega la clase de vencida", () => {
    const { getByTestId } = render(
      <TaskCard task={makeTask({ overdue: true })} onOpen={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(getByTestId("task-card").className).toContain("task--overdue");
  });

  it("abre la tarea al hacer clic en la tarjeta", () => {
    const onOpen = vi.fn();
    const { getByTestId } = render(
      <TaskCard task={makeTask()} onOpen={onOpen} onDelete={vi.fn()} />,
    );
    fireEvent.click(getByTestId("task-card"));
    expect(onOpen).toHaveBeenCalledWith(7);
  });

  it("elimina la tarea sin abrirla", () => {
    const onOpen = vi.fn();
    const onDelete = vi.fn();
    const { getByTestId } = render(
      <TaskCard task={makeTask()} onOpen={onOpen} onDelete={onDelete} />,
    );
    fireEvent.click(getByTestId("task-delete"));
    expect(onDelete).toHaveBeenCalledWith(7);
    expect(onOpen).not.toHaveBeenCalled();
  });

  it("abre la tarea con Enter y con Espacio", () => {
    const onOpen = vi.fn();
    const { getByTestId } = render(
      <TaskCard task={makeTask()} onOpen={onOpen} onDelete={vi.fn()} />,
    );
    fireEvent.keyDown(getByTestId("task-card"), { key: "Enter" });
    fireEvent.keyDown(getByTestId("task-card"), { key: " " });
    expect(onOpen).toHaveBeenCalledTimes(2);
  });

  it("ignora la tecla recibida desde un control interno", () => {
    const onOpen = vi.fn();
    const { getByTestId } = render(
      <TaskCard task={makeTask()} onOpen={onOpen} onDelete={vi.fn()} />,
    );
    fireEvent.keyDown(getByTestId("task-title"), { key: "Enter" });
    expect(onOpen).not.toHaveBeenCalled();
  });
});
