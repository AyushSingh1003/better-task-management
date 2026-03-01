from __future__ import annotations
import pytest
from services.errors import ConflictError

def test_task_deletion_rules(client):
    # 1. Setup User and Project
    user = client.post("/users", json={"name": "User", "email": "deleter@example.com"}).get_json()
    project = client.post(
        "/projects", json={"name": "Project", "owner_id": user["id"]}
    ).get_json()

    # 2. Create a TODO task
    todo_task = client.post(
        "/tasks",
        json={"title": "Todo Task", "project_id": project["id"], "status": "todo"},
    ).get_json()

    # 3. Attempt to delete TODO task (Should FAIL)
    response = client.delete(f"/tasks/{todo_task['id']}")
    assert response.status_code == 409
    assert response.get_json()["error"] == "TASK_DELETE_FORBIDDEN"

    # 4. Create an IN_PROGRESS task (requires assignee)
    ip_task = client.post(
        "/tasks",
        json={
            "title": "IP Task", 
            "project_id": project["id"], 
            "status": "todo",
            "assigned_to": user["id"]
        },
    ).get_json()
    client.patch(f"/tasks/{ip_task['id']}/status", json={"status": "in_progress"})

    # 5. Attempt to delete IN_PROGRESS task (Should FAIL)
    response = client.delete(f"/tasks/{ip_task['id']}")
    assert response.status_code == 409
    assert response.get_json()["error"] == "TASK_DELETE_FORBIDDEN"

    # 6. Move task to DONE
    client.patch(f"/tasks/{ip_task['id']}/status", json={"status": "done"})

    # 7. Attempt to delete DONE task (Should SUCCEED)
    response = client.delete(f"/tasks/{ip_task['id']}")
    assert response.status_code == 200
    assert response.get_json()["success"] is True
