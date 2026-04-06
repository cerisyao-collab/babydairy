## Context

### 当前架构问题

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     当前部署流程 (存在安全风险)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   GitHub Actions / 开发者机器                                           │
│   ┌──────────────────────────────────────────┐                         │
│   │  长期密钥 (永不过期!)                     │                         │
│   │                                          │                         │
│   │  ALICLOUD_ACCESS_KEY=LTAI...             │                         │
│   │  ALICLOUD_SECRET_KEY=abc123...           │                         │
│   │                                          │                         │
│   │  ⚠️ 风险:                                │                         │
│   │  - 泄露后攻击者永久有效                   │                         │
│   │  - 权限通常过大                          │                         │
│   │  - 难以审计是谁的操作                     │                         │
│   └──────────────────────────────────────────┘                         │
│                      │                                                  │
│                      ▼                                                  │
│   ┌──────────────────────────────────────────┐                         │
│   │         阿里云 RAM User (AK 所属)         │                         │
│   │                                          │                         │
│   │  权限: AdministratorAccess (过大!)       │                         │
│   └──────────────────────────────────────────┘                         │
│                      │                                                  │
│                      ▼                                                  │
│   ┌──────────────────────────────────────────┐                         │
│   │           阿里云资源                      │                         │
│   │  RDS / FC / OSS / VPC / ...              │                         │
│   └──────────────────────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 目标架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     OIDC + RAM 角色架构 (安全)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │                    GitHub Actions                       │          │
│   │                                                         │          │
│   │  ① 请求 OIDC Token                                      │          │
│   │     GET https://token.actions.githubusercontent.com     │          │
│   │     返回: JWT Token (含 repo, actor, branch 等声明)      │          │
│   │                                                         │          │
│   └──────────────────────────┬──────────────────────────────┘          │
│                              │                                         │
│                              │ ② 携带 OIDC Token 调用                   │
│                              │    aliyun sts AssumeRole                 │
│                              ▼                                         │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │               阿里云 STS (Security Token Service)        │          │
│   │                                                         │          │
│   │  ③ 验证 OIDC Token:                                     │          │
│   │     - 签名验证 (GitHub 公钥)                             │          │
│   │     - issuer 验证                                        │          │
│   │     - aud 验证                                           │          │
│   │     - 条件验证 (repo, branch 等)                         │          │
│   │                                                         │          │
│   │  ④ 签发临时凭证 (有效期: 1-12 小时)                       │          │
│   │     AccessKeyId + AccessKeySecret + SecurityToken        │          │
│   │                                                         │          │
│   └──────────────────────────┬──────────────────────────────┘          │
│                              │                                         │
│                              │ 临时凭证 (自动过期)                       │
│                              ▼                                         │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │               RAM 角色 (最小权限)                        │          │
│   │                                                         │          │
│   │  ┌─────────────────────┐   ┌─────────────────────┐      │          │
│   │  │ terraform-deploy    │   │ fc-deploy           │      │          │
│   │  │ (基础设施管理)       │   │ (FC 函数部署)       │      │          │
│   │  │                     │   │                     │      │          │
│   │  │ - VPC 读写          │   │ - FC 读写           │      │          │
│   │  │ - RDS 读写          │   │ - OSS 特定 bucket   │      │          │
│   │  │ - OSS 读写          │   │ - 日志写入          │      │          │
│   │  │ - RAM 部分权限      │   │                     │      │          │
│   │  └─────────────────────┘   └─────────────────────┘      │          │
│   │                                                         │          │
│   └─────────────────────────────────────────────────────────┘          │
│                              │                                         │
│                              ▼                                         │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │                    阿里云资源                            │          │
│   │  RDS / FC / OSS / VPC / ...                             │          │
│   └─────────────────────────────────────────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Goals / Non-Goals

**Goals:**
- 实现无长期密钥部署（GitHub Actions 使用 OIDC）
- 创建最小权限 RAM 角色（分离基础设施部署和应用部署）
- 支持细粒度权限控制（仓库/分支级别）
- 提供本地开发的安全替代方案
- 完整的审计追踪能力

**Non-Goals:**
- 不修改现有业务代码
- 不改变现有基础设施架构
- 不实现多账户/多环境隔离（后续扩展）

## Decisions

### 1. OIDC Provider 配置

**决策: 使用阿里云 RAM OIDC Provider 连接 GitHub Actions**

