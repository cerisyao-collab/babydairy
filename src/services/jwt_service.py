"""JWT token service for authentication"""

import jwt
from datetime import datetime, timedelta
from typing import Optional

from src.config import settings


class JWTService:
    """Service for JWT token generation and validation"""

    def __init__(self):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.jwt_expire_minutes

    def create_token(self, user_id: str, openid: str) -> str:
        """
        Create JWT token for authenticated user

        Args:
            user_id: User's UUID
            openid: WeChat openid

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "openid": openid,
            "exp": datetime.utcnow() + timedelta(minutes=self.expire_minutes),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token

    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate JWT token and extract payload

        Args:
            token: JWT token string

        Returns:
            Payload dict if valid, None if invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user_id from valid token"""
        payload = self.validate_token(token)
        if payload is None:
            return None
        return payload.get("user_id")

    def get_openid_from_token(self, token: str) -> Optional[str]:
        """Extract openid from valid token"""
        payload = self.validate_token(token)
        if payload is None:
            return None
        return payload.get("openid")