from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import get_current_user

bearer = HTTPBearer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    username = await get_current_user(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username