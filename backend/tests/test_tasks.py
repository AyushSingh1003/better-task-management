from __future__ import annotations

from services import TaskService


def test_invalid_status_transition_todo_to_done(client):
    user = client.post("/users", json={"name": "User", "email": "user1@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    task = client.post(
        "/tasks",
        json={"title": "Task", "project_id": project["id"], "status": "todo"},
    ).get_json()

    response = client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "INVALID_STATUS_TRANSITION"


def test_cannot_skip_lifecycle_steps_on_create(client):
    user = client.post("/users", json={"name": "User", "email": "user2@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    response = client.post(
        "/tasks",
        json={"title": "Task", "project_id": project["id"], "status": "done"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "INVALID_STATUS_TRANSITION"


def test_cannot_move_to_in_progress_without_assignment(client):
    user = client.post("/users", json={"name": "User", "email": "user3@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    task = client.post(
        "/tasks",
        json={"title": "Task", "project_id": project["id"], "status": "todo"},
    ).get_json()

    response = client.patch(
        f"/tasks/{task['id']}/status", json={"status": "in_progress"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "ASSIGNEE_REQUIRED"


def test_cannot_delete_project_with_tasks(client):
    user = client.post("/users", json={"name": "User", "email": "user4@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    client.post(
        "/tasks",
        json={"title": "Task", "project_id": project["id"], "status": "todo"},
    )

    response = client.delete(f"/projects/{project['id']}")

    assert response.status_code == 409
    assert response.get_json()["error"] == "PROJECT_HAS_TASKS"


def test_cannot_modify_title_after_done(client):
    user = client.post("/users", json={"name": "User", "email": "user5@example.com"}).get_json()
    assignee = client.post(
        "/users", json={"name": "Assignee", "email": "assignee@example.com"}
    ).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    task = client.post(
        "/tasks",
        json={
            "title": "Task",
            "project_id": project["id"],
            "status": "todo",
            "assigned_to": assignee["id"],
        },
    ).get_json()

    client.patch(f"/tasks/{task['id']}/status", json={"status": "in_progress"})
    client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})

    # Title updates are service-level and must still enforce domain rules.
    response_error = None
    try:
        TaskService.update_task_title(task["id"], "New title")
    except Exception as exc:
        response_error = exc

    assert response_error is not None
    assert getattr(response_error, "error", None) == "TITLE_LOCKED"


def test_invalid_enum_rejection(client):
    user = client.post("/users", json={"name": "User", "email": "user6@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    response = client.post(
        "/tasks",
        json={"title": "Task", "project_id": project["id"], "status": "bogus"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"
