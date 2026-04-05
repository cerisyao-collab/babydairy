# 部署安全指南

本文档说明如何使用 OIDC + RAM 角色进行安全部署，避免使用长期有效的 AccessKey。

## 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                     OIDC 安全部署架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   GitHub Actions                                                │
│   ┌──────────────────────────────────┐                         │
│   │  ① OIDC Token (自动, 5-10分钟)    │                         │
│   └───────────────┬──────────────────┘                         │
│                     │                                           │
│                     ▼                                           │
│   ┌──────────────────────────────────┐                         │
│   │  ② STS AssumeRole                │                         │
│   │     交换临时凭证                   │                         │
│   └───────────────┬──────────────────┘                         │
│                     │                                           │
│                     ▼                                           │
│   ┌──────────────────────────────────┐                         │
│   │  ③ 临时凭证 (1-12小时自动过期)    │                         │
│   └──────────────────────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 前置条件

1. **阿里云账号**: 需要有 RAM 管理权限
2. **GitHub 仓库**: 需要配置仓库 Secrets
3. **OIDC Provider**: 已通过 Terraform 创建

## 配置步骤

### 步骤 1: 获取 GitHub OIDC 公钥指纹

```bash
# 获取 GitHub OIDC 配置
curl -s https://token.actions.githubusercontent.com/.well-known/openid-configuration | jq -r '.jwks_uri'

# 获取 JWKS
curl -s https://token.actions.githubusercontent.com/.well-known/jwks | jq '.keys[].x5c[]' -r

# 计算指纹 (对于每个证书)
echo "-----BEGIN CERTIFICATE-----" > cert.pem
echo "<certificate_content>" >> cert.pem
echo "-----END CERTIFICATE-----" >> cert.pem
openssl x509 -in cert.pem -fingerprint -noout | cut -d= -f2 | tr -d ':'
```

### 步骤 2: 配置 Terraform 变量

编辑 `terraform/terraform.tfvars`:

```hcl
github_oidc_fingerprints = [
  "a0sha1fingerprint...",  # 替换为实际指纹
  "anotherfingerprint...",  # GitHub 可能有多个密钥
]

github_repository = "your-org/babyjour"  # 你的 GitHub 仓库
```

### 步骤 3: 应用 Terraform

```bash
cd terraform

# 首次需要使用现有 AK
export ALICLOUD_ACCESS_KEY="your-access-key"
export ALICLOUD_SECRET_KEY="your-secret-key"

# 应用 OIDC 配置
terraform init
terraform apply -target=alicloud_ram_oidc_provider.github
terraform apply
```

### 步骤 4: 获取角色 ARN

```bash
# 输出角色 ARN
terraform output terraform_deploy_role_arn
terraform output fc_deploy_role_arn
terraform output oidc_provider_arn
```

### 步骤 5: 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets:

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `TERRAFORM_DEPLOY_ROLE_ARN` | `acs:ram::xxx:role/baby-diary-terraform-deploy` | Terraform 部署角色 |
| `FC_DEPLOY_ROLE_ARN` | `acs:ram::xxx:role/baby-diary-fc-deploy` | FC 部署角色 |
| `OIDC_PROVIDER_ARN` | `acs:ram::xxx:oidc-provider/github-actions` | OIDC Provider |
| `VPC_ID` | `vpc-xxx` | VPC ID |
| `VSWITCH_ID` | `vsw-xxx` | VSwitch ID |
| `SECURITY_GROUP_ID` | `sg-xxx` | 安全组 ID |
| `OSS_SECRETS_BUCKET` | `baby-diary-secrets` | OSS 凭证 bucket |
| `OSS_ENDPOINT` | `oss-cn-hangzhou.aliyuncs.com` | OSS 端点 |

### 步骤 6: 触发部署

```bash
# 推送到 main 分支自动触发
git push origin main

# 或手动触发
# GitHub Actions -> Deploy -> Run workflow
```

## 本地开发配置

### 方式 1: 浏览器登录 (推荐)

```bash
# 安装 aliyun CLI
brew install aliyun-cli

# 使用浏览器登录
aliyun configure --mode Browser

# 配置完成后，临时凭证会自动存储
```

### 方式 2: AssumeRole

