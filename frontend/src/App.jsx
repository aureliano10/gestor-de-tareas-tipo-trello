import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createSubtask,
  createTask,
  deleteAttachment,
  deleteSubtask,
  deleteTask,
  getTags,
  getTasks,
  moveTask,
  restoreTask,
  updateSubtask,
  updateTask,
  uploadAttachment,
} from "./api.js";
import Board from "./components/Board.jsx";
import ConfirmDialog from "./components/ConfirmDialog.jsx";
import TaskDetailModal from "./components/TaskDetailModal.jsx";
import TaskForm from "./components/TaskForm.jsx";
import Toast from "./components/Toast.jsx";

const UNDO_WINDOW_MS = 7000;
const SEARCH_DEBOUNCE_MS = 300;

const PRIORITY_FILTERS = ["Baja", "Media", "Alta"];
const SORT_OPTIONS = [
  { value: "position", label: "Posición" },
  { value: "priority", label: "Prioridad" },
  { value: "due", label: "Vencimiento" },
  { value: "created", label: "Creación" },
];

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);

  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [sort, setSort] = useState("position");
  const [tagOptions, setTagOptions] = useState([]);

  const [detailId, setDetailId] = useState(null);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [undone, setUndone] = useState(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  const params = useMemo(
    () => ({
      overdue: overdueOnly,
      q: debouncedQuery,
      priority: priorityFilter,
      tag: tagFilter,
      sort,
    }),
    [overdueOnly, debouncedQuery, priorityFilter, tagFilter, sort],
  );

  const load = useCallback(async (filters, { silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
    }
    try {
      const [list, names] = await Promise.all([getTasks(filters), getTags()]);
      setTasks(list);
      setTagOptions(names);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    load(params);
  }, [load, params]);

  const refresh = useCallback(
    () => load(params, { silent: true }),
    [load, params],
  );

  /**
   * Ejecuta una acción y recarga el tablero.
   * Los errores se propagan para que los formularios y el modal los muestren.
   */
  const mutate = useCallback(
    async (action) => {
      const result = await action();
      await refresh();
      return result;
    },
    [refresh],
  );

  /** Acción disparada desde el tablero: el error va al aviso general. */
  async function mutateBoard(action) {
    setError("");
    try {
      await mutate(action);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!undone) {
      return undefined;
    }
    const timer = setTimeout(() => setUndone(null), UNDO_WINDOW_MS);
    return () => clearTimeout(timer);
  }, [undone]);

  useEffect(() => {
    if (detailId !== null && !loading && !tasks.some((task) => task.id === detailId)) {
      setDetailId(null);
    }
  }, [detailId, loading, tasks]);

  const handleCreate = (values) => mutate(() => createTask(values));
  const handleUpdate = (id, values) => mutate(() => updateTask(id, values));
  const handleMove = (id, status, position) =>
    mutateBoard(() => moveTask(id, { status, position }));
  const handleAddSubtask = (taskId, title) =>
    mutate(() => createSubtask(taskId, title));
  const handleToggleSubtask = (id, done) =>
    mutate(() => updateSubtask(id, { done }));
  const handleDeleteSubtask = (id) => mutate(() => deleteSubtask(id));
  const handleUpload = (taskId, file) => mutate(() => uploadAttachment(taskId, file));
  const handleDeleteAttachment = (taskId, attachmentId) =>
    mutate(() => deleteAttachment(taskId, attachmentId));

  function requestDelete(id) {
    const task = tasks.find((item) => item.id === id);
    setPendingDelete({ id, title: task ? task.title : `#${id}` });
  }

  async function confirmDelete() {
    const target = pendingDelete;
    setPendingDelete(null);
    setDetailId((current) => (current === target.id ? null : current));
    setError("");
    try {
      await deleteTask(target.id);
      await refresh();
      setUndone(target);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUndo() {
    const target = undone;
    setUndone(null);
    await mutateBoard(() => restoreTask(target.id));
  }

  const detailTask =
    detailId === null ? null : tasks.find((task) => task.id === detailId) ?? null;

  return (
    <main className="app">
      <header className="app__header">
        <h1>Tablero de Tareas</h1>
        <p>Organizá tus actividades, seguí su avance y sumá lo que necesites.</p>
      </header>

      <TaskForm onCreate={handleCreate} onUpload={handleUpload} />

      <div className="toolbar">
        <div className="toolbar__filters">
          <label className="toggle">
            <input
              type="checkbox"
              checked={overdueOnly}
              data-testid="overdue-filter"
              onChange={(event) => setOverdueOnly(event.target.checked)}
            />
            <span>Ver solo tareas vencidas</span>
          </label>

          <input
            type="search"
            className="filter__input"
            placeholder="Buscar por título o descripción"
            aria-label="Buscar tareas"
            value={query}
            data-testid="task-search"
            onChange={(event) => setQuery(event.target.value)}
          />

          <label className="filter">
            <span>Prioridad</span>
            <select
              value={priorityFilter}
              data-testid="priority-filter"
              onChange={(event) => setPriorityFilter(event.target.value)}
            >
              <option value="">Todas</option>
              {PRIORITY_FILTERS.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </label>

          <label className="filter">
            <span>Etiqueta</span>
            <select
              value={tagFilter}
              data-testid="tag-filter"
              onChange={(event) => setTagFilter(event.target.value)}
            >
              <option value="">Todas</option>
              {tagOptions.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>

          <label className="filter">
            <span>Orden</span>
            <select
              value={sort}
              data-testid="sort-select"
              onChange={(event) => setSort(event.target.value)}
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <span className="toolbar__summary" data-testid="task-count">
          {tasks.length} {tasks.length === 1 ? "tarea" : "tareas"}
        </span>
      </div>

      {error && (
        <p className="alert" role="alert" data-testid="app-error">
          {error}
        </p>
      )}

      {loading ? (
        <p className="loading">Cargando tareas...</p>
      ) : (
        <Board
          tasks={tasks}
          onMove={handleMove}
          onOpen={setDetailId}
          onDelete={requestDelete}
        />
      )}

      {detailTask && (
        <TaskDetailModal
          key={detailTask.id}
          task={detailTask}
          onClose={() => setDetailId(null)}
          onUpdate={handleUpdate}
          onAddSubtask={handleAddSubtask}
          onToggleSubtask={handleToggleSubtask}
          onDeleteSubtask={handleDeleteSubtask}
          onUpload={handleUpload}
          onDeleteAttachment={handleDeleteAttachment}
          onDelete={requestDelete}
        />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Eliminar tarea"
          message={`¿Querés eliminar "${pendingDelete.title}"? Podés deshacerlo durante unos segundos.`}
          confirmLabel="Eliminar"
          onConfirm={confirmDelete}
          onCancel={() => setPendingDelete(null)}
        />
      )}

      {undone && (
        <Toast
          message={`Eliminaste "${undone.title}".`}
          actionLabel="Deshacer"
          onAction={handleUndo}
          onClose={() => setUndone(null)}
        />
      )}
    </main>
  );
}
