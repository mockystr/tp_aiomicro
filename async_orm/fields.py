import datetime
from exceptions import IntegrityError


class Field:
    def __init__(self, f_type, required=False, default=None):
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None and not self.required:
            return None
        return self.f_type(value)


class IntField(Field):
    def __init__(self, required=False, default=None):
        super().__init__(int, required, default)


class StringField(Field):
    def __init__(self, required=False, default=None):
        super().__init__(str, required, default)


class DateField(Field):
    def __init__(self, required=False, default=None):
        super().__init__(datetime.datetime, required, default)

    def validate(self, value):
        if value is None and not self.required:
            return None
        elif isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, (list, tuple)):
            return datetime.datetime(*value)
        elif isinstance(value, dict):
            return datetime.datetime(**value)
        else:
            raise IntegrityError("wrong data insert to {} ({})".format(self.f_type, value))


class FloatField(Field):
    def __init__(self, required=False, default=None):
        super().__init__(float, required, default)


class BooleanField(Field):
    def __init__(self, required=False, default=None):
        super().__init__(bool, required, default)
