#!/usr/bin/env python3
"""Secrets Initialization Script

Initialize master key and encrypted secrets in OSS bucket.

Usage:
    python scripts/init_secrets.py --init-key
    python scripts/init_secrets.py --encrypt-secret <name> <value>
    python scripts/init_secrets.py --init-all

Environment variables required:
    OSS_ENDPOINT          - OSS endpoint (e.g., oss-cn-hangzhou.aliyuncs.com)
    OSS_SECRETS_BUCKET    - OSS bucket name for secrets
    ALIBABA_CLOUD_ACCESS_KEY_ID     - Aliyun AccessKey ID
    ALIBABA_CLOUD_ACCESS_KEY_SECRET - Aliyun AccessKey Secret
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.secrets_service import SecretsService
from src.services.oss_storage import (
    upload_master_key_to_oss,
    download_master_key_from_oss,
    upload_encrypted_secret_to_oss,
    list_secrets_in_oss,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_master_key() -> dict:
    """
    Initialize master key in OSS bucket.

    Creates a new 256-bit master key and uploads to OSS.

    Returns:
        Dict with key metadata
    """
    secrets_service = SecretsService()

    # Generate new master key
    master_key = secrets_service.generate_master_key()
    logger.info("Generated new 256-bit master key")

    # Upload to OSS
    metadata = upload_master_key_to_oss(
        master_key,
        metadata={
            "created_by": "init_secrets.py",
            "rotation_enabled": "true",
            "rotation_period_days": "90",
        }
    )

    logger.info(f"Master key uploaded to OSS: {metadata}")
    return metadata


def encrypt_secret(secret_name: str, secret_value: str) -> dict:
    """
    Encrypt a secret and upload to OSS.

    Args:
        secret_name: Name of the secret (e.g., "db_password")
        secret_value: Plaintext value to encrypt

    Returns:
        Dict with upload metadata
    """
    secrets_service = SecretsService()

    # Download master key
    try:
        master_key, _ = download_master_key_from_oss()
        logger.info("Master key downloaded from OSS")
    except Exception as e:
        logger.error(f"Failed to download master key: {e}")
        logger.error("Run 'init_secrets.py --init-key' first")
        raise

    # Encrypt secret
    encrypted_data = secrets_service.encrypt_secret(secret_value, master_key)
    logger.info(f"Secret '{secret_name}' encrypted")

    # Upload to OSS
    upload_metadata = upload_encrypted_secret_to_oss(secret_name, encrypted_data)
    logger.info(f"Secret '{secret_name}' uploaded to OSS")

    return upload_metadata


def init_all_secrets() -> dict:
    """
    Initialize all secrets from environment variables.

    Reads secrets from environment and encrypts them.

    Returns:
        Dict with all secrets metadata
    """
    secrets_to_init = {
        "db_password": os.environ.get("DB_PASSWORD", ""),
        "wechat_app_secret": os.environ.get("WECHAT_APP_SECRET", ""),
        "dashscope_api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
        "jwt_secret": os.environ.get("JWT_SECRET", ""),
    }

    # Initialize master key first
    logger.info("Initializing master key...")
    key_metadata = init_master_key()

    # Encrypt each secret
    results = {"master_key": key_metadata, "secrets": {}}

    for secret_name, secret_value in secrets_to_init.items():
        if secret_value:
            logger.info(f"Encrypting secret: {secret_name}")
            try:
                metadata = encrypt_secret(secret_name, secret_value)
                results["secrets"][secret_name] = metadata
            except Exception as e:
                logger.error(f"Failed to encrypt {secret_name}: {e}")
                results["secrets"][secret_name] = {"error": str(e)}
        else:
            logger.warning(f"Secret {secret_name} not set, skipping")
            results["secrets"][secret_name] = {"skipped": True, "reason": "not_set"}

    return results


def main():
    parser = argparse.ArgumentParser(description="Initialize secrets in OSS bucket")
    parser.add_argument("--init-key", action="store_true", help="Initialize master key only")
    parser.add_argument("--encrypt-secret", nargs=2, metavar=("NAME", "VALUE"),
                        help="Encrypt a specific secret")
    parser.add_argument("--init-all", action="store_true", help="Initialize master key and all secrets")
    parser.add_argument("--list", action="store_true", help="List existing secrets")
    parser.add_argument("--check-key", action="store_true", help="Check if master key exists")

    args = parser.parse_args()

    # Check required environment variables
    if not os.environ.get("OSS_SECRETS_BUCKET"):
        logger.error("OSS_SECRETS_BUCKET not set")
        sys.exit(1)

    if args.init_key:
        logger.info("Initializing master key...")
        result = init_master_key()
        print(json.dumps(result, indent=2))

    elif args.encrypt_secret:
        name, value = args.encrypt_secret
        logger.info(f"Encrypting secret: {name}")
        result = encrypt_secret(name, value)
        print(json.dumps(result, indent=2))

    elif args.init_all:
        logger.info("Initializing all secrets...")
        result = init_all_secrets()
        print(json.dumps(result, indent=2))

    elif args.list:
        secrets = list_secrets_in_oss()
        print(f"Existing secrets: {json.dumps(secrets, indent=2)}")

    elif args.check_key:
        try:
            master_key, metadata = download_master_key_from_oss()
            print(f"Master key exists: {json.dumps(metadata, indent=2)}")
        except Exception as e:
            print(f"Master key not found: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()