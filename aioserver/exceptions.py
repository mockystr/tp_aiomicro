class BasicApiException(Exception):
    pass


class UserExists(BasicApiException):
    def __init__(self):
        super().__init__("User already exists")


class ExpiredToken(BasicApiException):
    def __init__(self):
        super().__init__("Token is expired. Login again, please")
