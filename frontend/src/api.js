import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000"
});

export async function fetchProjects() {
  const response = await api.get("/projects");
  return response.data;
}

export async function fetchUsers() {
  const response = await api.get("/users");
  return response.data;
}

export async function createUser(payload) {
  const response = await api.post("/users", payload);
  return response.data;
}

export async function deleteUser(userId) {
  const response = await api.delete(`/users/${userId}`);
  return response.data;
}

export async function createProject(payload) {
  const response = await api.post("/projects", payload);
  return response.data;
}

export async function fetchTasks(projectId) {
  const response = await api.get("/tasks", {
    params: projectId ? { project_id: projectId } : {}
  });
  return response.data;
}

export async function createTask(payload) {
  const response = await api.post("/tasks", payload);
  return response.data;
}

export async function updateTaskStatus(taskId, status) {
  const response = await api.patch(`/tasks/${taskId}/status`, { status });
  return response.data;
}

export async function deleteTask(taskId) {
  const response = await api.delete(`/tasks/${taskId}`);
  return response.data;
}

export async function assignTask(taskId, assignedTo) {
  const response = await api.patch(`/tasks/${taskId}/assign`, {
    assigned_to: assignedTo
  });
  return response.data;
}

export function extractApiError(error) {
  if (error.response?.data?.message) {
    return `${error.response.data.error}: ${error.response.data.message}`;
  }
  return "Unexpected error while calling API";
}
