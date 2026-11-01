import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
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
import TaskForm from "./components/TaskForm.jsx";
import Toast from "./components/Toast.jsx";

// AUD-17: el detalle es el componente más pesado y sólo se usa bajo interacción,
// por lo que se carga de forma diferida (code splitting).
const TaskDetailModal = lazy(() => import("./components/TaskDetailModal.jsx"));

const UNDO_WINDOW_MS = 7000;
const SUCCESS_WINDOW_MS = 3500;
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
  const [loaded, setLoaded] = useState(false);
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
  const [toast, setToast] = useState(null);

  // AUD-19: se conserva el id de la última petición para descartar respuestas
  // obsoletas y evitar condiciones de carrera al cambiar de filtro.
  const requestRef = useRef(0);
  const tasksRef = useRef(tasks);

  useEffect(() => {
    tasksRef.current = tasks;
  }, [tasks]);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  /** Muestra un aviso breve; `duration` y `actionLabel` permiten reutilizar el
   * mismo componente para el "Deshacer" y para las confirmaciones de éxito. */
  const showToast = useCallback((message, options = {}) => {
    setToast({ message, duration: SUCCESS_WINDOW_MS, ...options });
  }, []);

  useEffect(() => {
    if (!toast) {
      return undefined;
    }
    const timer = setTimeout(
      () => setToast(null),
      toast.duration ?? SUCCESS_WINDOW_MS,
    );
    return () => clearTimeout(timer);
  }, [toast]);

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
    const requestId = requestRef.current + 1;
    requestRef.current = requestId;
    if (!silent) {
      setLoading(true);
    }
    try {
      // AUD-22: si el catálogo de etiquetas falla, el tablero se muestra igual.
      const [list, names] = await Promise.all([
        getTasks(filters),
        getTags().catch(() => null),
      ]);
      if (requestId !== requestRef.current) {
        return;
      }
      setTasks(list);
      if (names) {
        setTagOptions(names);
      }
      setError("");
    } catch (err) {
      if (requestId !== requestRef.current) {
        return;
      }
      setError(err.message);
    } finally {
      if (requestId === requestRef.current) {
        setLoaded(true);
        if (!silent) {
          setLoading(false);
        }
      }
    }
  }, []);

  useEffect(() => {
    load(params);
  }, [load, params]);

  const refresh = useCallback(() => load(params, { silent: true }), [load, params]);

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
  const mutateBoard = useCallback(
    async (action) => {
      setError("");
      try {
        await mutate(action);
      } catch (err) {
        setError(err.message);
      }
    },
    [mutate],
  );

  useEffect(() => {
    if (detailId !== null && !loading && !tasks.some((task) => task.id === detailId)) {
      setDetailId(null);
    }
  }, [detailId, loading, tasks]);

  // AUD-27: handlers estables para no invalidar la memoización de los hijos.
  const handleCreate = useCallback(
    async (values) => {
      const created = await mutate(() => createTask(values));
      // AUD-36: confirmación explícita de éxito.
      showToast("Tarea creada correctamente.");
      return created;
    },
    [mutate, showToast],
  );

  const handleUpdate = useCallback(
    async (id, values) => {
      const updated = await mutate(() => updateTask(id, values));
      showToast("Cambios guardados.");
      return updated;
    },
    [mutate, showToast],
  );

  const handleMove = useCallback(
    (id, status, position) => mutateBoard(() => moveTask(id, { status, position })),
    [mutateBoard],
  );
  const handleAddSubtask = useCallback(
    (taskId, title) => mutate(() => createSubtask(taskId, title)),
    [mutate],
  );
  const handleToggleSubtask = useCallback(
    (id, done) => mutate(() => updateSubtask(id, { done })),
    [mutate],
  );
  const handleDeleteSubtask = useCallback(
    (id) => mutate(() => deleteSubtask(id)),
    [mutate],
  );
  const handleUpload = useCallback(
    (taskId, file) => mutate(() => uploadAttachment(taskId, file)),
    [mutate],
  );
  const handleDeleteAttachment = useCallback(
    (taskId, attachmentId) => mutate(() => deleteAttachment(taskId, attachmentId)),
    [mutate],
  );

  const requestDelete = useCallback((id) => {
    const task = tasksRef.current.find((item) => item.id === id);
    setPendingDelete({ id, title: task ? task.title : `#${id}` });
  }, []);

  const openDetail = useCallback((id) => setDetailId(id), []);
  const closeDetail = useCallback(() => setDetailId(null), []);

  const confirmDelete = useCallback(async () => {
    const target = pendingDelete;
    if (!target) {
      return;
    }
    setPendingDelete(null);
    setDetailId((current) => (current === target.id ? null : current));
    setError("");
    try {
      await deleteTask(target.id);
      await refresh();
      showToast(`Eliminaste "${target.title}".`, {
        actionLabel: "Deshacer",
        duration: UNDO_WINDOW_MS,
        onAction: async () => {
          setToast(null);
          await mutateBoard(() => restoreTask(target.id));
        },
      });
    } catch (err) {
      setError(err.message);
    }
  }, [pendingDelete, refresh, showToast, mutateBoard]);

  const detailTask =
    detailId === null ? null : tasks.find((task) => task.id === detailId) ?? null;

  return (
    <main className="app">
      <header className="app__header">
        <h1>Tablero de Tareas</h1>
        <p>Organizá tus actividades, seguí su avance y sumá lo que necesites.</p>
      </header>

      <TaskForm
        onCreate={handleCreate}
        onUpload={handleUpload}
        tagOptions={tagOptions}
      />

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

      {!loaded ? (
        // AUD-12: la carga inicial se anuncia a los lectores de pantalla.
        <p className="loading" role="status" aria-live="polite">
          Cargando tareas...
        </p>
      ) : (
        // AUD-30: el tablero permanece montado; la recarga se superpone sin
        // reemplazarlo (sin salto de layout).
        <div className="board-area" aria-busy={loading}>
          {loading && (
            <div className="board-overlay">
              <span className="board-overlay__chip" role="status" aria-live="polite">
                Actualizando tareas...
              </span>
            </div>
          )}
          <Board
            tasks={tasks}
            onMove={handleMove}
            onOpen={openDetail}
            onDelete={requestDelete}
          />
        </div>
      )}

      {detailTask && (
        <Suspense fallback={null}>
          <TaskDetailModal
            key={detailTask.id}
            task={detailTask}
            onClose={closeDetail}
            onNotify={showToast}
            onMove={handleMove}
            onUpdate={handleUpdate}
            onAddSubtask={handleAddSubtask}
            onToggleSubtask={handleToggleSubtask}
            onDeleteSubtask={handleDeleteSubtask}
            onUpload={handleUpload}
            onDeleteAttachment={handleDeleteAttachment}
            onDelete={requestDelete}
          />
        </Suspense>
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

      {toast && (
        <Toast
          message={toast.message}
          actionLabel={toast.actionLabel}
          onAction={toast.onAction}
          onClose={() => setToast(null)}
        />
      )}
    </main>
  );
}
