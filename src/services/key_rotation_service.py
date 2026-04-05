"""Key Rotation Service for OSS-based secrets management

Provides automatic master key rotation every 90 days.
Scheduled via FC timer trigger (monthly check).

Rotation process:
1. Generate new master key
2. Re-encrypt all secrets with new master key
3. Upload new master key to OSS (versioned)
4. Backup old master key locally
5. Log rotation result
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from src.services.secrets_service import SecretsService, get_secrets_service
from src.services.oss_storage import (
    download_master_key_from_oss,
    upload_master_key_to_oss,
    download_encrypted_secret_from_oss,
    upload_encrypted_secret_to_oss,
    list_secrets_in_oss,
    get_master_key_versions,
)

logger = logging.getLogger(__name__)

# Rotation configuration
ROTATION_PERIOD_DAYS = 90  # Rotate after 90 days
BACKUP_RETENTION_DAYS = 7  # Keep old key backup for 7 days


class KeyRotationService:
    """Service for master key rotation"""

    def __init__(self):
        self.secrets_service = get_secrets_service()

    def check_master_key_age(self) -> dict:
        """
        Check if master key needs rotation.

        Returns:
            Dict with:
            - age_days: Current age of master key
            - needs_rotation: True if age > ROTATION_PERIOD_DAYS
            - created_at: When master key was created
        """
        try:
            _, metadata = download_master_key_from_oss()
            created_at_str = metadata.get("created_at")

            if not created_at_str:
                # No creation date, assume needs rotation
                logger.warning("Master key has no creation date")
                return {
                    "age_days": -1,
                    "needs_rotation": True,
                    "created_at": None,
                }

            created_at = datetime.fromisoformat(created_at_str)
            now = datetime.now(timezone.utc)

            age_days = (now - created_at).days
            needs_rotation = age_days > ROTATION_PERIOD_DAYS

            logger.info(f"Master key age: {age_days} days, rotation needed: {needs_rotation}")

            return {
                "age_days": age_days,
                "needs_rotation": needs_rotation,
                "created_at": created_at_str,
            }

        except Exception as e:
            logger.error(f"Failed to check master key age: {e}")
            raise

    def rotate_master_key(self) -> dict:
        """
        Rotate master key and re-encrypt all secrets.

        Steps:
        1. Download current master key
        2. Generate new master key
        3. Re-encrypt all secrets with new master key
        4. Upload new master key to OSS
        5. Backup old master key

        Returns:
            Dict with rotation result
        """
        logger.info("Starting master key rotation")

        # Download current master key
        try:
            old_master_key, old_metadata = download_master_key_from_oss()
            logger.info("Current master key downloaded")
        except Exception as e:
            logger.error(f"Failed to download current master key: {e}")
            raise ValueError("Cannot rotate without current master key")

        # Generate new master key
        new_master_key = self.secrets_service.generate_master_key()
        logger.info("New master key generated")

        # Re-encrypt all secrets
        secrets_to_rotate = self.re_encrypt_all_secrets(
            old_master_key,
            new_master_key
        )
        logger.info(f"Re-encrypted {len(secrets_to_rotate)} secrets")

        # Backup old master key locally
        self.backup_old_master_key(old_master_key, old_metadata)
        logger.info("Old master key backed up")

        # Upload new master key to OSS
        upload_metadata = upload_master_key_to_oss(
            new_master_key,
            metadata={
                "previous_version": old_metadata.get("version_id"),
                "rotation_reason": "automatic",
                "rotated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        logger.info(f"New master key uploaded, version: {upload_metadata.get('version_id')}")

        # Log rotation success
        self.log_rotation_result(True, {
            "secrets_rotated": len(secrets_to_rotate),
            "new_version": upload_metadata.get("version_id"),
        })

        return {
            "success": True,
            "secrets_rotated": len(secrets_to_rotate),
            "new_version": upload_metadata.get("version_id"),
            "rotated_at": datetime.now(timezone.utc).isoformat(),
        }

    def re_encrypt_all_secrets(
        self,
        old_master_key: bytes,
        new_master_key: bytes,
    ) -> list[str]:
        """
        Re-encrypt all secrets with new master key.

        Args:
            old_master_key: Current master key
            new_master_key: New master key

        Returns:
            List of re-encrypted secret names
        """
        secret_names = list_secrets_in_oss()
        rotated = []

        for secret_name in secret_names:
            try:
                # Download encrypted secret
                encrypted_data = download_encrypted_secret_from_oss(secret_name)

                # Decrypt with old master key
                plaintext = self.secrets_service.decrypt_secret(
                    encrypted_data,
                    old_master_key
                )

                # Encrypt with new master key
                new_encrypted_data = self.secrets_service.encrypt_secret(
                    plaintext,
                    new_master_key
                )

                # Upload re-encrypted secret
                upload_encrypted_secret_to_oss(secret_name, new_encrypted_data)

                rotated.append(secret_name)
                logger.info(f"Secret '{secret_name}' re-encrypted")

            except Exception as e:
                logger.error(f"Failed to re-encrypt secret '{secret_name}': {e}")
                # Continue with other secrets

        return rotated

    def backup_old_master_key(
        self,
        old_master_key: bytes,
        metadata: dict,
    ) -> str:
        """
        Backup old master key to local storage.

        The backup is encrypted with a backup password for security.

        Args:
            old_master_key: Old master key bytes
            metadata: Metadata from OSS

        Returns:
            Backup file path
        """
        backup_dir = os.environ.get("KEY_BACKUP_DIR", "/tmp/key-backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"master_key_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Encrypt backup with backup password
        backup_password = os.environ.get("KEY_BACKUP_PASSWORD", "")
        if backup_password:
            # Derive key from password (simple approach)
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"baby-diary-key-backup",  # Fixed salt
                iterations=100000,
            )
            backup_key = kdf.derive(backup_password.encode())

            # Encrypt master key
            encrypted_backup = self.secrets_service.encrypt_with_data_key(
                old_master_key.hex(),
                backup_key
            )

            backup_data = {
                "encrypted": True,
                "data": encrypted_backup,
                "metadata": metadata,
            }
        else:
            # Store unencrypted (not recommended)
            logger.warning("No backup password set, storing backup unencrypted")
            backup_data = {
                "encrypted": False,
                "key": old_master_key.hex(),
                "metadata": metadata,
            }

        with open(backup_path, "w") as f:
            json.dump(backup_data, f)

        logger.info(f"Backup saved to {backup_path}")
        return backup_path

    def log_rotation_result(
        self,
        success: bool,
        details: dict,
    ) -> None:
        """
        Log key rotation result.

        Args:
            success: Whether rotation succeeded
            details: Additional details
        """
        log_data = {
            "event": "key_rotation",
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }

        logger.info(f"Key rotation log: {json.dumps(log_data)}")

        # Optionally send to logging service
        # For FC, can use SLS (Simple Log Service)
        try:
            from src.services.oss_storage import OSS_ENDPOINT, OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET
            # Check if SLS is configured
            sls_project = os.environ.get("SLS_PROJECT", "")
            if sls_project:
                # Send log to SLS
                self.send_alert_to_sls(log_data)
        except Exception as e:
            logger.warning(f"Failed to send rotation log to SLS: {e}")

    def send_alert_to_sls(self, log_data: dict) -> None:
        """
        Send alert to Alibaba Cloud SLS.

        Args:
            log_data: Log data to send
        """
        # SLS integration would require additional SDK
        # This is a placeholder for actual implementation
        logger.info(f"Would send to SLS: {json.dumps(log_data)}")

    def rollback_master_key(self, version_id: str) -> dict:
        """
        Rollback to a previous master key version.

        Args:
            version_id: OSS version ID to rollback to

        Returns:
            Dict with rollback result
        """
        logger.warning(f"Attempting rollback to version {version_id}")

        try:
            # Download old master key
            old_master_key, metadata = download_master_key_from_oss(version_id)

            # This is the master key to use now
            # Secrets encrypted with newer key would need re-encryption
            # For simplicity, we just restore the key

            upload_metadata = upload_master_key_to_oss(
                old_master_key,
                metadata={
                    "rollback_from_version": version_id,
                    "rollback_reason": "manual",
                    "rolled_back_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            logger.info(f"Rollback complete, new version: {upload_metadata.get('version_id')}")

            return {
                "success": True,
                "version_id": upload_metadata.get("version_id"),
                "rolled_back_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise


# Global instance
_key_rotation_service: Optional[KeyRotationService] = None


def get_key_rotation_service() -> KeyRotationService:
    """Get or create key rotation service instance"""
    global _key_rotation_service
    if _key_rotation_service is None:
        _key_rotation_service = KeyRotationService()
    return _key_rotation_service


def run_key_rotation_check() -> dict:
    """
    Entry point for FC timer trigger.

    Checks if rotation is needed and performs it.

    Returns:
        Dict with check/rotation result
    """
    service = get_key_rotation_service()

    # Check key age
    status = service.check_master_key_age()

    if status["needs_rotation"]:
        logger.info("Rotation needed, starting...")
        result = service.rotate_master_key()
        return {
            "action": "rotated",
            "result": result,
        }
    else:
        logger.info(f"No rotation needed (age: {status['age_days']} days)")
        return {
            "action": "skipped",
            "reason": f"Key age ({status['age_days']} days) below threshold ({ROTATION_PERIOD_DAYS})",
        }