GitHub OIDC Token 声明 (Claims):
```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "aud": "github-actions",
  "sub": "repo:your-org/babyjour:ref:refs/heads/main",
  "actor": "your-username",
  "repository": "your-org/babyjour",
  "ref": "refs/heads/main",
  "workflow": "deploy",
  "event_name": "push"
}
```

关键配置:
- `issuer`: `https://token.actions.githubusercontent.com`
- `aud`: `github-actions` (固定值)
- `sub`: 用于限制仓库和分支

实现方式:
```hcl
# terraform/oidc.tf

# OIDC Provider for GitHub Actions
resource "alicloud_ram_oidc_provider" "github" {
  provider_name            = "github-actions"
  client_id                = "github-actions"
  issuer                   = "https://token.actions.githubusercontent.com"
  issuer_url_without_path = "https://token.actions.githubusercontent.com"
  
  # GitHub OIDC 公钥 (用于验证 Token 签名)
  # 可从 https://token.actions.githubusercontent.com/.well-known/jwks 获取
  fingerprints = [
    "a031c46782e6e6c662c2c87d76ae3934e0f7d2e6c55f8b1c7f8e9d0a1b2c3d4e5"
  ]
  
  description = "GitHub Actions OIDC Provider for Baby Diary deployment"
}
```

### 2. RAM 角色设计

**决策: 创建两个独立角色，职责分离**

#### 角色 1: Terraform Deploy Role (基础设施部署)

```hcl
# terraform/roles.tf

# Terraform 部署角色
resource "alicloud_ram_role" "terraform_deploy" {
  name        = "terraform-deploy"
  description = "Role for Terraform to manage infrastructure"
  
  document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        OIDC = [alicloud_ram_oidc_provider.github.arn]
      }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "github-actions"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:your-org/babyjour:*"
        }
      }
    }]
    Version = "1"
  })
}

# 附加最小权限策略
resource "alicloud_ram_role_policy_attachment" "terraform_deploy" {
  role_name   = alicloud_ram_role.terraform_deploy.name
  policy_name = alicloud_ram_policy.terraform_deploy.name
}
```

#### 角色 2: FC Deploy Role (应用部署)

```hcl
# FC 部署角色
resource "alicloud_ram_role" "fc_deploy" {
  name        = "fc-deploy"
  description = "Role for FC function deployment"
  
  document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        OIDC = [alicloud_ram_oidc_provider.github.arn]
      }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "github-actions"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:your-org/babyjour:*"
        }
      }
    }]
    Version = "1"
  })
}
```

### 3. 最小权限策略

**决策: 精细划分权限，遵循最小权限原则**