```bash
# 先登录获取基础凭证
aliyun configure

# 获取临时凭证
aliyun sts AssumeRole \
  --RoleArn acs:ram::ACCOUNT_ID:role/baby-diary-developer \
  --RoleSessionName local-dev-$(whoami) \
  --DurationSeconds 3600

# 设置环境变量
export ALICLOUD_ACCESS_KEY="<TemporaryAccessKeyId>"
export ALICLOUD_SECRET_KEY="<TemporaryAccessKeySecret>"
export ALICLOUD_SECURITY_TOKEN="<SecurityToken>"
```

### 方式 3: 使用 aliyun CLI 执行命令

```bash
# 直接使用角色执行命令
aliyun fc GetService \
  --ServiceName baby-diary-service \
  --role-arn acs:ram::ACCOUNT_ID:role/baby-diary-developer
```

## 角色权限说明

### terraform-deploy 角色

用于基础设施部署，权限包括：
- VPC 创建/删除/修改
- RDS 实例管理
- OSS bucket 管理
- FC 服务管理
- RAM 角色创建（仅限 baby-diary-* 前缀）

### fc-deploy 角色

用于 FC 函数部署，权限包括：
- FC 函数更新（仅限 baby-diary-* 服务）
- OSS 凭证读取
- 日志写入

### fc-execution 角色

FC 运行时角色，权限包括：
- OSS 凭证读取
- 日志写入

### developer 角色

本地开发角色，权限包括：
- 所有资源的只读访问
- 开发环境资源的写访问
- **需要 MFA 认证**

## 安全最佳实践

### 1. 定期轮换密钥

虽然 OIDC 不使用长期密钥，但如果有其他 AccessKey，应定期轮换：

```bash
# 创建新 AK
aliyun ram CreateAccessKey --UserName <username>

# 禁用旧 AK
aliyun ram UpdateAccessKey --UserAccessKeyId <old-key-id> --Status Inactive
```

### 2. 审计日志

查看 AssumeRole 操作日志：

```bash
aliyun actiontrail LookupEvents \
  --EventName AssumeRole \
  --StartTime "2024-01-01T00:00:00Z" \
  --EndTime "2024-01-31T23:59:59Z"
```

### 3. 限制分支部署

生产环境部署限制在 main 分支：

```hcl
# terraform/roles.tf
Condition = {
  StringLike = {
    "token.actions.githubusercontent.com:sub" = "repo:org/repo:ref:refs/heads/main"
  }
}
```

## 故障排除

### 问题 1: OIDC Token 验证失败

```
Error: OIDC token validation failed
```

**解决方案**:
1. 检查 OIDC Provider 指纹是否正确
2. 确认 GitHub 仓库配置正确
3. 检查 OIDC Provider 是否已创建

### 问题 2: AssumeRole 被拒绝

```
Error: Access denied when assuming role
```

**解决方案**:
1. 确认角色信任策略中的仓库路径正确
2. 检查 `aud` 条件是否为 `github-actions`
3. 确认 OIDC Provider ARN 正确

### 问题 3: 权限不足

```
Error: User has no permission to perform action
```

**解决方案**:
1. 检查角色附加的策略
2. 确认资源名称匹配（baby-diary-* 前缀）
3. 查看审计日志确认具体缺失的权限

### 问题 4: 本地开发 MFA 要求

```
Error: MFA required
```

**解决方案**:
确保先通过 MFA 认证：

```bash
# 使用浏览器登录会自动处理 MFA
aliyun configure --mode Browser
```

## 回滚方案

如果 OIDC 部署失败，可以临时使用 AccessKey：

1. 创建临时 AccessKey：
```bash
aliyun ram CreateAccessKey --UserName deploy-user
```

2. 设置 GitHub Secrets:
- `ALICLOUD_ACCESS_KEY`
- `ALICLOUD_SECRET_KEY`

3. 修改工作流使用 AK:
```yaml
- name: Configure Aliyun Credentials
  run: |
    echo "ALICLOUD_ACCESS_KEY=${{ secrets.ALICLOUD_ACCESS_KEY }}" >> $GITHUB_ENV
    echo "ALICLOUD_SECRET_KEY=${{ secrets.ALICLOUD_SECRET_KEY }}" >> $GITHUB_ENV
```

**注意**: 这是临时方案，问题解决后应立即禁用 AK。

## 相关链接

- [GitHub Actions OIDC 文档](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [阿里云 RAM OIDC Provider](https://help.aliyun.com/document_detail/438099.html)
- [Terraform alicloud_ram_oidc_provider](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/ram_oidc_provider)