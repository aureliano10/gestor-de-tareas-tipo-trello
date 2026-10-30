import { useState } from "react";
import { todayISO } from "../format.js";
import TaskFields, { validateTaskInput } from "./TaskFields.jsx";

const EMPTY_TASK = { title: "", description: "", dueDate: "" };

export default function TaskForm({ onCreate }) {
  const [values, setValues] = useState(EMPTY_TASK);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    const message = validateTaskInput(values);
    if (message) {
      setError(message);
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      await onCreate(values);
      setValues(EMPTY_TASK);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className="task-form"
      onSubmit={handleSubmit}
      noValidate
      data-testid="task-form"
    >
      <h2 className="task-form__heading">Nueva tarea</h2>

      <TaskFields
        idPrefix="new-task"
        values={values}
        onChange={setValues}
        disabled={submitting}
        minDueDate={todayISO()}
      />

      <div className="task-form__actions">
        <button
          type="submit"
          className="btn"
          data-testid="task-submit"
          disabled={submitting}
        >
          {submitting ? "Agregando..." : "Agregar tarea"}
        </button>
      </div>

      {error && (
        <p className="task-form__error" role="alert" data-testid="task-form-error">
          {error}
        </p>
      )}
    </form>
  );
}
