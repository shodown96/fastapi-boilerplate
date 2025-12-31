from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Literal

import bcrypt
import jwt
from core.schemas import TokenBlacklistCreate, TokenData
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from sqlalchemy import select
from models.user import User
from sqlalchemy import select
from models.token_blacklist import TokenBlacklist

SECRET_KEY: SecretStr = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign-in")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = bcrypt.checkpw(
        plain_password.encode(), hashed_password.encode()
    )
    return correct_password


def get_password_hash(password: str) -> str:
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashed_password


async def authenticate_user(
    username_or_email: str,
    password: str,
    db: AsyncSession,
) -> dict[str, Any] | Literal[False]:

    stmt = select(User).where(User.is_deleted.is_(False))

    if "@" in username_or_email:
        stmt = stmt.where(User.email == username_or_email)
    else:
        stmt = stmt.where(User.username == username_or_email)

    result = await db.execute(stmt)
    user = result.scalars().one_or_none()

    if not user:
        return False

    if not await verify_password(password, user.hashed_password):
        return False

    return user


async def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    encoded_jwt: str = jwt.encode(
        to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM
    )
    return encoded_jwt


async def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    encoded_jwt: str = jwt.encode(
        to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM
    )
    return encoded_jwt


async def verify_token(
    token: str, expected_token_type: TokenType, db: AsyncSession
) -> TokenData | None:
    """Verify a JWT token and return TokenData if valid.

    Parameters
    ----------
    token: str
        The JWT token to be verified.
    expected_token_type: TokenType
        The expected type of token (access or refresh)
    db: AsyncSession
        Database session for performing database operations.

    Returns
    -------
    TokenData | None
        TokenData instance if the token is valid, None otherwise.
    """
    result = await db.execute(
        select(TokenBlacklist.id).where(TokenBlacklist.token == token)
    )
    is_blacklisted = result.scalar_one_or_none() is not None

    if is_blacklisted:
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY.get_secret_value(),
            algorithms=[ALGORITHM],
        )

        username_or_email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if username_or_email is None or token_type != expected_token_type:
            return None

        return TokenData(username_or_email=username_or_email)

    except JWTError:
        return None


async def blacklist_tokens(access_token: str, refresh_token: str, db: AsyncSession) -> None:
    """Blacklist both access and refresh tokens.

    Parameters
    ----------
    access_token: str
        The access token to blacklist
    refresh_token: str
        The refresh token to blacklist
    db: AsyncSession
        Database session for performing database operations.
    """
    for token in (access_token, refresh_token):
        payload = jwt.decode(
            token,
            SECRET_KEY.get_secret_value(),
            algorithms=[ALGORITHM],
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            continue

        db.add(
            TokenBlacklist(
                token=token,
                expires_at=datetime.fromtimestamp(exp_timestamp),
            )
        )

    await db.commit()


async def blacklist_token(token: str, db: AsyncSession) -> None:
    payload = jwt.decode(
        token,
        SECRET_KEY.get_secret_value(),
        algorithms=[ALGORITHM],
    )
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        return

    db.add(
        TokenBlacklist(
            token=token,
            expires_at=datetime.fromtimestamp(exp_timestamp),
        )
    )
    await db.commit()
