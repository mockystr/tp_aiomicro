class UserExists(Exception):
    def __init__(self):
        super().__init__("User already exists")


class ExpiredToken(Exception):
    def __init__(self):
        super().__init__("Token is expired. Login again, please")
