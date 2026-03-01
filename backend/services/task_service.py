from __future__ import annotations

import logging
from typing import List, Optional

from models import Project, Task, TaskStatus, User, db
from services.errors import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


ALLOWED_STATUSES = {TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE}


class TaskService:
    @staticmethod
    def _get_task_or_404(task_id: int) -> Task:
        task = db.session.get(Task, task_id)
        if task is None:
            raise NotFoundError(message="Task not found", error="TASK_NOT_FOUND")
        return task

    @staticmethod
    def _status_from_string(status: str) -> TaskStatus:
        try:
            parsed = TaskStatus(status)
        except ValueError:
            logger.warning("Validation failure: invalid task status '%s'", status)
            raise ValidationError(
                message="Status must be one of: todo, in_progress, done",
                error="INVALID_STATUS",
            )

        if parsed not in ALLOWED_STATUSES:
            raise ValidationError(
                message="Status must be one of: todo, in_progress, done",
                error="INVALID_STATUS",
            )
        return parsed

    @staticmethod
    def create_task(
        title: str,
        description: Optional[str],
        project_id: int,
        assigned_to: Optional[int] = None,
        status: str = "todo",
    ) -> Task:
        project = db.session.get(Project, project_id)
        if project is None:
            raise NotFoundError(message="Project not found", error="PROJECT_NOT_FOUND")

        parsed_status = TaskService._status_from_string(status)

        if assigned_to is not None:
            assignee = db.session.get(User, assigned_to)
            if assignee is None:
                raise NotFoundError(
                    message="Assigned user not found", error="ASSIGNEE_NOT_FOUND"
                )

        if parsed_status == TaskStatus.IN_PROGRESS and assigned_to is None:
            raise ValidationError(
                message="Cannot move to in_progress without assignment",
                error="ASSIGNEE_REQUIRED",
            )

        if parsed_status == TaskStatus.DONE:
            raise ValidationError(
                message="Cannot move from todo directly to done",
                error="INVALID_STATUS_TRANSITION",
            )

        task = Task(
            title=title,
            description=description,
            status=parsed_status,
            project_id=project_id,
            assigned_to=assigned_to,
        )
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def list_tasks(project_id: Optional[int] = None) -> List[Task]:
        query = Task.query
        if project_id is not None:
            query = query.filter_by(project_id=project_id)
        return query.order_by(Task.id.asc()).all()

    @staticmethod
    def assign_task(task_id: int, assigned_to: int) -> Task:
        task = TaskService._get_task_or_404(task_id)

        assignee = db.session.get(User, assigned_to)
        if assignee is None:
            raise NotFoundError(message="Assigned user not found", error="ASSIGNEE_NOT_FOUND")

        with db.session.begin_nested():
            task.assigned_to = assigned_to

        db.session.commit()
        return task

    @staticmethod
    def update_status(task_id: int, status: str) -> Task:
        task = TaskService._get_task_or_404(task_id)
        new_status = TaskService._status_from_string(status)
        current = task.status

        if current == TaskStatus.TODO and new_status == TaskStatus.DONE:
            raise ValidationError(
                message="Cannot move from todo directly to done",
                error="INVALID_STATUS_TRANSITION",
            )

        if new_status == TaskStatus.IN_PROGRESS and task.assigned_to is None:
            raise ValidationError(
                message="Cannot move to in_progress without assignment",
                error="ASSIGNEE_REQUIRED",
            )

        with db.session.begin_nested():
            task.status = new_status

        db.session.commit()
        logger.info(
            "Task status transition task_id=%s from=%s to=%s",
            task.id,
            current.value,
            new_status.value,
        )
        return task

    @staticmethod
    def update_task_title(task_id: int, title: str) -> Task:
        task = TaskService._get_task_or_404(task_id)
        if task.status == TaskStatus.DONE:
            raise ConflictError(
                message="Cannot edit title after task is done",
                error="TITLE_LOCKED",
            )

        with db.session.begin_nested():
            task.title = title

        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id: int) -> None:
        task = TaskService._get_task_or_404(task_id)

        if task.status != TaskStatus.DONE:
            raise ConflictError(
                message=f"Cannot delete task with status {task.status.value.upper()}. Only DONE tasks can be deleted.",
                error="TASK_DELETE_FORBIDDEN",
            )

        db.session.delete(task)
        db.session.commit()
