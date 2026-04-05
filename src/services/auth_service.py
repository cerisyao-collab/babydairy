"""WeChat authentication service"""

from sqlalchemy.orm import Session
from wechatpy import WeChatApp
from wechatpy.exceptions import WeChatClientException
import uuid
from datetime import datetime
from typing import Optional

from src.models.user import User
from src.config import settings
from src.services.jwt_service import JWTService


class AuthService:
    """Service for WeChat mini-program authentication"""

    def __init__(self, db: Session):
        self.db = db
        self.jwt_service = JWTService()
        self._wechat_app = None

    @property
    def wechat_app(self) -> WeChatApp:
        """Lazy load WeChat app instance"""
        if self._wechat_app is None:
            self._wechat_app = WeChatApp(
                appid=settings.wechat_app_id,
                secret=settings.wechat_app_secret,
            )
        return self._wechat_app

    def login_with_wechat_code(self, code: str) -> dict:
        """
        Login using WeChat mini-program code

        Args:
            code: Code from wx.login() in WeChat mini-program

        Returns:
            dict with token and user info

        Raises:
            ValueError: If code is invalid
        """
        try:
            # Get openid and session_key from WeChat
            result = self.wechat_app.code_to_session(code)
            openid = result.get("openid")

            if not openid:
                raise ValueError("Failed to get openid from WeChat")

            # Find or create user
            user = self._get_or_create_user(openid)

            # Generate JWT token
            token = self.jwt_service.create_token(user_id=str(user.id), openid=openid)

            return {
                "token": token,
                "openid": openid,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
            }

        except WeChatClientException as e:
            raise ValueError(f"WeChat login failed: {e.errmsg}")

    def _get_or_create_user(self, openid: str) -> User:
        """Find existing user or create new one"""
        user = self.db.query(User).filter(User.openid == openid).first()

        if user is None:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                openid=openid,
                nickname=None,
                avatar_url=None,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_openid(self, openid: str) -> Optional[User]:
        """Get user by WeChat openid"""
        return self.db.query(User).filter(User.openid == openid).first()

    def update_user_profile(
        self,
        user_id: str,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Update user profile information"""
        user = self.get_user_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user