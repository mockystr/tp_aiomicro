from marshmallow import Schema, fields, ValidationError
from validate_email import validate_email


def validate_limit_search(n):
    if n > 100:
        raise ValidationError("Limit must be less than 100")


def validate_password_signup(password):
    if len(password) <= 4:
        raise ValueError("Password must be more than 4 characters.")


class SearchViewSchema(Schema):
    q = fields.Str(required=True)
    limit = fields.Integer(default=0, validate=validate_limit_search, required=False)
    offset = fields.Integer(default=0, required=False)


class SignupViewSchema(Schema):
    email = fields.Str(required=True, validate=validate_email)
    password = fields.Str(required=True, validate=validate_password_signup)
    name = fields.Str()


class LoginViewSchema(Schema):
    email = fields.Str(required=True, validate=validate_email)
    password = fields.Str(required=True, validate=validate_password_signup)


class IndexViewSchema(Schema):
    https = fields.Integer(required=True)
    domain = fields.Str(required=True)
