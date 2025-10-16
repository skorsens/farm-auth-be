from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """User info stored in the DB"""

    id: str = Field(...)
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)


class UserIn(BaseModel):
    """User info required for user registration or login"""

    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)


class UserOut(BaseModel):
    """User info that is displayed in the UI, so that it does not contain the user password"""

    id: str = Field(...)
    username: str = Field(..., min_length=3, max_length=15)


class UsersList(BaseModel):
    """The list of users displayed in the UI"""

    users: list[UserOut]
