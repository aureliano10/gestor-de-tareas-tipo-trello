import { describe, it, expect, afterEach, vi } from "vitest";
import { render, cleanup, fireEvent, waitFor } from "@testing-library/react";
import TaskDetailModal from "./TaskDetailModal.jsx";

afterEach(cleanup);

function makeTask() {
  return {
    id: 1,
    title: "Tarea",
    description: "",
    status: "Pendiente",
    priority: "Media",
    assignee: "",
    due_date: null,
    overdue: false,
    subtask_total: 0,
    subtask_done: 0,
    subtasks: [],
    attachments: [],
    tags: [],
    links: [],
    activity: [],
  };
}

function setup(overrides = {}) {
  const props = {
    task: makeTask(),
    onClose: vi.fn(),
    onNotify: vi.fn(),
    onMove: vi.fn().mockResolvedValue(undefined),
    onUpdate: vi.fn().mockResolvedValue(undefined),
    onAddSubtask: vi.fn().mockResolvedValue(undefined),
    onToggleSubtask: vi.fn().mockResolvedValue(undefined),
    onDeleteSubtask: vi.fn().mockResolvedValue(undefined),
    onUpload: vi.fn().mockResolvedValue(undefined),
    onDeleteAttachment: vi.fn().mockResolvedValue(undefined),
    onDelete: vi.fn(),
    ...overrides,
  };
  return { ...render(<TaskDetailModal {...props} />), props };
}

describe("TaskDetailModal", () => {
  it("muestra el error del backend cuando no se puede mover", async () => {
    const onMove = vi
      .fn()
      .mockRejectedValue(
        new Error("No se puede finalizar: la tarea tiene 1 subtarea pendiente"),
      );
    const { getByTestId, findByTestId } = setup({ onMove });

    fireEvent.change(getByTestId("detail-status"), {
      target: { value: "Terminada" },
    });

    const error = await findByTestId("move-error");
    expect(error.textContent).toContain("subtarea pendiente");
  });

  it("limpia el error de movimiento al reintentar", async () => {
    const onMove = vi
      .fn()
      .mockRejectedValueOnce(new Error("Primer intento falló"))
      .mockResolvedValueOnce(undefined);
    const { getByTestId, findByTestId, queryByTestId } = setup({ onMove });

    fireEvent.change(getByTestId("detail-status"), {
      target: { value: "Terminada" },
    });
    await findByTestId("move-error");

    fireEvent.change(getByTestId("detail-status"), {
      target: { value: "En curso" },
    });

    await waitFor(() => expect(onMove).toHaveBeenCalledTimes(2));
    expect(queryByTestId("move-error")).toBeNull();
  });
});
