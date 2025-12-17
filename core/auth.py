# from datetime import datetime, timedelta, timezone
# from typing import Annotated

# import jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jwt.exceptions import InvalidTokenError
# from models.user import User
# from pwdlib import PasswordHash
# from schemas.user import TokenData
# from sqlmodel import select

# from core.config import settings
# from core.db import SessionDep

# password_hash = PasswordHash.recommended()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="sign-in")


# def verify_password(plain_password, hashed_password):
#     return password_hash.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return password_hash.hash(password)


# def get_user(session: SessionDep, id: str):
#     return session.get(User, id)

# def get_user_by_email(session: SessionDep, email: str):
#     statement = select(User).where(User.email == email)
#     return session.exec(statement).first()


# def authenticate_user(session: SessionDep, email: str, password: str):
#     user = get_user_by_email(session, email)
#     if not user:
#         return False
#     if not verify_password(password, user.password):
#         return False
#     return user


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt


# async def get_current_user(
#     session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
# ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#         token_data = TokenData(user_id=user_id)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(session, id=token_data.user_id)
#     if user is None:
#         raise credentials_exception
#     return user


# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
