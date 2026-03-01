from __future__ import annotations


def test_delete_task_valid_when_not_done(client):
    user = client.post("/users", json={"name": "Owner", "email": "owner1@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()
    task = client.post(
        "/tasks", json={"title": "Task", "project_id": project["id"], "status": "todo"}
    ).get_json()

    response = client.delete(f"/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_delete_task_invalid_when_done(client):
    owner = client.post("/users", json={"name": "Owner", "email": "owner2@example.com"}).get_json()
    assignee = client.post(
        "/users", json={"name": "Assignee", "email": "assignee2@example.com"}
    ).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": owner["id"]}
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

    response = client.delete(f"/tasks/{task['id']}")

    assert response.status_code == 409
    assert response.get_json()["error"] == "DONE_TASK_DELETE_FORBIDDEN"


def test_delete_user_valid_when_no_owned_projects_or_assigned_tasks(client):
    user = client.post("/users", json={"name": "Delete Me", "email": "deleteme@example.com"}).get_json()

    response = client.delete(f"/users/{user['id']}")

    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_delete_user_invalid_when_user_owns_projects(client):
    owner = client.post("/users", json={"name": "Owner", "email": "owner3@example.com"}).get_json()
    client.post("/projects", json={"name": "Project", "owner_id": owner["id"]})

    response = client.delete(f"/users/{owner['id']}")

    assert response.status_code == 409
    assert response.get_json()["error"] == "USER_OWNS_PROJECTS"


def test_delete_user_invalid_when_user_has_assigned_tasks(client):
    owner = client.post("/users", json={"name": "Owner", "email": "owner4@example.com"}).get_json()
    assignee = client.post(
        "/users", json={"name": "Assignee", "email": "assignee4@example.com"}
    ).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": owner["id"]}
    ).get_json()
    client.post(
        "/tasks",
        json={
            "title": "Task",
            "project_id": project["id"],
            "status": "todo",
            "assigned_to": assignee["id"],
        },
    )

    response = client.delete(f"/users/{assignee['id']}")

    assert response.status_code == 409
    assert response.get_json()["error"] == "USER_HAS_ASSIGNED_TASKS"


def test_delete_user_invalid_when_not_found(client):
    response = client.delete("/users/99999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "USER_NOT_FOUND"
