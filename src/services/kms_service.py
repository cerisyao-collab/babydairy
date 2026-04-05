"""Legacy KMS Service - now redirects to OSS-based secrets management

This file is kept for backwards compatibility but now uses the OSS-based
secrets management system.

Migration note:
- Old: Alibaba Cloud KMS (¥50-100/month)
- New: OSS + local envelope encryption (¥5-10/month)
"""

import logging
import os
from typing import Optional

# Import the new OSS-based secrets functions
from src.config import (
    get_database_password,
    get_wechat_app_secret,
    get_dashscope_api_key,
    get_jwt_secret,
    clear_secret_cache,
    get_secret,
)

logger = logging.getLogger(__name__)


# Re-export functions for backwards compatibility
# These now use OSS-based secrets instead of KMS

def get_decrypted_secret(env_var: str) -> str:
    """
    Get decrypted secret (legacy function).

    Now redirects to OSS-based secrets management.

    Args:
        env_var: Name of environment variable or secret name

    Returns:
        Decrypted secret value
    """
    # Map environment variable names to secret names
    secret_name_map = {
        "ENCRYPTED_DB_PASSWORD": "db_password",
        "DB_PASSWORD": "db_password",
        "ENCRYPTED_WECHAT_APP_SECRET": "wechat_app_secret",
        "WECHAT_APP_SECRET": "wechat_app_secret",
        "ENCRYPTED_DASHSCOPE_API_KEY": "dashscope_api_key",
        "DASHSCOPE_API_KEY": "dashscope_api_key",
        "ENCRYPTED_JWT_SECRET": "jwt_secret",
        "JWT_SECRET": "jwt_secret",
    }

    secret_name = secret_name_map.get(env_var, env_var.lower())
    return get_secret(secret_name)


# Convenience functions - now use OSS-based secrets
def get_database_password_oss() -> str:
    """Get decrypted database password (OSS-based)"""
    return get_database_password()


def get_wechat_app_secret_oss() -> str:
    """Get decrypted WeChat app secret (OSS-based)"""
    return get_wechat_app_secret()


def get_dashscope_api_key_oss() -> str:
    """Get decrypted DashScope API key (OSS-based)"""
    return get_dashscope_api_key()


def get_jwt_secret_oss() -> str:
    """Get decrypted JWT secret (OSS-based)"""
    return get_jwt_secret()


# Note: KMSService class is removed.
# If you need encryption capabilities, use SecretsService from secrets_service.py
logger.info("KMS service migrated to OSS-based secrets management")