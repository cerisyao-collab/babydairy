#!/bin/bash
# OIDC authentication script for Alibaba Cloud
# Uses GitHub's OIDC token to assume RAM role via AssumeRoleWithOIDC API

set -e

ROLE_ARN="${ROLE_TO_ASSUME:-}"
OIDC_PROVIDER_ARN="${OIDC_PROVIDER_ARN:-}"
SESSION_NAME="${ROLE_SESSION_NAME:-github-actions-session}"
AUDIENCE="${OIDC_AUDIENCE:-github-actions}"
REGION="${ALIYUN_REGION:-cn-shanghai}"

# Validate required environment variables
if [ -z "$ROLE_ARN" ] || [ -z "$OIDC_PROVIDER_ARN" ]; then
  echo "Error: ROLE_TO_ASSUME and OIDC_PROVIDER_ARN must be set"
  exit 1
fi

# Get OIDC token from GitHub Actions environment
if [ -z "$ACTIONS_ID_TOKEN_REQUEST_TOKEN" ] || [ -z "$ACTIONS_ID_TOKEN_REQUEST_URL" ]; then
  echo "Error: This script must run in GitHub Actions environment"
  exit 1
fi

echo "Getting OIDC token from GitHub..."
OIDC_TOKEN=$(curl -sSL \
  -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
  "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=${AUDIENCE}" | jq -r '.value')

if [ -z "$OIDC_TOKEN" ] || [ "$OIDC_TOKEN" = "null" ]; then
  echo "Error: Failed to get OIDC token"
  exit 1
fi

echo "OIDC token obtained (length: ${#OIDC_TOKEN})"

# Call AssumeRoleWithOIDC API directly via HTTP
# This API does NOT require signature or Timestamp according to documentation
# But we'll include minimal required parameters
echo "Assuming role: $ROLE_ARN"

STS_ENDPOINT="https://sts.aliyuncs.com"  # Global endpoint

# Build request body for POST
RESPONSE=$(curl -sSL -X POST "$STS_ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Action=AssumeRoleWithOIDC" \
  -d "Version=2015-04-01" \
  -d "Format=JSON" \
  -d "RoleArn=$ROLE_ARN" \
  -d "OIDCProviderArn=$OIDC_PROVIDER_ARN" \
  -d "OIDCToken=$OIDC_TOKEN" \
  -d "RoleSessionName=$SESSION_NAME" \
  -d "DurationSeconds=3600")

# Check for error
if echo "$RESPONSE" | jq -e '.Error' > /dev/null 2>&1; then
  echo "Error: API call failed"
  echo "$RESPONSE" | jq '.'
  exit 1
fi

# Parse credentials from response
ACCESS_KEY_ID=$(echo "$RESPONSE" | jq -r '.Credentials.AccessKeyId')
ACCESS_KEY_SECRET=$(echo "$RESPONSE" | jq -r '.Credentials.AccessKeySecret')
SECURITY_TOKEN=$(echo "$RESPONSE" | jq -r '.Credentials.SecurityToken')
EXPIRATION=$(echo "$RESPONSE" | jq -r '.Credentials.Expiration')

if [ -z "$ACCESS_KEY_ID" ] || [ "$ACCESS_KEY_ID" = "null" ]; then
  echo "Error: Failed to get credentials"
  echo "Response: $RESPONSE"
  exit 1
fi

echo "Credentials obtained successfully"
echo "Expiration: $EXPIRATION"

# Initialize aliyun CLI config with obtained credentials
mkdir -p ~/.aliyun
cat > ~/.aliyun/config.json << EOF
{
  "current": "default",
  "profiles": [
    {
      "name": "default",
      "mode": "StsToken",
      "access_key_id": "$ACCESS_KEY_ID",
      "access_key_secret": "$ACCESS_KEY_SECRET",
      "sts_token": "$SECURITY_TOKEN",
      "region_id": "$REGION",
      "output_format": "json",
      "language": "en"
    }
  ]
}
EOF

# Set environment variables for other tools
export ALIYUN_ACCESS_KEY_ID="$ACCESS_KEY_ID"
export ALIYUN_ACCESS_KEY_SECRET="$ACCESS_KEY_SECRET"
export ALIYUN_SECURITY_TOKEN="$SECURITY_TOKEN"

export ALICLOUD_ACCESS_KEY="$ACCESS_KEY_ID"
export ALICLOUD_SECRET_KEY="$ACCESS_KEY_SECRET"
export ALICLOUD_SECURITY_TOKEN="$SECURITY_TOKEN"

# Mask secrets in GitHub Actions output
echo "::add-mask::$ACCESS_KEY_ID"
echo "::add-mask::$ACCESS_KEY_SECRET"
echo "::add-mask::$SECURITY_TOKEN"

echo "Alibaba Cloud OIDC authentication completed successfully"