```hcl
# terraform/policies.tf

# Terraform 部署策略 - 仅允许管理特定资源
resource "alicloud_ram_policy" "terraform_deploy" {
  policy_name     = "terraform-deploy-policy"
  policy_document = jsonencode({
    Statement = [
      # VPC 权限
      {
        Effect = "Allow"
        Action = [
          "vpc:CreateVpc", "vpc:DeleteVpc", "vpc:DescribeVpcs", "vpc:ModifyVpcAttribute",
          "vpc:CreateVSwitch", "vpc:DeleteVSwitch", "vpc:DescribeVSwitches",
          "vpc:CreateSecurityGroup", "vpc:DeleteSecurityGroup", "vpc:DescribeSecurityGroups",
          "vpc:AuthorizeSecurityGroup", "vpc:RevokeSecurityGroup",
        ]
        Resource = ["*"]
      },
      # RDS 权限 (仅限项目数据库)
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBInstance", "rds:DeleteDBInstance", "rds:DescribeDBInstances",
          "rds:CreateDatabase", "rds:DeleteDatabase", "rds:DescribeDatabases",
          "rds:CreateAccount", "rds:DeleteAccount", "rds:DescribeAccounts",
        ]
        Resource = ["acs:rds:*:*:dbinstance/*"]
        Condition = {
          StringLike = {
            "rds:DBInstanceName" = "baby-diary-*"
          }
        }
      },
      # OSS 权限 (仅限项目 bucket)
      {
        Effect = "Allow"
        Action = [
          "oss:CreateBucket", "oss:DeleteBucket", "oss:GetBucketInfo", "oss:ListBuckets",
          "oss:PutObject", "oss:GetObject", "oss:DeleteObject", "oss:ListObjects",
        ]
        Resource = [
          "acs:oss:*:*:baby-diary-*",
          "acs:oss:*:*:baby-diary-*/*",
        ]
      },
      # RAM 权限 (仅限创建服务角色)
      {
        Effect = "Allow"
        Action = [
          "ram:CreateRole", "ram:DeleteRole", "ram:GetRole", "ram:ListRoles",
          "ram:CreatePolicy", "ram:DeletePolicy", "ram:GetPolicy",
          "ram:AttachPolicyToRole", "ram:DetachPolicyFromRole",
        ]
        Resource = [
          "acs:ram:*:*:role/baby-diary-*",
          "acs:ram:*:*:policy/baby-diary-*",
        ]
      },
      # FC 权限
      {
        Effect = "Allow"
        Action = [
          "fc:CreateService", "fc:DeleteService", "fc:GetService", "fc:UpdateService",
          "fc:CreateFunction", "fc:DeleteFunction", "fc:GetFunction", "fc:UpdateFunction",
          "fc:CreateTrigger", "fc:DeleteTrigger", "fc:GetTrigger",
        ]
        Resource = ["acs:fc:*:*:services/baby-diary-*"]
      },
    ]
    Version = "1"
  })
  description = "Minimal permissions for Terraform to manage Baby Diary infrastructure"
}

# FC 部署策略
resource "alicloud_ram_policy" "fc_deploy" {
  policy_name     = "fc-deploy-policy"
  policy_document = jsonencode({
    Statement = [
      # FC 函数操作
      {
        Effect = "Allow"
        Action = [
          "fc:GetService", "fc:UpdateService",
          "fc:GetFunction", "fc:UpdateFunction", "fc:InvokeFunction",
        ]
        Resource = ["acs:fc:*:*:services/baby-diary-*"]
      },
      # OSS 凭证读取
      {
        Effect = "Allow"
        Action = ["oss:GetObject"]
        Resource = [
          "acs:oss:*:*:baby-diary-secrets",
          "acs:oss:*:*:baby-diary-secrets/*",
        ]
      },
      # 日志写入
      {
        Effect = "Allow"
        Action = ["log:PostLogStoreLogs"]
        Resource = ["acs:log:*:*:project/baby-diary-*"]
      },
    ]
    Version = "1"
  })
  description = "Minimal permissions for FC deployment"
}

# FC 运行时角色 (函数执行时使用)
resource "alicloud_ram_role" "fc_execution" {
  name        = "baby-diary-fc-execution"
  description = "Role assumed by FC function at runtime"
  
  document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = ["fc.aliyuncs.com"]
      }
    }]
    Version = "1"
  })
}
```

### 4. GitHub Actions 工作流

**决策: 使用官方 aliyun/configure-credentials-action**

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write  # 允许获取 OIDC token
  contents: read

jobs:
  deploy-infrastructure:
    name: Deploy Infrastructure (Terraform)
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Configure Aliyun Credentials (Terraform)
        uses: aliyun/configure-credentials-action@v1
        with:
          role-arn: ${{ secrets.TERRAFORM_DEPLOY_ROLE_ARN }}
          oidc-provider-arn: ${{ secrets.OIDC_PROVIDER_ARN }}
          role-session-name: terraform-deploy-${{ github.run_id }}
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"
      
      - name: Terraform Init
        run: terraform init
        working-directory: terraform
      
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: terraform
      
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve tfplan
        working-directory: terraform

  deploy-function:
    name: Deploy FC Function
    runs-on: ubuntu-latest
    needs: deploy-infrastructure
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Configure Aliyun Credentials (FC)
        uses: aliyun/configure-credentials-action@v1
        with:
          role-arn: ${{ secrets.FC_DEPLOY_ROLE_ARN }}
          oidc-provider-arn: ${{ secrets.OIDC_PROVIDER_ARN }}
          role-session-name: fc-deploy-${{ github.run_id }}
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install Serverless Devs
        run: npm install -g @serverless-devs/s
      
      - name: Deploy FC Function
        run: s deploy
        env:
          VPC_ID: ${{ secrets.VPC_ID }}
          VSWITCH_ID: ${{ secrets.VSWITCH_ID }}
          SECURITY_GROUP_ID: ${{ secrets.SECURITY_GROUP_ID }}
          OSS_SECRETS_BUCKET: ${{ secrets.OSS_SECRETS_BUCKET }}
