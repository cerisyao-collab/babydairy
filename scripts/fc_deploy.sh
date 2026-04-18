#!/bin/bash
# Generate s.yaml with actual VPC values for FC deployment
# This works around Serverless Devs env var resolution issues in YAML arrays

set -e

VPC_ID="${VPC_ID:?VPC_ID is required}"
VSWITCH_ID="${VSWITCH_ID:?VSWITCH_ID is required}"
SECURITY_GROUP_ID="${SECURITY_GROUP_ID:?SECURITY_GROUP_ID is required}"
DATABASE_URL="${DATABASE_URL:?DATABASE_URL is required}"
OSS_SECRETS_BUCKET="${OSS_SECRETS_BUCKET:?OSS_SECRETS_BUCKET is required}"
OSS_ENDPOINT="${OSS_ENDPOINT:-oss-cn-shanghai.aliyuncs.com}"

cat > s.yaml.deploy << EOF
edition: 1.0.0
name: baby-diary-api
access: default

services:
  baby-diary-api:
    component: fc
    props:
      region: cn-shanghai
      service:
        name: baby-diary-service
        description: Baby Diary API Service
        internetAccess: true
        vpcConfig:
          vpcId: ${VPC_ID}
          securityGroupId: ${SECURITY_GROUP_ID}
          vswitchIds:
            - ${VSWITCH_ID}
      function:
        name: api
        description: Baby Diary API Function
        runtime: python3.9
        codeUri: ./
        handler: src.api.index.handler
        memorySize: 256
        timeout: 30
        environmentVariables:
          DATABASE_URL: ${DATABASE_URL}
          WECHAT_APP_ID: ${WECHAT_APP_ID:-}
          WECHAT_APP_SECRET: ${WECHAT_APP_SECRET:-}
          JWT_SECRET: ${JWT_SECRET:-}
          JWT_ALGORITHM: HS256
          JWT_EXPIRE_MINUTES: "10080"
        instanceConcurrency: 1
        instanceType: e1
      triggers:
        - name: httpTrigger
          type: http
          config:
            authType: anonymous
            methods:
              - GET
              - POST
              - PUT
              - DELETE
              - OPTIONS
              - HEAD
              - PATCH
EOF

echo "Generated s.yaml.deploy with VPC config"
echo "=== s.yaml.deploy contents ==="
cat s.yaml.deploy
echo "=============================="

# Backup original s.yaml and use the generated one
mv s.yaml s.yaml.orig
mv s.yaml.deploy s.yaml
s deploy
# Restore original
mv s.yaml.orig s.yaml
