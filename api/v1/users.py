from fastapi import Query, Depends
from sqlmodel import select
from fastapi import APIRouter
from models.user import User
from schemas.user import UserRead
from core.db import SessionDep
from typing import Annotated
from starlette.exceptions import HTTPException
from core.dependencies import get_current_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    result = await session.execute(
        select(User).offset(offset).limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/{id}", response_model=UserRead)
async def get_user(session: SessionDep, id: str,
    current_superuser: Annotated[User, Depends(get_current_superuser)],):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
