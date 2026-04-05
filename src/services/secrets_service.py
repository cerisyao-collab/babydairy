"""Secrets Service for local envelope encryption

Provides encryption/decryption using AES-256-GCM with envelope encryption.
Master key is stored in OSS bucket, secrets are encrypted locally.

This replaces KMS-based secrets management for cost reduction:
- KMS: ¥50-100/month
- OSS + local encryption: ¥5-10/month
"""

import base64
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

# In-memory cache for decrypted secrets
_decrypted_cache: dict[str, str] = {}

# In-memory cache for master key (cached per FC invocation)
_master_key_cache: Optional[bytes] = None
_master_key_metadata_cache: Optional[dict] = None


class SecretsService:
    """Service for local envelope encryption using AES-256-GCM"""

    # AES-GCM requires 12 bytes IV
    IV_LENGTH = 12
    # AES-256 requires 32 bytes key
    KEY_LENGTH = 32
    # AES-GCM auth tag is 16 bytes (handled by library)

    def generate_master_key(self) -> bytes:
        """
        Generate a new 256-bit master key.

        Returns:
            32-byte random master key
        """
        return secrets.token_bytes(self.KEY_LENGTH)

    def generate_data_key(self) -> bytes:
        """
        Generate a new 256-bit data key for encrypting a single secret.

        Returns:
            32-byte random data key
        """
        return secrets.token_bytes(self.KEY_LENGTH)

    def encrypt_with_data_key(
        self,
        plaintext: str,
        data_key: bytes,
    ) -> dict:
        """
        Encrypt plaintext using AES-256-GCM with the given data key.

        Args:
            plaintext: Text to encrypt
            data_key: 32-byte data key

        Returns:
            Dict with: iv (base64), ciphertext (base64), auth_tag (base64)
        """
        aesgcm = AESGCM(data_key)
        iv = secrets.token_bytes(self.IV_LENGTH)

        # Encrypt (auth tag is appended by library)
        ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode(), None)

        # Split ciphertext and auth tag (last 16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        auth_tag = ciphertext_with_tag[-16:]

        return {
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "auth_tag": base64.b64encode(auth_tag).decode(),
        }

    def decrypt_with_data_key(
        self,
        encrypted_data: dict,
        data_key: bytes,
    ) -> str:
        """
        Decrypt ciphertext using AES-256-GCM with the given data key.

        Args:
            encrypted_data: Dict with iv, ciphertext, auth_tag (all base64)
            data_key: 32-byte data key

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If decryption fails (wrong key or corrupted data)
        """
        aesgcm = AESGCM(data_key)

        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        auth_tag = base64.b64decode(encrypted_data["auth_tag"])

        # Combine ciphertext and auth tag for decryption
        ciphertext_with_tag = ciphertext + auth_tag

        try:
            plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)
            return plaintext.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Decryption failed - possibly wrong key or corrupted data")

    def encrypt_data_key(
        self,
        data_key: bytes,
        master_key: bytes,
    ) -> dict:
        """
        Encrypt a data key using the master key (envelope encryption).

        Args:
            data_key: 32-byte data key to encrypt
            master_key: 32-byte master key

        Returns:
            Dict with: iv, encrypted_data_key, auth_tag (all base64)
        """
        # Data key as bytes, encrypt directly
        aesgcm = AESGCM(master_key)
        iv = secrets.token_bytes(self.IV_LENGTH)

        ciphertext_with_tag = aesgcm.encrypt(iv, data_key, None)

        ciphertext = ciphertext_with_tag[:-16]
        auth_tag = ciphertext_with_tag[-16:]

        return {
            "iv": base64.b64encode(iv).decode(),
            "encrypted_data_key": base64.b64encode(ciphertext).decode(),
            "auth_tag": base64.b64encode(auth_tag).decode(),
        }

    def decrypt_data_key(
        self,
        encrypted_data_key: dict,
        master_key: bytes,
    ) -> bytes:
        """
        Decrypt a data key using the master key.

        Args:
            encrypted_data_key: Dict with iv, encrypted_data_key, auth_tag
            master_key: 32-byte master key

        Returns:
            Decrypted 32-byte data key
        """
        aesgcm = AESGCM(master_key)

        iv = base64.b64decode(encrypted_data_key["iv"])
        ciphertext = base64.b64decode(encrypted_data_key["encrypted_data_key"])
        auth_tag = base64.b64decode(encrypted_data_key["auth_tag"])

        ciphertext_with_tag = ciphertext + auth_tag

        try:
            data_key = aesgcm.decrypt(iv, ciphertext_with_tag, None)
            return data_key
        except Exception as e:
            logger.error(f"Data key decryption failed: {e}")
            raise ValueError(f"Data key decryption failed")

    def encrypt_secret(
        self,
        plaintext: str,
        master_key: bytes,
    ) -> dict:
        """
        Encrypt a secret using envelope encryption.

        1. Generate data key
        2. Encrypt secret with data key
        3. Encrypt data key with master key

        Args:
            plaintext: Secret value to encrypt
            master_key: 32-byte master key

        Returns:
            Dict with encrypted_data_key and encrypted_secret
        """
        # Generate data key
        data_key = self.generate_data_key()

        # Encrypt secret with data key
        encrypted_secret = self.encrypt_with_data_key(plaintext, data_key)

        # Encrypt data key with master key
        encrypted_data_key = self.encrypt_data_key(data_key, master_key)

        return {
            "encrypted_data_key": encrypted_data_key,
            "encrypted_secret": encrypted_secret,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def decrypt_secret(
        self,
        encrypted_data: dict,
        master_key: bytes,
    ) -> str:
        """
        Decrypt a secret using envelope decryption.

        1. Decrypt data key with master key
        2. Decrypt secret with data key

        Args:
            encrypted_data: Dict with encrypted_data_key and encrypted_secret
            master_key: 32-byte master key

        Returns:
            Decrypted secret string
        """
        # Decrypt data key
        data_key = self.decrypt_data_key(encrypted_data["encrypted_data_key"], master_key)

        # Decrypt secret with data key
        plaintext = self.decrypt_with_data_key(encrypted_data["encrypted_secret"], data_key)

        return plaintext


# Global secrets service instance
_secrets_service: Optional[SecretsService] = None


def get_secrets_service() -> SecretsService:
    """Get or create the secrets service instance"""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = SecretsService()
    return _secrets_service


def clear_secret_cache():
    """Clear all in-memory caches"""
    global _decrypted_cache, _master_key_cache, _master_key_metadata_cache
    _decrypted_cache = {}
    _master_key_cache = None
    _master_key_metadata_cache = None
    logger.info("Secret caches cleared")