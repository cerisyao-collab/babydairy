"""OSS Storage Service for secrets management

Provides functions to store and retrieve master key and encrypted secrets
from Alibaba Cloud OSS bucket.

OSS bucket uses SSE-OSS encryption (free, managed by Alibaba Cloud).
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import oss2

logger = logging.getLogger(__name__)

# OSS configuration from environment
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
OSS_SECRETS_BUCKET = os.environ.get("OSS_SECRETS_BUCKET", "")
OSS_ACCESS_KEY_ID = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")

# OSS object paths
MASTER_KEY_PATH = "master_key.json"
SECRETS_DIR = "secrets/"

# In-memory OSS bucket instance
_bucket_cache: Optional[oss2.Bucket] = None


def get_oss_bucket() -> oss2.Bucket:
    """
    Get OSS bucket instance for secrets storage.

    Uses FC execution role's access key.

    Returns:
        oss2.Bucket instance
    """
    global _bucket_cache

    if _bucket_cache is None:
        if not OSS_SECRETS_BUCKET:
            raise ValueError("OSS_SECRETS_BUCKET not configured")

        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        _bucket_cache = oss2.Bucket(auth, OSS_ENDPOINT, OSS_SECRETS_BUCKET)
        logger.info(f"OSS bucket initialized: {OSS_SECRETS_BUCKET}")

    return _bucket_cache


def upload_master_key_to_oss(
    master_key: bytes,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Upload master key to OSS bucket.

    The master key is stored as JSON with:
    - key: base64-encoded master key
    - created_at: timestamp
    - metadata: optional metadata

    Args:
        master_key: 32-byte master key
        metadata: Optional metadata dict

    Returns:
        Metadata dict with version info
    """
    bucket = get_oss_bucket()

    data = {
        "key": master_key.hex(),  # Store as hex string
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }

    result = bucket.put_object(
        MASTER_KEY_PATH,
        json.dumps(data).encode(),
    )

    logger.info(f"Master key uploaded, version: {result.versionid}")
    return {
        "path": MASTER_KEY_PATH,
        "version_id": result.versionid,
        "created_at": data["created_at"],
    }


def download_master_key_from_oss(
    version_id: Optional[str] = None,
) -> tuple[bytes, dict]:
    """
    Download master key from OSS bucket.

    Args:
        version_id: Optional specific version (for rollback)

    Returns:
        Tuple of (master_key_bytes, metadata_dict)

    Raises:
        ValueError: If master key not found
    """
    bucket = get_oss_bucket()

    params = {}
    if version_id:
        params["versionId"] = version_id

    try:
        result = bucket.get_object(MASTER_KEY_PATH, params=params)
        data = json.loads(result.read())

        master_key = bytes.fromhex(data["key"])
        metadata = {
            "version_id": result.versionid or version_id,
            "created_at": data.get("created_at"),
            "metadata": data.get("metadata", {}),
        }

        logger.info(f"Master key downloaded, version: {metadata['version_id']}")
        return master_key, metadata

    except oss2.exceptions.NoSuchKey:
        raise ValueError(f"Master key not found in OSS bucket: {OSS_SECRETS_BUCKET}")


def upload_encrypted_secret_to_oss(
    secret_name: str,
    encrypted_data: dict,
) -> dict:
    """
    Upload encrypted secret to OSS bucket.

    Args:
        secret_name: Name of the secret (e.g., "db_password")
        encrypted_data: Encrypted secret dict from secrets_service.encrypt_secret()

    Returns:
        Metadata dict with path and version
    """
    bucket = get_oss_bucket()

    path = f"{SECRETS_DIR}{secret_name}.json"

    result = bucket.put_object(
        path,
        json.dumps(encrypted_data).encode(),
    )

    logger.info(f"Secret '{secret_name}' uploaded, version: {result.versionid}")
    return {
        "path": path,
        "version_id": result.versionid,
        "secret_name": secret_name,
    }


def download_encrypted_secret_from_oss(
    secret_name: str,
    version_id: Optional[str] = None,
) -> dict:
    """
    Download encrypted secret from OSS bucket.

    Args:
        secret_name: Name of the secret
        version_id: Optional specific version

    Returns:
        Encrypted secret dict

    Raises:
        ValueError: If secret not found
    """
    bucket = get_oss_bucket()

    path = f"{SECRETS_DIR}{secret_name}.json"

    params = {}
    if version_id:
        params["versionId"] = version_id

    try:
        result = bucket.get_object(path, params=params)
        data = json.loads(result.read())

        data["_metadata"] = {
            "version_id": result.versionid or version_id,
            "path": path,
        }

        logger.info(f"Secret '{secret_name}' downloaded")
        return data

    except oss2.exceptions.NoSuchKey:
        raise ValueError(f"Secret '{secret_name}' not found in OSS bucket")


def list_secrets_in_oss() -> list[str]:
    """
    List all secret names in OSS bucket.

    Returns:
        List of secret names
    """
    bucket = get_oss_bucket()

    secrets = []
    for obj in oss2.ObjectIterator(bucket, prefix=SECRETS_DIR):
        if obj.key.endswith(".json") and obj.key != MASTER_KEY_PATH:
            # Extract secret name from path
            name = obj.key.replace(SECRETS_DIR, "").replace(".json", "")
            secrets.append(name)

    logger.info(f"Found {len(secrets)} secrets in OSS bucket")
    return secrets


def delete_secret_from_oss(secret_name: str) -> bool:
    """
    Delete a secret from OSS bucket.

    Note: With versioning enabled, this creates a delete marker.
    Old versions are still recoverable.

    Args:
        secret_name: Name of the secret to delete

    Returns:
        True if deleted successfully
    """
    bucket = get_oss_bucket()

    path = f"{SECRETS_DIR}{secret_name}.json"

    try:
        bucket.delete_object(path)
        logger.info(f"Secret '{secret_name}' deleted (versioned)")
        return True
    except oss2.exceptions.NoSuchKey:
        logger.warning(f"Secret '{secret_name}' not found, nothing to delete")
        return False


def get_master_key_versions() -> list[dict]:
    """
    Get all versions of the master key (for backup/rollback).

    Returns:
        List of version metadata dicts
    """
    bucket = get_oss_bucket()

    versions = []
    for version in oss2.ObjectVersionIterator(bucket, MASTER_KEY_PATH):
        versions.append({
            "version_id": version.versionid,
            "is_latest": version.islatest,
            "last_modified": version.lastmodified,
        })

    return versions


def clear_oss_cache():
    """Clear OSS bucket instance cache"""
    global _bucket_cache
    _bucket_cache = None