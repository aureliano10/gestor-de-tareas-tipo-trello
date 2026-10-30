import { useCallback, useEffect, useState } from "react";
import {
  createSubtask,
  createTask,
  deleteAttachment,
  deleteSubtask,
  deleteTask,
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

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [detailId, setDetailId] = useState(null);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [undone, setUndone] = useState(null);

  const load = useCallback(async (overdue, { silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
    }
    try {
      setTasks(await getTasks(overdue));
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
    load(overdueOnly);
  }, [load, overdueOnly]);

  const refresh = useCallback(
    () => load(overdueOnly, { silent: true }),
    [load, overdueOnly],
  );

  /**
   * Ejecuta una acción y recarga el tablero.
   * Los errores se propagan para que los formularios y el modal los muestren.
   */
  const mutate = useCallback(
    async (action) => {
      await action();
      await refresh();
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

      <TaskForm onCreate={handleCreate} />

      <div className="toolbar">
        <label className="toggle">
          <input
            type="checkbox"
            checked={overdueOnly}
            data-testid="overdue-filter"
            onChange={(event) => setOverdueOnly(event.target.checked)}
          />
          <span>Ver solo tareas vencidas</span>
        </label>
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
