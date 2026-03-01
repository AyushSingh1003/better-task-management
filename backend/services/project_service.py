from __future__ import annotations

from typing import List

from models import Project, Task, User, db
from services.errors import ConflictError, NotFoundError


class ProjectService:
    @staticmethod
    def create_project(name: str, owner_id: int) -> Project:
        owner = db.session.get(User, owner_id)
        if owner is None:
            raise NotFoundError(message="Owner user not found", error="OWNER_NOT_FOUND")

        project = Project(name=name, owner_id=owner_id)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def list_projects() -> List[Project]:
        return Project.query.order_by(Project.id.asc()).all()

    @staticmethod
    def delete_project(project_id: int) -> None:
        project = db.session.get(Project, project_id)
        if project is None:
            raise NotFoundError(message="Project not found", error="PROJECT_NOT_FOUND")

        task_count = Task.query.filter_by(project_id=project_id).count()
        if task_count > 0:
            raise ConflictError(
                message="Cannot delete project with existing tasks",
                error="PROJECT_HAS_TASKS",
            )

        db.session.delete(project)
        db.session.commit()
