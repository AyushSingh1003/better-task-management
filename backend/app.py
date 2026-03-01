from __future__ import annotations

import logging
from typing import Type

from flask import Flask, jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config
from models import db
from routes import projects_bp, tasks_bp, users_bp
from services.errors import AppError

try:
    from flask_cors import CORS
except ModuleNotFoundError:  # pragma: no cover
    CORS = None


def create_app(config_class: Type[Config] = Config) -> Flask:
    app = Flask(__name__)
    if CORS is not None:
        CORS(app)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    db.init_app(app)

    with app.app_context():
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
            _enable_sqlite_foreign_keys(db.engine)
        db.create_all()

    app.register_blueprint(users_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.error, "message": error.message}), error.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(error: MarshmallowValidationError):
        logging.getLogger(__name__).warning("Validation failure: %s", error.messages)
        return (
            jsonify(
                {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request payload",
                }
            ),
            400,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logging.getLogger(__name__).exception("An unexpected error occurred: %s", error)
        return (
            jsonify(
                {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )

    return app


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=False)
