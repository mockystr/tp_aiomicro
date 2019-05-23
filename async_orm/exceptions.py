class MultipleObjectsReturned(Exception):
    pass


class DoesNotExist(Exception):
    pass


class DeleteError(Exception):
    pass


class DuplicateKeyConstraint(Exception):
    pass


class OrderByFieldError(Exception):
    pass


class IntegrityError(Exception):
    pass


class ParentClashError(Exception):
    pass


class FieldLookupError(Exception):
    pass
