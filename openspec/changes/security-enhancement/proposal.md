## Why

当前系统存在三个关键安全边界的安全风险：小程序 Token 明文存储、后端凭证环境变量暴露、用户数据未加密发送到 LLM。随着产品上线和用户增长，安全合规要求（如《个人信息保护法》）和用户信任需求使得安全增强成为必要。

## What Changes

### 边界 A: 小程序 → 后端

- **Token 安全存储**: 加密存储 JWT Token + 设备绑定验证
- **请求签名机制**: 添加 timestamp + nonce + signature 防重放攻击
- **Token 有效期优化**: 缩短 Access Token 有效期 + Refresh Token 机制

### 边界 B: 后端 → 数据库

- **凭证管理**: 集成阿里云 KMS 管理敏感凭证（数据库密码、微信 Secret、LLM API Key）
- **数据库连接加密**: 强制 SSL/TLS 连接
- **敏感字段加密**: 宝宝姓名、出生日期等 PII 字段加密存储
- **审计日志**: 启用 RDS SQL 审计

### 边界 C: 后端 → LLM

- **数据脱敏**: 发送到 LLM 前移除/匿名化 PII 信息
- **调用审计**: 记录 LLM 调用日志（谁、何时、发送了什么）
- **Prompt 保护**: 输入过滤防止注入，输出校验防止泄露

**BREAKING**:
- Token 存储格式变更，已登录用户需要重新登录
- 数据库敏感字段加密，需要迁移脚本

## Capabilities

### New Capabilities

- `secrets-management`: 阿里云 KMS 集成，管理所有敏感凭证
- `request-signing`: 小程序请求签名机制，防重放防篡改
- `token-security`: Token 加密存储、设备绑定、Refresh Token 机制
- `data-encryption`: 数据库敏感字段加密（字段级 AES-GCM）
- `llm-data-protection`: LLM 调用前数据脱敏、调用审计
- `audit-logging`: 安全相关操作审计日志

### Modified Capabilities

无（这是新增安全能力，不改变现有功能行为）

## Impact

### 代码变更

| 模块 | 变更 |
|------|------|
| `src/config.py` | 添加 KMS 相关配置 |
| `src/services/kms_service.py` | 新建 KMS 服务 |
| `src/services/jwt_service.py` | 添加 Refresh Token 支持 |
| `src/api/auth.py` | 添加签名验证中间件 |
| `src/models/baby_config.py` | 敏感字段加密处理 |
| `src/services/llm_service.py` | 添加数据脱敏层 |
| `utils/api.js` (小程序) | 添加请求签名、Token 加密 |
| `utils/crypto.js` (小程序) | 新建加密工具 |

### 基础设施变更

- 启用阿里云 KMS 服务（额外费用约 ¥50-100/月）
- 启用 RDS SQL 审计（额外费用约 ¥30/月）
- 更新 Terraform 配置添加 KMS 资源

### 依赖变更

- 后端: 添加 `alicloud-kms` SDK
- 小程序: 无新增依赖（使用微信内置 crypto）