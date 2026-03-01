import { useEffect, useMemo, useState } from "react";
import {
  assignTask,
  createProject,
  createTask,
  createUser,
  deleteTask,
  deleteUser,
  extractApiError,
  fetchProjects,
  fetchTasks,
  fetchUsers,
  updateTaskStatus
} from "./api";

const STATUS_OPTIONS = ["todo", "in_progress", "done"];

function App() {
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [tasks, setTasks] = useState([]);

  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newProjectName, setNewProjectName] = useState("");
  const [projectOwnerId, setProjectOwnerId] = useState("");
  const [newTaskTitle, setNewTaskTitle] = useState("");

  const [error, setError] = useState("");

  const selectedProjectId = useMemo(
    () => (selectedProject ? Number(selectedProject) : null),
    [selectedProject]
  );

  useEffect(() => {
    initializeData();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadTasks(selectedProjectId);
    } else {
      setTasks([]);
    }
  }, [selectedProjectId]);

  useEffect(() => {
    if (error) {
      window.alert(error);
    }
  }, [error]);

  async function initializeData() {
    setError("");
    try {
      const [userData, projectData] = await Promise.all([fetchUsers(), fetchProjects()]);
      setUsers(userData);
      setProjects(projectData);

      if (userData.length > 0) {
        setProjectOwnerId(String(userData[0].id));
      }

      if (projectData.length > 0) {
        setSelectedProject(String(projectData[0].id));
      }
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Initialization failed", apiError);
    }
  }

  async function loadTasks(projectId) {
    setError("");
    try {
      const taskData = await fetchTasks(projectId);
      setTasks(taskData);
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Failed to load tasks", apiError);
    }
  }

  async function handleCreateUser(event) {
    event.preventDefault();
    if (!newUserName.trim() || !newUserEmail.trim()) {
      return;
    }

    setError("");
    try {
      const user = await createUser({
        name: newUserName.trim(),
        email: newUserEmail.trim()
      });
      console.info("User created", { userId: user.id });
      setNewUserName("");
      setNewUserEmail("");
      await initializeData();
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("User creation failed", apiError);
    }
  }

  async function handleDeleteUser(userId) {
    setError("");
    try {
      await deleteUser(userId);
      console.info("User deleted", { userId });
      await initializeData();
      if (selectedProjectId) {
        await loadTasks(selectedProjectId);
      }
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("User deletion failed", apiError);
    }
  }

  async function handleCreateProject(event) {
    event.preventDefault();
    if (!newProjectName.trim() || !projectOwnerId) {
      return;
    }

    setError("");
    try {
      const project = await createProject({
        name: newProjectName.trim(),
        owner_id: Number(projectOwnerId)
      });
      console.info("Project created", { projectId: project.id, ownerId: project.owner_id });
      setNewProjectName("");
      await initializeData();
      setSelectedProject(String(project.id));
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Project creation failed", apiError);
    }
  }

  async function handleCreateTask(event) {
    event.preventDefault();
    if (!selectedProjectId || !newTaskTitle.trim()) {
      return;
    }

    setError("");
    try {
      const task = await createTask({
        title: newTaskTitle.trim(),
        project_id: selectedProjectId,
        status: "todo"
      });
      console.info("Task created", { taskId: task.id, projectId: selectedProjectId });
      setNewTaskTitle("");
      await loadTasks(selectedProjectId);
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Task creation failed", apiError);
    }
  }

  async function handleAssignTask(taskId, assignedTo) {
    setError("");
    try {
      await assignTask(taskId, Number(assignedTo));
      console.info("Task assigned", { taskId, assignedTo: Number(assignedTo) });
      await loadTasks(selectedProjectId);
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Task assignment failed", apiError);
    }
  }

  async function handleStatusUpdate(taskId, status) {
    setError("");
    try {
      await updateTaskStatus(taskId, status);
      console.info("Status transition", { taskId, status });
      await loadTasks(selectedProjectId);
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Status update failed", apiError);
    }
  }

  async function handleDeleteTask(taskId) {
    setError("");
    try {
      await deleteTask(taskId);
      console.info("Task deleted", { taskId });
      await loadTasks(selectedProjectId);
    } catch (apiError) {
      setError(extractApiError(apiError));
      console.error("Task deletion failed", apiError);
    }
  }

  return (
    <main className="container">
      <h1>Task Management</h1>
      {error && <p className="error">{error}</p>}

      <section className="panel">
        <h2>Create User</h2>
        <form onSubmit={handleCreateUser}>
          <input
            placeholder="Name"
            value={newUserName}
            onChange={(event) => setNewUserName(event.target.value)}
          />
          <input
            placeholder="Email"
            value={newUserEmail}
            onChange={(event) => setNewUserEmail(event.target.value)}
          />
          <button type="submit">Create User</button>
        </form>
        <div className="user-list">
          {users.map((user) => (
            <div key={user.id} className="user-row">
              <span>
                {user.name} ({user.email})
              </span>
              <button type="button" onClick={() => handleDeleteUser(user.id)}>
                Delete User
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Create Project</h2>
        <form onSubmit={handleCreateProject}>
          <input
            placeholder="Project name"
            value={newProjectName}
            onChange={(event) => setNewProjectName(event.target.value)}
          />
          <select
            value={projectOwnerId}
            onChange={(event) => setProjectOwnerId(event.target.value)}
          >
            <option value="">Select owner</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} ({user.email})
              </option>
            ))}
          </select>
          <button type="submit">Create Project</button>
        </form>
      </section>

      <section className="panel">
        <h2>Projects</h2>
        <select
          value={selectedProject}
          onChange={(event) => setSelectedProject(event.target.value)}
        >
          <option value="">Select project</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </section>

      <section className="panel">
        <h2>Create Task</h2>
        <form onSubmit={handleCreateTask}>
          <input
            placeholder="Task title"
            value={newTaskTitle}
            onChange={(event) => setNewTaskTitle(event.target.value)}
          />
          <button type="submit" disabled={!selectedProjectId}>
            Create Task
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Tasks</h2>
        {tasks.length === 0 && <p>No tasks found.</p>}
        {tasks.map((task) => (
          <article key={task.id} className="task-row">
            <div>
              <strong>{task.title}</strong>
              <p>Status: {task.status}</p>
              <p>Assigned to: {task.assigned_to ?? "unassigned"}</p>
            </div>
            <div className="actions">
              <select
                value={task.assigned_to ?? ""}
                onChange={(event) => {
                  if (event.target.value) {
                    handleAssignTask(task.id, event.target.value);
                  }
                }}
              >
                <option value="">Assign user</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.name}
                  </option>
                ))}
              </select>
              <select
                value={task.status}
                onChange={(event) => handleStatusUpdate(task.id, event.target.value)}
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
              <button type="button" onClick={() => handleDeleteTask(task.id)}>
                Delete Task
              </button>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

export default App;
