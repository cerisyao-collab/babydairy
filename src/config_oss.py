"""Application configuration using OSS-based secrets management

Replaces KMS-based secrets management for cost reduction:
- KMS: ¥50-100/month
- OSS + local encryption: ¥5-10/month

Secrets are stored encrypted in OSS bucket and decrypted at runtime
using local envelope encryption (AES-256-GCM).
"""

import logging
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings

from src.services.secrets_service import SecretsService, get_secrets_service
from src.services.oss_storage import (
    download_master_key_from_oss,
    download_encrypted_secret_from_oss,
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Baby Diary API"
    app_version: str = "1.0.0"
    debug: bool = False

    # OSS Configuration for secrets storage
    oss_endpoint: str = "oss-cn-hangzhou.aliyuncs.com"
    oss_secrets_bucket: str = ""

    # Database (will be loaded from OSS if bucket configured)
    database_url: str = "postgresql://postgres:password@localhost:5432/baby_diary"

    # WeChat Mini-program (will be loaded from OSS)
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # JWT Authentication (will be loaded from OSS)
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["*"]

    # Qwen LLM Configuration (will be loaded from OSS)
    dashscope_api_key: str = ""
    qwen_model: str = "qwen-turbo"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance (lazy loaded)
_settings: Optional[Settings] = None

# In-memory cache for decrypted secrets
_secrets_cache: dict[str, str] = {}

# Cached master key (per FC invocation)
_master_key: Optional[bytes] = None


def load_secrets_from_oss() -> dict[str, str]:
    """
    Load and decrypt all secrets from OSS bucket.

    Uses local envelope encryption (AES-256-GCM).

    Returns:
        Dict of secret_name -> plaintext_value
    """
    global _master_key, _secrets_cache

    if _secrets_cache:
        return _secrets_cache

    secrets_bucket = os.environ.get("OSS_SECRETS_BUCKET", "")
    if not secrets_bucket:
        logger.info("OSS secrets bucket not configured, using environment variables")
        return {}

    # Download master key
    if _master_key is None:
        try:
            _master_key, _ = download_master_key_from_oss()
            logger.info("Master key loaded from OSS")
        except Exception as e:
            logger.error(f"Failed to load master key: {e}")
            raise

    # Get secrets service
    secrets_service = get_secrets_service()

    # Define which secrets to load
    secret_names = [
        "db_password",
        "wechat_app_secret",
        "dashscope_api_key",
        "jwt_secret",
    ]

    for secret_name in secret_names:
        try:
            encrypted_data = download_encrypted_secret_from_oss(secret_name)
            plaintext = secrets_service.decrypt_secret(encrypted_data, _master_key)
            _secrets_cache[secret_name] = plaintext
            logger.info(f"Secret '{secret_name}' loaded and decrypted")
        except Exception as e:
            logger.warning(f"Failed to load secret '{secret_name}': {e}")

    return _secrets_cache


def get_secret(secret_name: str) -> str:
    """
    Get a secret value by name.

    First checks OSS secrets cache, then environment variables.

    Args:
        secret_name: Name of the secret

    Returns:
        Secret plaintext value
    """
    # Try cache first
    if secret_name in _secrets_cache:
        return _secrets_cache[secret_name]

    # Load from OSS if bucket configured
    secrets_bucket = os.environ.get("OSS_SECRETS_BUCKET", "")
    if secrets_bucket:
        secrets = load_secrets_from_oss()
        if secret_name in secrets:
            return secrets[secret_name]

    # Fallback to environment variable
    env_var_name = secret_name.upper()
    return os.environ.get(env_var_name, "")


def clear_secrets_cache():
    """Clear all secrets caches"""
    global _settings, _secrets_cache, _master_key
    _settings = None
    _secrets_cache = {}
    _master_key = None


def get_settings() -> Settings:
    """
    Get application settings with secrets loaded from OSS.

    Settings are cached per FC invocation.

    Returns:
        Settings instance with all configuration
    """
    global _settings

    if _settings is None:
        # Load secrets from OSS
        secrets = load_secrets_from_oss()

        # Create settings with overrides from OSS secrets
        settings_kwargs = {}

        # Database URL with password from OSS
        if secrets.get("db_password"):
            db_url = os.environ.get("DATABASE_URL", "")
            if db_url:
                # Replace password in URL
                import re
                settings_kwargs["database_url"] = re.sub(
                    r"postgresql://([^:]+):([^@]+)@",
                    f"postgresql://\\1:{secrets['db_password']}@",
                    db_url
                )

        # WeChat credentials
        if secrets.get("wechat_app_secret"):
            settings_kwargs["wechat_app_secret"] = secrets["wechat_app_secret"]

        # JWT secret
        if secrets.get("jwt_secret"):
            settings_kwargs["jwt_secret"] = secrets["jwt_secret"]

        # DashScope API key
        if secrets.get("dashscope_api_key"):
            settings_kwargs["dashscope_api_key"] = secrets["dashscope_api_key"]

        _settings = Settings(**settings_kwargs)
        logger.info("Settings loaded with OSS secrets")

    return _settings


# Convenience functions for common secrets
def get_database_password() -> str:
    """Get decrypted database password"""
    return get_secret("db_password")


def get_wechat_app_secret() -> str:
    """Get decrypted WeChat app secret"""
    return get_secret("wechat_app_secret")


def get_dashscope_api_key() -> str:
    """Get decrypted DashScope API key"""
    return get_secret("dashscope_api_key")


def get_jwt_secret() -> str:
    """Get decrypted JWT secret"""
    return get_secret("jwt_secret")


# Create global settings instance (lazy loaded via get_settings())
settings = Settings()  # Default settings for import compatibility