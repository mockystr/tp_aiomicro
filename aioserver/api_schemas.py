from marshmallow import Schema, fields, ValidationError


def validate_limit_search(n):
    if n > 100:
        raise ValidationError("Limit must be less than 100")


class SearchViewSchema(Schema):
    q = fields.Str(required=True)
    limit = fields.Integer(default=0, validate=validate_limit_search)
    offset = fields.Integer(default=0)
