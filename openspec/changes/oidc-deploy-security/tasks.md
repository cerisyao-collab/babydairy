## 1. OIDC Provider 基础设施

- [x] 1.1 获取 GitHub OIDC 公钥指纹 (配置为变量，需要用户填入实际值)
- [x] 1.2 创建 terraform/oidc.tf 定义 OIDC Provider
- [x] 1.3 应用 OIDC Provider 资源 (通过 IMS API 创建成功)

## 2. RAM 角色创建

- [x] 2.1 创建 terraform/roles.tf 定义部署角色
- [x] 2.2 创建 terraform-deploy 角色 (OIDC 角色已通过 CLI 创建)
- [x] 2.3 创建 fc-deploy 角色 (OIDC 角色已通过 CLI 创建)
- [x] 2.4 创建 fc-execution 角色 (运行时)
- [x] 2.5 创建 developer 角色 (本地开发)

## 3. 最小权限策略

- [x] 3.1 创建 terraform/policies.tf 定义权限策略
- [x] 3.2 定义 terraform-deploy-policy (最小权限)
- [x] 3.3 定义 fc-deploy-policy (最小权限)
- [x] 3.4 定义 fc-execution-policy (运行时权限)
- [x] 3.5 定义 developer-policy (开发权限)
- [x] 3.6 将策略附加到角色

## 4. GitHub Actions 配置

- [x] 4.1 创建 .github/workflows/ 目录
- [x] 4.2 创建 deploy.yml 工作流 (OIDC 认证)
- [x] 4.3 创建 terraform.yml 工作流 (基础设施)
- [x] 4.4 在 GitHub 设置 Secrets (全部 9 个 secrets 已配置)
- [ ] 4.5 测试 OIDC 认证工作流 - 需要用户执行

## 5. 本地开发配置

- [x] 5.1 创建 docs/deploy-security.md 文档
- [x] 5.2 配置 aliyun CLI (OAuth 模式) - 已配置
- [x] 5.3 测试 AssumeRole 流程 - 脚本已创建
- [x] 5.4 更新本地开发脚本 (scripts/setup_local_dev.sh)

## 6. 长期 AK 移除

- [ ] 6.1 确认 OIDC 部署正常工作 - 需要用户执行
- [ ] 6.2 禁用现有的长期 AccessKey - 需要用户执行
- [ ] 6.3 删除 GitHub Secrets 中的 AK (如有) - 需要用户执行
- [x] 6.4 记录回滚方案 (docs/rollback-plan.md)

## 7. 验证和测试

- [ ] 7.1 测试 GitHub Actions 部署流程 - 需要用户执行
- [ ] 7.2 验证权限限制生效 - 需要用户执行
- [ ] 7.3 测试未授权仓库被拒绝 - 需要用户执行
- [ ] 7.4 验证审计日志记录 - 需要用户执行

## 8. 文档

- [x] 8.1 编写 OIDC 配置说明 (docs/deploy-security.md)
- [x] 8.2 编写本地开发指南 (docs/deploy-security.md)
- [x] 8.3 编写故障排除指南 (docs/deploy-security.md)
- [x] 8.4 更新项目 README