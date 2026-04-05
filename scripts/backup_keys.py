#!/usr/bin/env python3
"""Key Backup Script

Create local backup of master key and all secrets.

Usage:
    python scripts/backup_keys.py --backup
    python scripts/backup_keys.py --backup-all

Environment variables:
    KEY_BACKUP_PASSWORD - Password to encrypt backup (optional but recommended)
    KEY_BACKUP_DIR      - Directory for backup files (default: /tmp/key-backups)
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
    download_master_key_from_oss,
    download_encrypted_secret_from_oss,
    list_secrets_in_oss,
    get_master_key_versions,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def backup_master_key(output_path: Optional[str] = None) -> str:
    """
    Create local backup of master key.

    Args:
        output_path: Optional custom output path

    Returns:
        Backup file path
    """
    # Download master key
    master_key, metadata = download_master_key_from_oss()
    logger.info("Master key downloaded from OSS")

    # Determine backup path
    backup_dir = os.environ.get("KEY_BACKUP_DIR", "/tmp/key-backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if output_path:
        backup_path = output_path
    else:
        backup_filename = f"master_key_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)

    # Encrypt backup with password
    backup_password = os.environ.get("KEY_BACKUP_PASSWORD", "")

    if backup_password:
        secrets_service = SecretsService()
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"baby-diary-key-backup",
            iterations=100000,
        )
        backup_key = kdf.derive(backup_password.encode())

        # Encrypt master key
        encrypted_backup = secrets_service.encrypt_with_data_key(
            master_key.hex(),
            backup_key
        )

        backup_data = {
            "encrypted": True,
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "master_key_data": encrypted_backup,
            "oss_metadata": metadata,
        }
    else:
        logger.warning("No KEY_BACKUP_PASSWORD set, storing unencrypted backup")
        backup_data = {
            "encrypted": False,
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "master_key": master_key.hex(),
            "oss_metadata": metadata,
        }

    # Write backup
    with open(backup_path, "w") as f:
        json.dump(backup_data, f, indent=2)

    logger.info(f"Master key backup saved to: {backup_path}")
    return backup_path


def backup_all_secrets(output_dir: Optional[str] = None) -> dict:
    """
    Backup all secrets and master key.

    Args:
        output_dir: Optional custom output directory

    Returns:
        Dict with backup paths
    """
    backup_dir = output_dir or os.environ.get("KEY_BACKUP_DIR", "/tmp/key-backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_subdir = os.path.join(backup_dir, f"full_backup_{timestamp}")
    os.makedirs(backup_subdir, exist_ok=True)

    results = {
        "backup_dir": backup_subdir,
        "timestamp": timestamp,
        "files": {},
    }

    # Backup master key
    master_key_path = os.path.join(backup_subdir, "master_key.json")
    results["files"]["master_key"] = backup_master_key(master_key_path)

    # Download master key for decryption
    master_key, _ = download_master_key_from_oss()
    secrets_service = SecretsService()

    # Backup each secret
    secret_names = list_secrets_in_oss()
    secrets_backup = {}

    for secret_name in secret_names:
        try:
            encrypted_data = download_encrypted_secret_from_oss(secret_name)
            # Store both encrypted and decrypted for flexibility
            plaintext = secrets_service.decrypt_secret(encrypted_data, master_key)

            secrets_backup[secret_name] = {
                "encrypted_data": encrypted_data,
                "plaintext": plaintext,  # WARNING: contains sensitive data
            }
            logger.info(f"Secret '{secret_name}' backed up")
        except Exception as e:
            logger.error(f"Failed to backup '{secret_name}': {e}")
            secrets_backup[secret_name] = {"error": str(e)}

    # Write secrets backup
    secrets_path = os.path.join(backup_subdir, "secrets.json")

    # Encrypt secrets backup with password
    backup_password = os.environ.get("KEY_BACKUP_PASSWORD", "")
    if backup_password:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"baby-diary-key-backup",
            iterations=100000,
        )
        backup_key = kdf.derive(backup_password.encode())

        secrets_service = SecretsService()
        encrypted_secrets = secrets_service.encrypt_with_data_key(
            json.dumps(secrets_backup),
            backup_key
        )

        secrets_backup_data = {
            "encrypted": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": encrypted_secrets,
        }
    else:
        logger.warning("Storing secrets backup unencrypted!")
        secrets_backup_data = {
            "encrypted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "secrets": secrets_backup,
        }

    with open(secrets_path, "w") as f:
        json.dump(secrets_backup_data, f, indent=2)

    results["files"]["secrets"] = secrets_path
    logger.info(f"All secrets backed up to: {secrets_path}")

    # Write backup manifest
    manifest_path = os.path.join(backup_subdir, "manifest.json")
    manifest = {
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backup_type": "full",
        "files": list(results["files"].keys()),
        "oss_versions": get_master_key_versions(),
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    results["files"]["manifest"] = manifest_path
    logger.info(f"Backup manifest saved to: {manifest_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Backup master key and secrets")
    parser.add_argument("--backup", action="store_true", help="Backup master key only")
    parser.add_argument("--backup-all", action="store_true", help="Backup master key and all secrets")
    parser.add_argument("--output", metavar="PATH", help="Custom output path/directory")
    parser.add_argument("--list-versions", action="store_true", help="List OSS versions")

    args = parser.parse_args()

    if args.backup:
        result = backup_master_key(args.output)
        print(f"Backup saved to: {result}")

    elif args.backup_all:
        result = backup_all_secrets(args.output)
        print(json.dumps(result, indent=2))

    elif args.list_versions:
        versions = get_master_key_versions()
        print(json.dumps(versions, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()