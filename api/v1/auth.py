from datetime import timedelta
from typing import Annotated, Any
from sqlmodel import select, delete

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
from schemas.user import UserCreate, UserCreateInternal, UserRead
from core.schemas import Token
from core.config import settings
from starlette.exceptions import HTTPException
from core.security import authenticate_user, create_access_token, get_password_hash, create_refresh_token
from core.config import settings
from core.db import SessionDep
from core.exceptions.http_exceptions import UnauthorizedException, DuplicateValueException, ForbiddenException, NotFoundException

router = APIRouter()

@router.post("/sign-in", response_model=Token)
async def sign_in_user(
    # response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=session)
    if not user:
        raise UnauthorizedException("Wrong username, email or password.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    # refresh_token = await create_refresh_token(data={"sub": user["username"]})
    # max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # response.set_cookie(
    #     key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age
    # )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/sign-up", response_model=UserRead, status_code=201)
async def sign_up_user(
    request: Request,
    user: UserCreate,
    session: SessionDep,
) -> dict[str, Any]:
    await session.execute(
        delete(User).where(User.email == user.email)
    )
    email_exists = await session.execute(
        select(User.id).where(User.email == user.email)
    )
    if email_exists.scalar_one_or_none():
        raise DuplicateValueException("Email is already registered")

    username_exists = await session.execute(
        select(User.id).where(User.username == user.username)
    )
    if username_exists.scalar_one_or_none():
        raise DuplicateValueException("Username not available")

    db_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=get_password_hash(user.password),
    )

    session.add(db_user)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(db_user)

    return db_user