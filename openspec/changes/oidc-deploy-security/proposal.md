## Why

当前部署流程使用长期有效的 AccessKey (ALICLOUD_ACCESS_KEY / ALICLOUD_SECRET_KEY)，存在以下安全风险：

1. **密钥泄露风险**: 长期密钥一旦泄露，攻击者可获得所有权限，且难以自动发现
2. **权限过大**: 部署使用的 AK 通常拥有管理员权限，违反最小权限原则
3. **无法自动轮换**: 长期密钥需要手动轮换，操作复杂且容易遗忘
4. **审计困难**: 无法区分是哪个 GitHub Action 或开发者执行的操作

阿里云支持 OIDC (OpenID Connect) 与 RAM 角色集成，可以实现：
- 无长期密钥部署
- 自动签发临时凭证（默认 1-12 小时有效期）
- 基于 GitHub 仓库/分支的细粒度权限控制
- 完整的审计追踪

## What Changes

### 部署认证方式

| 变更项 | 当前方案 | 改进方案 |
|--------|---------|---------|
| 认证方式 | 长期 AccessKey | OIDC Token → STS 临时凭证 |
| 密钥有效期 | 永久 | 1-12 小时自动过期 |
| 权限控制 | 粗粒度 | 细粒度（仓库/分支级别） |
| 审计追踪 | 无 | 完整（GitHub Actor, Repo, Branch） |

### 新增资源

- **RAM OIDC Provider**: 用于验证 GitHub Actions 的 OIDC Token
- **RAM Role (Deploy)**: 部署专用角色，最小权限
- **RAM Role (FC Execution)**: FC 运行时角色，仅业务所需权限
- **GitHub Actions Workflow**: OIDC 认证 + 部署流程

### 移除/废弃

- **长期 AccessKey**: 移除部署用的长期 AK
- **环境变量明文凭证**: 迁移到 OSS 加密存储

## Capabilities

### New Capabilities

- `oidc-authentication`: GitHub Actions OIDC 与阿里云 RAM 集成，实现无密钥部署
- `deploy-roles`: 最小权限部署角色，分离基础设施部署和应用部署权限

### Modified Capabilities

无（这是新增安全能力，不改变现有功能行为）

## Impact

### 新增文件

| 文件 | 说明 |
|------|------|
| `terraform/oidc.tf` | OIDC Provider 和 RAM 角色定义 |
| `terraform/policies.tf` | 最小权限策略定义 |
| `.github/workflows/deploy.yml` | GitHub Actions 部署工作流 |
| `.github/workflows/terraform.yml` | Terraform 基础设施部署 |
| `docs/deploy-security.md` | 部署安全说明文档 |

### 变更流程

1. 首次配置 OIDC Provider (一次性)
2. 创建部署专用 RAM 角色
3. 配置 GitHub Actions 使用 OIDC
4. 移除长期 AccessKey
5. 验证部署流程正常