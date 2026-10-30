import { useEffect, useState } from "react";
import { createTask, deleteTask, getTasks, updateTaskStatus } from "./api.js";
import Board from "./components/Board.jsx";
import TaskForm from "./components/TaskForm.jsx";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getTasks()
      .then(setTasks)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(title) {
    setError("");
    const task = await createTask(title);
    setTasks((current) => [...current, task]);
  }

  async function handleMove(id, status) {
    setError("");
    try {
      const updated = await updateTaskStatus(id, status);
      setTasks((current) =>
        current.map((task) => (task.id === updated.id ? updated : task)),
      );
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    setError("");
    try {
      await deleteTask(id);
      setTasks((current) => current.filter((task) => task.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="app">
      <header className="app__header">
        <h1>Tablero de Tareas</h1>
        <p>Organizá tus actividades y seguí su avance.</p>
      </header>

      <TaskForm onCreate={handleCreate} />

      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className="loading">Cargando tareas...</p>
      ) : (
        <Board tasks={tasks} onMove={handleMove} onDelete={handleDelete} />
      )}
    </main>
  );
}
