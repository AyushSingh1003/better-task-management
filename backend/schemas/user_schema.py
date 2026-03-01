from __future__ import annotations

from marshmallow import Schema, fields


class CreateUserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
