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

# Extract OIDC Provider name from ARN
OIDC_PROVIDER_NAME=$(echo "$OIDC_PROVIDER_ARN" | rev | cut -d'/' -f1 | rev)

# Call AssumeRoleWithOIDC API
echo "Assuming role: $ROLE_ARN"
ASSUME_RESULT=$(aliyun sts AssumeRoleWithOIDC \
  --RoleArn "$ROLE_ARN" \
  --OIDCProviderArn "$OIDC_PROVIDER_ARN" \
  --OIDCToken "$OIDC_TOKEN" \
  --RoleSessionName "$SESSION_NAME" \
  --DurationSeconds 3600)

# Parse credentials from response
ACCESS_KEY_ID=$(echo "$ASSUME_RESULT" | jq -r '.Credentials.AccessKeyId')
ACCESS_KEY_SECRET=$(echo "$ASSUME_RESULT" | jq -r '.Credentials.AccessKeySecret')
SECURITY_TOKEN=$(echo "$ASSUME_RESULT" | jq -r '.Credentials.SecurityToken')
EXPIRATION=$(echo "$ASSUME_RESULT" | jq -r '.Credentials.Expiration')

if [ -z "$ACCESS_KEY_ID" ] || [ "$ACCESS_KEY_ID" = "null" ]; then
  echo "Error: Failed to get credentials"
  echo "Response: $ASSUME_RESULT"
  exit 1
fi

echo "Credentials obtained successfully"
echo "Expiration: $EXPIRATION"

# Configure aliyun CLI with temporary credentials
aliyun configure set \
  --access-key-id "$ACCESS_KEY_ID" \
  --access-key-secret "$ACCESS_KEY_SECRET" \
  --sts-token "$SECURITY_TOKEN" \
  --region "$REGION"

# Also export as environment variables for other tools
export ALIYUN_ACCESS_KEY_ID="$ACCESS_KEY_ID"
export ALIYUN_ACCESS_KEY_SECRET="$ACCESS_KEY_SECRET"
export ALIYUN_SECURITY_TOKEN="$SECURITY_TOKEN"

echo "::add-mask::$ACCESS_KEY_ID"
echo "::add-mask::$ACCESS_KEY_SECRET"
echo "::add-mask::$SECURITY_TOKEN"

echo "Alibaba Cloud OIDC authentication completed successfully"