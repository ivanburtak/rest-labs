from typing import Optional, Dict
from models.user import USERS, REFRESH_TOKENS


async def get_by_username(username: str) -> Optional[Dict]:
    return next((u for u in USERS if u["username"] == username), None)


async def store_refresh_token(token: str, username: str) -> None:
    REFRESH_TOKENS[token] = username


async def get_username_by_token(token: str) -> Optional[str]:
    return REFRESH_TOKENS.get(token)


async def revoke_refresh_token(token: str) -> None:
    REFRESH_TOKENS.pop(token, None)