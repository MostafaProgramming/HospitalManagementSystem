import datetime


class User:

    def __init__(self, userID, username, salt, password_hash, role, created_at=None, last_login_at = None, active = False):

        self.userID = userID
        self.username = username
        self.salt = salt
        self.password_hash = password_hash
        self.role = role

        self.created_at = created_at if created_at else str(datetime.datetime.now())
        self.last_login_at = last_login_at
        self.active = active


    def to_dict(self):

        return {
            "userID": self.userID,
            "username": self.username,
            "salt": self.salt,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at,
            "active": self.active
        }


    @staticmethod
    def from_dict(data):

        return User(
            data["userID"],
            data["username"],
            data["salt"],
            data["password_hash"],
            data["role"],
            data["created_at"],
            data["last_login_at"],
            data["active"]
        )
