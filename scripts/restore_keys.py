#!/usr/bin/env python3
"""Key Restore Script

Restore master key and secrets from backup.

Usage:
    python scripts/restore_keys.py --restore-key <backup_file>
    python scripts/restore_keys.py --restore-all <backup_dir>
    python scripts/restore_keys.py --restore-version <oss_version_id>

Environment variables:
    KEY_BACKUP_PASSWORD - Password to decrypt backup
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
    upload_encrypted_secret_to_oss,
    download_master_key_from_oss,
    list_secrets_in_oss,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def decrypt_backup_data(backup_data: dict) -> bytes:
    """
    Decrypt backup data using backup password.

    Args:
        backup_data: Backup dict from backup file

    Returns:
        Decrypted master key bytes
    """
    backup_password = os.environ.get("KEY_BACKUP_PASSWORD", "")
    if not backup_password:
        logger.error("KEY_BACKUP_PASSWORD not set")
        raise ValueError("Backup password required for encrypted backups")

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

    if backup_data.get("encrypted"):
        encrypted_key_data = backup_data["master_key_data"] if "master_key_data" in backup_data else backup_data["data"]
        master_key_hex = secrets_service.decrypt_with_data_key(encrypted_key_data, backup_key)
        master_key = bytes.fromhex(master_key_hex)
    else:
        master_key = bytes.fromhex(backup_data["master_key"])

    return master_key


def restore_master_key_from_backup(backup_path: str) -> dict:
    """
    Restore master key from local backup file.

    Args:
        backup_path: Path to backup JSON file

    Returns:
        Dict with restore result
    """
    logger.info(f"Restoring master key from: {backup_path}")

    # Read backup file
    with open(backup_path, "r") as f:
        backup_data = json.load(f)

    # Decrypt backup
    master_key = decrypt_backup_data(backup_data)
    logger.info("Master key decrypted from backup")

    # Upload to OSS
    metadata = upload_master_key_to_oss(
        master_key,
        metadata={
            "restored_from": backup_path,
            "restore_reason": "manual",
            "original_created_at": backup_data.get("oss_metadata", {}).get("created_at"),
            "restored_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    logger.info(f"Master key restored to OSS, version: {metadata.get('version_id')}")
    return metadata


def restore_all_from_backup(backup_dir: str) -> dict:
    """
    Restore master key and all secrets from backup directory.

    Args:
        backup_dir: Directory containing backup files

    Returns:
        Dict with restore results
    """
    logger.info(f"Restoring all from backup: {backup_dir}")

    results = {
        "backup_dir": backup_dir,
        "restored_at": datetime.now(timezone.utc).isoformat(),
        "master_key": {},
        "secrets": {},
    }

    # Restore master key
    master_key_path = os.path.join(backup_dir, "master_key.json")
    if os.path.exists(master_key_path):
        results["master_key"] = restore_master_key_from_backup(master_key_path)

        # Get restored master key
        master_key, _ = download_master_key_from_oss()
    else:
        logger.error(f"Master key backup not found: {master_key_path}")
        return {"error": "Master key backup not found"}

    # Restore secrets
    secrets_path = os.path.join(backup_dir, "secrets.json")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            secrets_backup_data = json.load(f)

        # Decrypt secrets backup
        backup_password = os.environ.get("KEY_BACKUP_PASSWORD", "")
        secrets_service = SecretsService()

        if secrets_backup_data.get("encrypted"):
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"baby-diary-key-backup",
                iterations=100000,
            )
            backup_key = kdf.derive(backup_password.encode())

            secrets_json = secrets_service.decrypt_with_data_key(
                secrets_backup_data["data"],
                backup_key
            )
            secrets_backup = json.loads(secrets_json)
        else:
            secrets_backup = secrets_backup_data["secrets"]

        # Upload each secret
        for secret_name, secret_data in secrets_backup.items():
            if secret_data.get("error"):
                continue

            # Re-encrypt with current master key
            plaintext = secret_data["plaintext"]
            encrypted_data = secrets_service.encrypt_secret(plaintext, master_key)

            upload_metadata = upload_encrypted_secret_to_oss(secret_name, encrypted_data)
            results["secrets"][secret_name] = upload_metadata
            logger.info(f"Secret '{secret_name}' restored")

    # Verify manifest
    manifest_path = os.path.join(backup_dir, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        results["manifest"] = manifest
        logger.info(f"Backup manifest: {manifest.get('created_at')}")

    return results


def restore_from_oss_version(version_id: str) -> dict:
    """
    Restore master key from a specific OSS version.

    Args:
        version_id: OSS version ID to restore

    Returns:
        Dict with restore result
    """
    from src.services.key_rotation_service import KeyRotationService

    service = KeyRotationService()
    result = service.rollback_master_key(version_id)

    logger.info(f"Master key restored from OSS version: {version_id}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Restore master key and secrets")
    parser.add_argument("--restore-key", metavar="BACKUP_FILE", help="Restore master key from backup file")
    parser.add_argument("--restore-all", metavar="BACKUP_DIR", help="Restore all from backup directory")
    parser.add_argument("--restore-version", metavar="VERSION_ID", help="Restore from OSS version ID")
    parser.add_argument("--verify", action="store_true", help="Verify current master key")

    args = parser.parse_args()

    if args.restore_key:
        result = restore_master_key_from_backup(args.restore_key)
        print(json.dumps(result, indent=2))

    elif args.restore_all:
        result = restore_all_from_backup(args.restore_all)
        print(json.dumps(result, indent=2))

    elif args.restore_version:
        result = restore_from_oss_version(args.restore_version)
        print(json.dumps(result, indent=2))

    elif args.verify:
        try:
            master_key, metadata = download_master_key_from_oss()
            print(f"Master key valid: {json.dumps(metadata, indent=2)}")

            secrets_service = SecretsService()
            secret_names = list_secrets_in_oss()
            print(f"Secrets available: {secret_names}")

            for name in secret_names:
                try:
                    encrypted = download_encrypted_secret_from_oss(name)
                    # Just check we can decrypt
                    plaintext = secrets_service.decrypt_secret(encrypted, master_key)
                    print(f"  - {name}: OK")
                except Exception as e:
                    print(f"  - {name}: FAILED ({e})")

        except Exception as e:
            print(f"Verification failed: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()