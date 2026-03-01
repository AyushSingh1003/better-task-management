from __future__ import annotations

from flask import Blueprint, jsonify, request

from schemas import CreateProjectSchema, ProjectSchema
from services import ProjectService

projects_bp = Blueprint("projects", __name__)

create_project_schema = CreateProjectSchema()
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


@projects_bp.post("/projects")
def create_project():
    payload = create_project_schema.load(request.get_json(force=True))
    project = ProjectService.create_project(
        name=payload["name"], owner_id=payload["owner_id"]
    )
    return jsonify(project_schema.dump(project)), 201


@projects_bp.get("/projects")
def list_projects():
    projects = ProjectService.list_projects()
    return jsonify(projects_schema.dump(projects)), 200


@projects_bp.delete("/projects/<int:project_id>")
def delete_project(project_id: int):
    ProjectService.delete_project(project_id)
    return jsonify({"success": True}), 200
