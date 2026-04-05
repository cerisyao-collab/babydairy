## Why

OIDC 部署安全方案已完成基础设施配置，但尚未验证整个部署流程是否正常工作。需要在 GitHub Actions 中测试 OIDC 认证和自动部署，确保：
1. GitHub Actions 能够通过 OIDC 获取临时凭证
2. 部署流程能成功创建/更新 FC 函数
3. 数据库连接正常
4. API 端点可访问

这是 OIDC 部署方案的最后验证步骤。

## What Changes

- 触发 GitHub Actions 工作流测试 OIDC 认证
- 验证 FC 函数部署成功
- 测试 API 端点可访问性
- 确认数据库连接正常
- 验证日志和监控正常工作

## Capabilities

### New Capabilities

- `deployment-validation`: 部署验证流程，包括 OIDC 认证测试、FC 部署验证、API 健康检查

### Modified Capabilities

无需修改现有能力，这是纯验证任务。

## Impact

- 影响 GitHub Actions 工作流
- 验证 FC 函数部署
- 验证 RDS PostgreSQL 连接
- 验证 OSS secrets 存储