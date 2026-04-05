## Context

OIDC 部署安全方案已完成：
- OIDC Provider 已通过 IMS API 创建
- RAM 角色 (terraform-deploy, fc-deploy) 已通过 CLI 创建
- GitHub Secrets 已配置 9 个必要参数
- Terraform 基础设施 (VPC, RDS, OSS) 已部署

当前需要验证整个 CI/CD 流程是否正常工作，这是上线前的最后确认步骤。

## Goals / Non-Goals

**Goals:**
- 验证 GitHub Actions OIDC 认证流程
- 确认 FC 函数部署成功
- 测试 API 端点健康检查
- 验证数据库连接正常

**Non-Goals:**
- 不修改现有基础设施
- 不添加新功能
- 不进行性能测试

## Decisions

### 测试方式
- **决策**: 通过推送代码触发 GitHub Actions，观察 OIDC 认证和部署结果
- **理由**: 这是实际生产部署的流程，测试真实场景

### 验证点
1. OIDC 认证成功 - GitHub Actions 日志显示 AssumeRole 成功
2. FC 部署成功 - 函数可查询、配置正确
3. API 健康检查 - HTTP 请求返回正确响应
4. 数据库连接 - FC 函数能连接 RDS

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| OIDC 认证失败 | 检查 thumbprint 配置、角色信任策略 |
| FC 部署失败 | 检查 fc-deploy-role 权限、VPC 配置 |
| 数据库连接失败 | 检查安全组、白名单配置 |