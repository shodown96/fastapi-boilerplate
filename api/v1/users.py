from fastapi import Query, Depends
from sqlmodel import select
from fastapi import APIRouter
from models.user import User
from core.db import SessionDep
from typing import Annotated
from starlette.exceptions import HTTPException
from core.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=list[User])
async def get_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/me", response_model=User)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/{id}", response_model=User)
async def get_user(session: SessionDep, id: str):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
