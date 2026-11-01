import { describe, it, expect, afterEach, vi } from "vitest";
import { render, cleanup, fireEvent, waitFor } from "@testing-library/react";
import TaskForm from "./TaskForm.jsx";
import { validateTaskInput } from "./TaskFields.jsx";

afterEach(cleanup);

function setup(overrides = {}) {
  const onCreate = overrides.onCreate ?? vi.fn().mockResolvedValue({ id: 1 });
  const onUpload = overrides.onUpload ?? vi.fn().mockResolvedValue(undefined);
  const utils = render(<TaskForm onCreate={onCreate} onUpload={onUpload} />);
  return { onCreate, onUpload, ...utils };
}

describe("validateTaskInput", () => {
  it("exige un título no vacío", () => {
    expect(validateTaskInput({ title: "   ", description: "" })).toBe(
      "El título es obligatorio y no puede contener solo espacios.",
    );
  });

  it("limita la longitud del título", () => {
    expect(validateTaskInput({ title: "a".repeat(101) })).toBe(
      "El título no puede superar los 100 caracteres.",
    );
  });

  it("limita la longitud de la descripción", () => {
    expect(
      validateTaskInput({ title: "Ok", description: "a".repeat(501) }),
    ).toBe("La descripción no puede superar los 500 caracteres.");
  });

  it("acepta una entrada válida", () => {
    expect(validateTaskInput({ title: "Ok", description: "Detalle" })).toBe("");
  });
});

describe("TaskForm", () => {
  it("valida el título vacío sin llamar a onCreate", () => {
    const { onCreate, getByTestId } = setup();
    fireEvent.click(getByTestId("task-submit"));
    expect(getByTestId("task-form-error").textContent).toBe(
      "El título es obligatorio y no puede contener solo espacios.",
    );
    expect(onCreate).not.toHaveBeenCalled();
  });

  it("crea la tarea con los valores cargados y limpia el formulario", () => {
    const { onCreate, getByTestId } = setup();
    fireEvent.change(getByTestId("new-task-title"), { target: { value: "Nueva" } });
    fireEvent.change(getByTestId("new-task-description"), {
      target: { value: "Detalle" },
    });
    fireEvent.click(getByTestId("task-submit"));

    return waitFor(() => expect(onCreate).toHaveBeenCalledTimes(1)).then(() => {
      expect(onCreate.mock.calls[0][0]).toMatchObject({
        title: "Nueva",
        description: "Detalle",
        priority: "Media",
      });
      expect(getByTestId("new-task-title").value).toBe("");
    });
  });

  it("muestra el mensaje cuando onCreate falla", () => {
    const onCreate = vi.fn().mockRejectedValue(new Error("El servidor falló"));
    const { getByTestId } = setup({ onCreate });
    fireEvent.change(getByTestId("new-task-title"), { target: { value: "Nueva" } });
    fireEvent.click(getByTestId("task-submit"));

    return waitFor(() =>
      expect(getByTestId("task-form-error").textContent).toContain("El servidor falló"),
    );
  });

  it("avisa cuando no se pudieron adjuntar los archivos", () => {
    const onCreate = vi.fn().mockResolvedValue({ id: 5 });
    const onUpload = vi.fn().mockRejectedValue(new Error("red"));
    const { getByTestId } = setup({ onCreate, onUpload });

    const file = new File(["contenido"], "acta.txt", { type: "text/plain" });
    fireEvent.change(getByTestId("new-task-attachment-input"), {
      target: { files: [file] },
    });
    fireEvent.change(getByTestId("new-task-title"), { target: { value: "Con adjunto" } });
    fireEvent.click(getByTestId("task-submit"));

    return waitFor(() =>
      expect(getByTestId("task-form-error").textContent).toContain(
        "no se pudieron adjuntar",
      ),
    );
  });

  it("agrega etiquetas con Enter", () => {
    const { getByTestId } = setup();
    const input = getByTestId("new-task-tag-input");
    fireEvent.change(input, { target: { value: "backend" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(getByTestId("new-task-tag-chip").textContent).toContain("backend");
  });

  it("agrega subtareas al checklist", () => {
    const { getByTestId } = setup();
    fireEvent.change(getByTestId("new-task-subtask-input"), {
      target: { value: "Paso 1" },
    });
    fireEvent.click(getByTestId("new-task-subtask-add"));
    expect(getByTestId("new-task-subtask-item").textContent).toContain("Paso 1");
  });

  it("valida y agrega enlaces", () => {
    const { getByTestId } = setup();
    fireEvent.change(getByTestId("new-task-link-url"), {
      target: { value: "ejemplo.com" },
    });
    fireEvent.click(getByTestId("new-task-link-add"));
    expect(getByTestId("new-task-link-error").textContent).toContain("http://");

    fireEvent.change(getByTestId("new-task-link-url"), {
      target: { value: "https://ejemplo.com" },
    });
    fireEvent.click(getByTestId("new-task-link-add"));
    expect(getByTestId("new-task-link-item").textContent).toContain(
      "https://ejemplo.com",
    );
  });

  it("rechaza archivos con extensión no permitida", () => {
    const { getByTestId } = setup();
    const file = new File(["binario"], "malware.exe", {
      type: "application/octet-stream",
    });
    fireEvent.change(getByTestId("new-task-attachment-input"), {
      target: { files: [file] },
    });
    expect(getByTestId("new-task-file-error").textContent).toContain(
      "Formato no permitido",
    );
  });
});
