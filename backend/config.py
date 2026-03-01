from __future__ import annotations

import os


class Config:
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "sqlite:///task_management.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    TESTING: bool = False


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    TESTING: bool = True
