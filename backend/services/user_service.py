from __future__ import annotations

from typing import List

from sqlalchemy.exc import IntegrityError

from models import Project, Task, User, db
from services.errors import ConflictError, NotFoundError


class UserService:
    @staticmethod
    def create_user(name: str, email: str) -> User:
        user = User(name=name, email=email)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(message="Email already exists", error="EMAIL_EXISTS")
        return user

    @staticmethod
    def list_users() -> List[User]:
        return User.query.order_by(User.id.asc()).all()

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = db.session.get(User, user_id)
        if user is None:
            raise NotFoundError(message="User not found", error="USER_NOT_FOUND")

        owns_projects = Project.query.filter_by(owner_id=user_id).count() > 0
        if owns_projects:
            raise ConflictError(
                message="Cannot delete user who owns projects",
                error="USER_OWNS_PROJECTS",
            )

        has_assigned_tasks = Task.query.filter_by(assigned_to=user_id).count() > 0
        if has_assigned_tasks:
            raise ConflictError(
                message="Cannot delete user with assigned tasks",
                error="USER_HAS_ASSIGNED_TASKS",
            )

        db.session.delete(user)
        db.session.commit()
