const API_URL = import.meta.env.VITE_API_URL ?? "/api";

async function request(path, { body, ...options } = {}) {
  const headers = { ...(options.headers ?? {}) };
  if (body !== undefined && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, body, headers });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function readError(response) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg.replace(/^Value error,\s*/i, "");
    }
  } catch {
    // La respuesta no traía un cuerpo JSON legible.
  }
  return `Error ${response.status}`;
}

export function getTasks(options = {}) {
  const { overdue = false, q, priority, tag, sort } =
    typeof options === "boolean" ? { overdue: options } : options;

  const params = new URLSearchParams();
  if (overdue) {
    params.set("overdue", "true");
  }
  if (q) {
    params.set("q", q);
  }
  if (priority) {
    params.set("priority", priority);
  }
  if (tag) {
    params.set("tag", tag);
  }
  if (sort) {
    params.set("sort", sort);
  }

  const query = params.toString();
  return request(`/tasks${query ? `?${query}` : ""}`);
}

export function getTags() {
  return request("/tags");
}

export function createTask({
  title,
  description,
  dueDate,
  priority,
  assignee,
  subtasks,
  tags,
  links,
}) {
  return request("/tasks", {
    method: "POST",
    body: JSON.stringify({
      title,
      description,
      due_date: dueDate || null,
      priority: priority ?? "Media",
      assignee,
      subtasks,
      tags,
      links,
    }),
  });
}

export function updateTask(id, values) {
  const body = {};
  if ("title" in values) {
    body.title = values.title;
  }
  if ("description" in values) {
    body.description = values.description;
  }
  if ("dueDate" in values) {
    body.due_date = values.dueDate || null;
  }
  if ("priority" in values) {
    body.priority = values.priority;
  }
  if ("assignee" in values) {
    body.assignee = values.assignee;
  }
  if ("tags" in values) {
    body.tags = values.tags;
  }
  if ("links" in values) {
    body.links = values.links;
  }

  return request(`/tasks/${id}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function moveTask(id, { status, position }) {
  return request(`/tasks/${id}/move`, {
    method: "PATCH",
    body: JSON.stringify({ status, position }),
  });
}

export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: "DELETE" });
}

export function restoreTask(id) {
  return request(`/tasks/${id}/restore`, { method: "POST" });
}

export function createSubtask(taskId, title) {
  return request(`/tasks/${taskId}/subtasks`, {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export function updateSubtask(id, { title, done }) {
  return request(`/subtasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title, done }),
  });
}

export function deleteSubtask(id) {
  return request(`/subtasks/${id}`, { method: "DELETE" });
}

export function uploadAttachment(taskId, file) {
  const body = new FormData();
  body.append("file", file);
  return request(`/tasks/${taskId}/attachments`, { method: "POST", body });
}

export function deleteAttachment(taskId, attachmentId) {
  return request(`/tasks/${taskId}/attachments/${attachmentId}`, {
    method: "DELETE",
  });
}

export function attachmentUrl(taskId, attachmentId) {
  return `${API_URL}/tasks/${taskId}/attachments/${attachmentId}`;
}
