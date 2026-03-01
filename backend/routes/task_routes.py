from __future__ import annotations

from flask import Blueprint, jsonify, request

from schemas import AssignTaskSchema, CreateTaskSchema, TaskSchema, UpdateTaskStatusSchema
from services import TaskService

tasks_bp = Blueprint("tasks", __name__)

create_task_schema = CreateTaskSchema()
assign_task_schema = AssignTaskSchema()
update_status_schema = UpdateTaskStatusSchema()
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@tasks_bp.post("/tasks")
def create_task():
    payload = create_task_schema.load(request.get_json(force=True))
    task = TaskService.create_task(
        title=payload["title"],
        description=payload.get("description"),
        status=payload.get("status", "todo"),
        project_id=payload["project_id"],
        assigned_to=payload.get("assigned_to"),
    )
    return jsonify(task_schema.dump(task)), 201


@tasks_bp.get("/tasks")
def list_tasks():
    project_id = request.args.get("project_id", type=int)
    tasks = TaskService.list_tasks(project_id=project_id)
    return jsonify(tasks_schema.dump(tasks)), 200


@tasks_bp.patch("/tasks/<int:task_id>/assign")
def assign_task(task_id: int):
    payload = assign_task_schema.load(request.get_json(force=True))
    task = TaskService.assign_task(task_id=task_id, assigned_to=payload["assigned_to"])
    return jsonify(task_schema.dump(task)), 200


@tasks_bp.patch("/tasks/<int:task_id>/status")
def update_task_status(task_id: int):
    payload = update_status_schema.load(request.get_json(force=True))
    task = TaskService.update_status(task_id=task_id, status=payload["status"])
    return jsonify(task_schema.dump(task)), 200


@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    TaskService.delete_task(task_id)
    return jsonify({"success": True}), 200
