from __future__ import annotations

from marshmallow import Schema, fields


class CreateProjectSchema(Schema):
    name = fields.String(required=True)
    owner_id = fields.Integer(required=True)


class ProjectSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    owner_id = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)
