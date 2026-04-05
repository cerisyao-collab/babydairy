#!/usr/bin/env python3
"""
OIDC authentication script for Alibaba Cloud
Uses GitHub's OIDC token to assume RAM role via AssumeRoleWithOIDC API
"""

import json
import os
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone

def get_oidc_token():
    """Get OIDC token from GitHub Actions"""
    request_token = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    request_url = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
    audience = os.environ.get('OIDC_AUDIENCE', 'github-actions')

    if not request_token or not request_url:
        raise Exception("This script must run in GitHub Actions environment")

    url = f"{request_url}&audience={audience}"
    req = urllib.request.Request(url, headers={'Authorization': f'bearer {request_token}'})

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        token = data.get('value')

    if not token:
        raise Exception("Failed to get OIDC token")

    print(f"OIDC token obtained (length: {len(token)})")
    return token

def assume_role_with_oidc(token, role_arn, oidc_provider_arn, session_name, region):
    """Call AssumeRoleWithOIDC API using aliyun CLI with OIDC mode"""
    # Create temporary OIDC token file
    token_file = '/tmp/oidc_token.txt'
    with open(token_file, 'w') as f:
        f.write(token)

    # Use aliyun CLI with OIDC mode (configure first)
    # Create a minimal profile for OIDC
    config = {
        "current": "default",
        "profiles": [{
            "name": "default",
            "mode": "OIDC",
            "oidc_provider_arn": oidc_provider_arn,
            "oidc_token_file": token_file,
            "ram_role_arn": role_arn,
            "ram_session_name": session_name,
            "expired_seconds": 3600,
            "region_id": region,
            "output_format": "json",
            "language": "en"
        }]
    }

    config_path = os.path.expanduser('~/.aliyun/config.json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Assuming role: {role_arn}")

    # Test credentials by calling a simple API
    result = subprocess.run(
        ['aliyun', 'sts', 'GetCallerIdentity', '--region', region],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # OIDC mode might not work, try direct STS call
        print("OIDC mode failed, trying direct API call...")

        # Clean up and create AK profile with obtained credentials
        # We need to call AssumeRoleWithOIDC directly
        import hashlib
        import base64
        import hmac
        import time

        # Build canonicalized query string
        params = {
            'Action': 'AssumeRoleWithOIDC',
            'Version': '2015-04-01',
            'Format': 'JSON',
            'RegionId': region,
            'Timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'SignatureNonce': str(time.time_ns()),
            'RoleArn': role_arn,
            'OIDCProviderArn': oidc_provider_arn,
            'OIDCToken': token,
            'RoleSessionName': session_name,
            'DurationSeconds': '3600'
        }

        # For AssumeRoleWithOIDC, no signature needed - it's an anonymous API
        # But we need to send it properly

        endpoint = f"https://sts.{region}.aliyuncs.com"
        query_string = urllib.parse.urlencode(sorted(params.items()))

        url = f"{endpoint}?{query_string}"
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if 'Error' in data:
            raise Exception(f"API error: {data['Error']['Message']}")

        creds = data.get('Credentials', {})
        access_key_id = creds.get('AccessKeyId')
        access_key_secret = creds.get('AccessKeySecret')
        security_token = creds.get('SecurityToken')

        if not access_key_id:
            raise Exception(f"Failed to get credentials: {data}")

        print(f"Credentials obtained successfully")

        # Update config with obtained credentials
        config['profiles'][0] = {
            "name": "default",
            "mode": "StsToken",
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret,
            "sts_token": security_token,
            "region_id": region,
            "output_format": "json",
            "language": "en"
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Set environment variables
        os.environ['ALIYUN_ACCESS_KEY_ID'] = access_key_id
        os.environ['ALIYUN_ACCESS_KEY_SECRET'] = access_key_secret
        os.environ['ALIYUN_SECURITY_TOKEN'] = security_token
        os.environ['ALICLOUD_ACCESS_KEY'] = access_key_id
        os.environ['ALICLOUD_SECRET_KEY'] = access_key_secret
        os.environ['ALICLOUD_SECURITY_TOKEN'] = security_token

        # Mask secrets in GitHub Actions
        print(f"::add-mask::{access_key_id}")
        print(f"::add-mask::{access_key_secret}")
        print(f"::add-mask::{security_token}")

        print("Alibaba Cloud OIDC authentication completed successfully")
        return

def main():
    role_arn = os.environ.get('ROLE_TO_ASSUME')
    oidc_provider_arn = os.environ.get('OIDC_PROVIDER_ARN')
    session_name = os.environ.get('ROLE_SESSION_NAME', 'github-actions-session')
    region = os.environ.get('ALIYUN_REGION', 'cn-shanghai')

    if not role_arn or not oidc_provider_arn:
        raise Exception("ROLE_TO_ASSUME and OIDC_PROVIDER_ARN must be set")

    print("Getting OIDC token from GitHub...")
    token = get_oidc_token()

    assume_role_with_oidc(token, role_arn, oidc_provider_arn, session_name, region)

if __name__ == '__main__':
    main()