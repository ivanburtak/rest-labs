from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from repository.user_repository import (
    get_by_username,
    store_refresh_token,
    get_username_by_token,
    revoke_refresh_token,
)
from schemas.auth import TokenResponse, AccessTokenResponse

SECRET_KEY = "change-me-in-production-access"
REFRESH_SECRET_KEY = "change-me-in-production-refresh"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _make_token(data: dict, secret: str, expires: timedelta) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + expires}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def _decode_token(token: str, secret: str) -> Optional[dict]:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def login(username: str, password: str) -> Optional[TokenResponse]:
    user = await get_by_username(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return None

    access_token = _make_token(
        {"sub": username}, SECRET_KEY, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = _make_token(
        {"sub": username}, REFRESH_SECRET_KEY, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    await store_refresh_token(refresh_token, username)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh(refresh_token: str) -> Optional[AccessTokenResponse]:
    payload = _decode_token(refresh_token, REFRESH_SECRET_KEY)
    if not payload:
        return None

    username = payload.get("sub", "")
    stored = await get_username_by_token(refresh_token)
    if stored != username:
        return None

    access_token = _make_token(
        {"sub": username}, SECRET_KEY, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return AccessTokenResponse(access_token=access_token)


async def logout(refresh_token: str) -> None:
    await revoke_refresh_token(refresh_token)


async def get_current_user(token: str) -> Optional[str]:
    payload = _decode_token(token, SECRET_KEY)
    if not payload:
        return None
    return payload.get("sub")