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
