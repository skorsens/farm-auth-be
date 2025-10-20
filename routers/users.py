import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from authentication import AuthHandler
from models import UserBase, UserIn, UserOut, UsersList
from users_db import CUsersDb


router = APIRouter()

auth_handler = AuthHandler()
users_db = CUsersDb()


@router.post("/register", response_description="Register user")
async def register(request: Request, newUser: UserIn = Body(...)) -> UserBase:
    """Register a new user in the database"""
    user = users_db.get_user(newUser.username)

    if user:
        raise HTTPException(status_code=409, detail="Username already taken")

    hashed_password = auth_handler.get_password_hash(newUser.password)

    newUserBase = UserBase(
        id=str(uuid.uuid4()), username=newUser.username, password=hashed_password
    )

    users_db.add_user(newUserBase)

    return newUserBase


@router.post("/login", response_description="Login user")
async def login(request: Request, loginUser: UserIn = Body(...)) -> JSONResponse:
    """Login a registered user"""
    user = users_db.get_user(loginUser.username)

    if (user is None) or (
        not auth_handler.verify_password(loginUser.password, user.password)
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")

    token = auth_handler.encode_token(user.id, user.username)
    response = JSONResponse(content={"token": token})

    return response


@router.get("/list", response_description="List all users")
async def list_users(
    request: Request, user_data=Depends(auth_handler.auth_wrapper)
) -> UsersList:
    """Get the list of the users for an authenticated user

        Test using httpie:
    http 127.0.0.1:8000/users/login username="marko-1" password="marko-1-1234"
    ...
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjA5NzY4MTIsImlhdCI6MTc2MDk3NTAxMiwic3ViIjoiOWRlOTg3OTQtYWY0My00YjM0LTg1OWYtMTBmYjQ0YWQyMDAwOm1hcmtvLTEifQ.1GszX2tAUuDyy1DQkD9VDE2okL5k0U3dtrr4vkLrnN8"
    }

    GET 127.0.0.1:8000/users/list "Authorization:Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjA5NzY4MTIsImlhdCI6MTc2MDk3NTAxMiwic3ViIjoiOWRlOTg3OTQtYWY0My00YjM0LTg1OWYtMTBmYjQ0YWQyMDAwOm1hcmtvLTEifQ.1GszX2tAUuDyy1DQkD9VDE2okL5k0U3dtrr4vkLrnN8"
    ...
    """
    users = users_db.get_users_out()
    return UsersList(users=users)
