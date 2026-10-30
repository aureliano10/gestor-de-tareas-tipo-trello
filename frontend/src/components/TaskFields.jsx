export const MAX_TITLE_LENGTH = 100;
export const MAX_DESCRIPTION_LENGTH = 500;

export function validateTaskInput({ title, description }) {
  const cleanTitle = (title ?? "").trim();
  if (!cleanTitle) {
    return "El título es obligatorio y no puede contener solo espacios.";
  }
  if (cleanTitle.length > MAX_TITLE_LENGTH) {
    return `El título no puede superar los ${MAX_TITLE_LENGTH} caracteres.`;
  }
  if ((description ?? "").trim().length > MAX_DESCRIPTION_LENGTH) {
    return `La descripción no puede superar los ${MAX_DESCRIPTION_LENGTH} caracteres.`;
  }
  return "";
}

export default function TaskFields({
  idPrefix,
  values,
  onChange,
  disabled,
  minDueDate,
}) {
  function update(field, value) {
    onChange({ ...values, [field]: value });
  }

  return (
    <div className="fields">
      <div className="field">
        <label htmlFor={`${idPrefix}-title`}>Título</label>
        <input
          id={`${idPrefix}-title`}
          data-testid={`${idPrefix}-title`}
          type="text"
          placeholder="Ej. Preparar informe de pruebas"
          value={values.title}
          maxLength={MAX_TITLE_LENGTH}
          disabled={disabled}
          onChange={(event) => update("title", event.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor={`${idPrefix}-description`}>Descripción</label>
        <textarea
          id={`${idPrefix}-description`}
          data-testid={`${idPrefix}-description`}
          rows={2}
          placeholder="Detalle opcional de la tarea"
          value={values.description}
          maxLength={MAX_DESCRIPTION_LENGTH}
          disabled={disabled}
          onChange={(event) => update("description", event.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor={`${idPrefix}-due`}>Fecha límite</label>
        <input
          id={`${idPrefix}-due`}
          data-testid={`${idPrefix}-due`}
          type="date"
          value={values.dueDate}
          min={minDueDate}
          disabled={disabled}
          onChange={(event) => update("dueDate", event.target.value)}
        />
      </div>
    </div>
  );
}