```

### 5. 本地开发方案

**决策: 使用 aliyun CLI + RAM 用户 (临时凭证)**

```bash
# 方案 1: 使用 aliyun CLI 登录 (推荐)
aliyun configure --mode OIDC

# 或使用浏览器登录
aliyun configure --mode Browser

# 方案 2: 使用 AssumeRole (需要创建开发角色)
aliyun sts AssumeRole \
  --RoleArn acs:ram::ACCOUNT_ID:role/developer \
  --RoleSessionName local-dev-$(whoami)

# 临时凭证自动写入环境变量或配置文件
```

开发角色配置:
```hcl
# 开发者角色 (需要 MFA)
resource "alicloud_ram_role" "developer" {
  name        = "developer"
  description = "Role for local development"
  
  document = jsonencode({
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          RAM = ["acs:ram::*:root"]
        }
        Condition = {
          Bool = {
            "acs:MFAPresent" = "true"  # 要求 MFA
          }
        }
      }
    ]
    Version = "1"
  })
}
```

### 6. 分支级别权限控制

**决策: 通过 OIDC sub 条件限制分支**

```hcl
# 仅允许 main 分支部署到生产环境
resource "alicloud_ram_role" "terraform_deploy_production" {
  name = "terraform-deploy-production"
  
  document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        OIDC = [alicloud_ram_oidc_provider.github.arn]
      }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "github-actions"
        }
        StringLike = {
          # 仅允许 main 分支
          "token.actions.githubusercontent.com:sub" = "repo:your-org/babyjour:ref:refs/heads/main"
        }
      }
    }]
    Version = "1"
  })
}

# 允许所有分支部署到开发环境
resource "alicloud_ram_role" "terraform_deploy_development" {
  name = "terraform-deploy-development"
  
  document = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        OIDC = [alicloud_ram_oidc_provider.github.arn]
      }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "github-actions"
        }
        StringLike = {
          # 允许任意分支
          "token.actions.githubusercontent.com:sub" = "repo:your-org/babyjour:*"
        }
      }
    }]
    Version = "1"
  })
}
```

## Risks / Trade-offs

### Risk 1: OIDC Provider 配置错误导致无法部署
→ **Mitigation**: 先在测试仓库验证 OIDC 配置，再迁移到生产仓库

### Risk 2: 权限过于严格导致部署失败
→ **Mitigation**: 初始使用较宽松策略，逐步收紧；保留回滚方案

### Risk 3: GitHub Actions 不可用
→ **Mitigation**: 保留本地部署脚本作为备用方案

### Risk 4: OIDC Token 被窃取
→ **Mitigation**: OIDC Token 有效期仅约 5-10 分钟，且绑定特定仓库/分支

### Trade-off: 初始配置复杂度增加
→ **Acceptance**: 一次性配置成本换取长期安全性提升

## Migration Plan

### Phase 1: 创建 OIDC 基础设施 (一次性)

```bash
# 1. 使用现有 AK 创建 OIDC Provider 和角色
cd terraform
terraform plan -target=alicloud_ram_oidc_provider.github
terraform apply -target=alicloud_ram_oidc_provider.github

# 2. 创建部署角色
terraform plan -target=alicloud_ram_role.terraform_deploy
terraform apply -target=alicloud_ram_role.terraform_deploy
```

### Phase 2: 配置 GitHub Actions

```bash
# 1. 在 GitHub 仓库设置 Secrets
# - TERRAFORM_DEPLOY_ROLE_ARN
# - FC_DEPLOY_ROLE_ARN
# - OIDC_PROVIDER_ARN

# 2. 创建 .github/workflows/deploy.yml
# 3. 推送测试
git push origin main
```

### Phase 3: 移除长期 AK

```bash
# 1. 确认 OIDC 部署正常工作
# 2. 禁用/删除长期 AccessKey
# 3. 删除 GitHub Secrets 中的 AK (如有)
```

### Phase 4: 本地开发配置

```bash
# 1. 配置 aliyun CLI
aliyun configure --mode Browser

# 2. 验证可以 AssumeRole
aliyun sts AssumeRole --RoleArn ...
```

## Open Questions

1. **OIDC Provider 指纹获取**: GitHub OIDC 公钥指纹如何正确获取？需要进一步验证
2. **多环境隔离**: 是否需要为 dev/staging/prod 创建独立的角色？
3. **审批流程**: 生产部署是否需要 GitHub branch protection + required reviewers？