from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from config import TestConfig
from models import db


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(client, name: str = "User A", email: str = "a@example.com") -> dict:
    response = client.post("/users", json={"name": name, "email": email})
    return response.get_json()


def create_project(client, owner_id: int, name: str = "Project A") -> dict:
    response = client.post("/projects", json={"name": name, "owner_id": owner_id})
    return response.get_json()
