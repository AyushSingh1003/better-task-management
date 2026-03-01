from __future__ import annotations

from flask import Blueprint, jsonify, request

from schemas import CreateUserSchema, UserSchema
from services import UserService

users_bp = Blueprint("users", __name__)

create_user_schema = CreateUserSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@users_bp.post("/users")
def create_user():
    payload = create_user_schema.load(request.get_json(force=True))
    user = UserService.create_user(name=payload["name"], email=payload["email"])
    return jsonify(user_schema.dump(user)), 201


@users_bp.get("/users")
def list_users():
    users = UserService.list_users()
    return jsonify(users_schema.dump(users)), 200


@users_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    UserService.delete_user(user_id)
    return jsonify({"success": True}), 200
