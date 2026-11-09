export const MAX_TITLE_LENGTH = 100;
export const MAX_DESCRIPTION_LENGTH = 500;
export const MAX_ASSIGNEE_LENGTH = 60;

export const PRIORITY_OPTIONS = ["Baja", "Media", "Alta"];
export const DEFAULT_PRIORITY = "Media";

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
  showGroups = false,
}) {
  function update(field, value) {
    onChange({ ...values, [field]: value });
  }

  const requiredMark = showGroups ? (
    <span className="field__required" aria-hidden="true">
      *
    </span>
  ) : null;
  const optionalMark = showGroups ? (
    <span className="field__optional">Opcional</span>
  ) : null;

  const titleField = (
    <div className="field">
      <label htmlFor={`${idPrefix}-title`}>
        Título {requiredMark}
      </label>
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
  );

  const descriptionField = (
    <div className="field">
      <label htmlFor={`${idPrefix}-description`}>Descripción {optionalMark}</label>
      <textarea
        id={`${idPrefix}-description`}
        data-testid={`${idPrefix}-description`}
        rows={2}
        placeholder="Detalle de la tarea"
        value={values.description}
        maxLength={MAX_DESCRIPTION_LENGTH}
        disabled={disabled}
        onChange={(event) => update("description", event.target.value)}
      />
    </div>
  );

  const dueField = (
    <div className="field">
      <label htmlFor={`${idPrefix}-due`}>Fecha límite {optionalMark}</label>
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
  );

  const priorityField = (
    <div className="field">
      <label htmlFor={`${idPrefix}-priority`}>Prioridad {optionalMark}</label>
      <select
        id={`${idPrefix}-priority`}
        data-testid={`${idPrefix}-priority`}
        value={values.priority ?? DEFAULT_PRIORITY}
        disabled={disabled}
        onChange={(event) => update("priority", event.target.value)}
      >
        {PRIORITY_OPTIONS.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );

  const assigneeField = (
    <div className="field">
      <label htmlFor={`${idPrefix}-assignee`}>Responsable {optionalMark}</label>
      <input
        id={`${idPrefix}-assignee`}
        data-testid={`${idPrefix}-assignee`}
        type="text"
        placeholder="Nombre o equipo"
        value={values.assignee ?? ""}
        maxLength={MAX_ASSIGNEE_LENGTH}
        disabled={disabled}
        onChange={(event) => update("assignee", event.target.value)}
      />
    </div>
  );

  if (!showGroups) {
    return (
      <div className="fields">
        {titleField}
        {descriptionField}
        {dueField}
        {priorityField}
        {assigneeField}
      </div>
    );
  }

  return (
    <div className="field-groups">
      <fieldset className="field-group">
        <legend className="field-group__legend">Datos obligatorios</legend>
        <div className="fields fields--single">{titleField}</div>
      </fieldset>

      <fieldset className="field-group">
        <legend className="field-group__legend field-group__legend--optional">
          Datos opcionales
        </legend>
        <div className="fields">
          {descriptionField}
          {dueField}
          {priorityField}
          {assigneeField}
        </div>
      </fieldset>
    </div>
  );
}
