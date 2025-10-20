import json

from fastapi.encoders import jsonable_encoder

from models import UserBase, UserOut


class CUsersDb:
    _sUsersDbFile = "users.json"

    def __init__(self):
        self._lUsers: list[dict] | None = None

    def get_user(self, username: str) -> UserBase | None:
        """Return the user from the DB or None if the user is not found"""
        user = next(
            (user for user in self.lUsers if user["username"] == username), None
        )

        return UserBase(**user) if user is not None else None

    def get_users_out(self) -> list[UserOut]:
        """Return the list of users as UserOut"""
        lUsersOut = [
            UserOut(id=dUser["id"], username=dUser["username"]) for dUser in self.lUsers
        ]

        return lUsersOut

    def add_user(self, user: UserBase) -> None:
        """Add a new user to the DB"""
        user_json_encoded = jsonable_encoder(user)
        self.lUsers.append(user_json_encoded)
        self.store_users()

    def load_users(self) -> list[dict]:
        """Load the users from the DB"""
        self._lUsers: list[dict] = json.loads(open(self._sUsersDbFile).read())["users"]

        return self._lUsers

    def store_users(self):
        """Store the loaded users in the DB"""
        with open(self._sUsersDbFile, "w") as f:
            json.dump({"users": self._lUsers}, f, indent=4)

    @property
    def lUsers(self) -> list[dict]:
        if self._lUsers is None:
            self.load_users()
        return self._lUsers
