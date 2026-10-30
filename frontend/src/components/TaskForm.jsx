import { useState } from "react";

const MAX_TITLE_LENGTH = 100;

export default function TaskForm({ onCreate }) {
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const cleanTitle = title.trim();

    if (!cleanTitle) {
      setError("El título es obligatorio y no puede contener solo espacios.");
      return;
    }
    if (cleanTitle.length > MAX_TITLE_LENGTH) {
      setError(`El título no puede superar los ${MAX_TITLE_LENGTH} caracteres.`);
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      await onCreate(cleanTitle);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="task-form" onSubmit={handleSubmit} noValidate>
      <div className="task-form__field">
        <label htmlFor="task-title">Nueva tarea</label>
        <input
          id="task-title"
          name="title"
          type="text"
          placeholder="Ej. Preparar informe de pruebas"
          value={title}
          maxLength={MAX_TITLE_LENGTH}
          onChange={(event) => {
            setTitle(event.target.value);
            setError("");
          }}
        />
      </div>
      <button type="submit" disabled={submitting}>
        {submitting ? "Agregando..." : "Agregar"}
      </button>
      {error && (
        <p className="task-form__error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
