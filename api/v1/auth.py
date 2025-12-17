from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import User, UserCreate, UserCreateInternal, UserRead
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


@router.post("/sign-up", response_model=User)
def sign_up_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(
        {
            **user.model_dump(exclude="password"),
            "password": get_password_hash(user.password),
        }
    )
    print("db_user", db_user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# from crud.crud_users import crud_users

# @router.post("/sign-up", response_model=UserRead, status_code=201)
# async def write_user(
#     request: Request, user: UserCreate, db: SessionDep
# ) -> dict[str, Any]:
#     email_row = await crud_users.exists(db=db, email=user.email)
#     if email_row:
#         raise DuplicateValueException("Email is already registered")

#     username_row = await crud_users.exists(db=db, username=user.username)
#     if username_row:
#         raise DuplicateValueException("Username not available")

#     user_internal_dict = user.model_dump()
#     user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
#     del user_internal_dict["password"]

#     user_internal = UserCreateInternal(**user_internal_dict)
#     created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)

#     if created_user is None:
#         raise NotFoundException("Failed to create user")

#     return created_user
