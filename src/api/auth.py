"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.session import get_db
from src.services.auth_service import AuthService
from src.services.jwt_service import JWTService
from src.models.user import User

router = APIRouter()

# HTTP Bearer token security scheme
security = HTTPBearer()


# Request/Response models
class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str
    openid: str
    nickname: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    id: str
    openid: str
    nickname: str | None
    avatar_url: str | None
    created_at: str


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class ErrorResponse(BaseModel):
    error: dict


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user from JWT token"""
    jwt_service = JWTService()
    auth_service = AuthService(db)

    # Validate token
    payload = jwt_service.validate_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_id = payload.get("user_id")
    user = auth_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/login", response_model=LoginResponse, summary="WeChat mini-program login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login using WeChat mini-program code.

    **Flow:**
    1. Mini-program calls wx.login() to get code
    2. Send code to this endpoint
    3. Server exchanges code with WeChat for openid
    4. Returns JWT token for subsequent API calls
    """
    try:
        auth_service = AuthService(db)
        result = auth_service.login_with_wechat_code(request.code)
        return LoginResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/profile", response_model=UserProfileResponse, summary="Get user profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information.

    Requires valid JWT token in Authorization header.
    """
    return UserProfileResponse(
        id=str(current_user.id),
        openid=current_user.openid,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/profile", response_model=UserProfileResponse, summary="Update user profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.

    Requires valid JWT token in Authorization header.
    """
    try:
        auth_service = AuthService(db)
        updated_user = auth_service.update_user_profile(
            user_id=str(current_user.id),
            nickname=request.nickname,
            avatar_url=request.avatar_url,
        )
        return UserProfileResponse(
            id=str(updated_user.id),
            openid=updated_user.openid,
            nickname=updated_user.nickname,
            avatar_url=updated_user.avatar_url,
            created_at=updated_user.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )