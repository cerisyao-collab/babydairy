## Why

当前安全增强方案（security-enhancement）计划使用阿里云 KMS 管理敏感凭证，预计月费用 ¥50-100。考虑到：
- 项目为个人/小团队项目，成本敏感
- KMS 费用相对项目规模较高
- KMS 主要是密钥托管服务，核心加密能力可自行实现

需要探索更低成本的安全方案，在保证安全性的前提下降低运营成本。

## What Changes

- **替代 KMS 凭证管理**: 使用 OSS 服务端加密 + 自管主密钥方案，成本降至 ¥5-10/月
- **简化密钥管理**: 移除 KMS SDK 依赖，使用 Python cryptography 库实现本地加密
- **保持同等安全级别**: 仍使用 AES-256-GCM 加密，密钥轮换由应用控制

**NOT CHANGING**:
- Token 安全存储方案（不变）
- 请求签名机制（不变）
- 数据库敏感字段加密方案（仍使用信封加密，仅密钥管理方式变更）
- LLM 数据脱敏方案（不变）

## Capabilities

### New Capabilities

- `secrets-management-v2`: 替代 KMS 的轻量级凭证管理方案，使用 OSS 加密存储 + 本地信封加密

### Modified Capabilities

- `secrets-management`: **BREAKING** - 原方案使用阿里云 KMS，现改为 OSS + 自管密钥方案，需调整实现

## Impact

### 成本对比

| 方案 | 月费用 | 说明 |
|------|--------|------|
| KMS (原方案) | ¥50-100 | 密钥托管 + API 调用费用 |
| OSS 加密存储 | ¥5-10 | OSS 存储费用 + 请求费用 |

### 代码变更

| 模块 | 变更 |
|------|------|
| `src/services/secrets_service.py` | 新建本地加密服务替代 KMS |
| `src/config.py` | 从 OSS 读取加密凭证 |
| `terraform/kms.tf` | 移除，改用 OSS bucket |

### 风险

- 自管密钥需要更严格的备份策略
- 密钥轮换需要应用代码实现（而非 KMS 自动）
- 需要确保密钥安全存储（权限控制）