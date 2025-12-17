from fastapi import APIRouter
from api.v1 import users,auth

router = APIRouter(prefix="/v1")
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])