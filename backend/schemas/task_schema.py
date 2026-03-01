from __future__ import annotations

from marshmallow import Schema, fields, validate


STATUS_VALUES = ["todo", "in_progress", "done"]


class CreateTaskSchema(Schema):
    title = fields.String(required=True)
    description = fields.String(required=False, allow_none=True)
    status = fields.String(required=False, load_default="todo", validate=validate.OneOf(STATUS_VALUES))
    project_id = fields.Integer(required=True)
    assigned_to = fields.Integer(required=False, allow_none=True)


class AssignTaskSchema(Schema):
    assigned_to = fields.Integer(required=True)


class UpdateTaskStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(STATUS_VALUES))


class TaskSchema(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    status = fields.Function(lambda obj: obj.status.value)
    project_id = fields.Integer(required=True)
    assigned_to = fields.Integer(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
