from fastapi import APIRouter, HTTPException, status, Depends
from schemas.auth import LoginRequest, TokenResponse, AccessTokenResponse, RefreshRequest
from services import auth_service
from api.deps import require_auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    tokens = await auth_service.login(body.username, body.password)
    if not tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")
    return tokens


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(body: RefreshRequest):
    result = await auth_service.refresh(body.refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired refresh token")
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, _: str = Depends(require_auth)):
    await auth_service.logout(body.refresh_token)