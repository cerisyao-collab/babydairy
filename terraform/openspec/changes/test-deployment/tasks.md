## 1. OIDC 认证测试

- [x] 1.1 确认 GitHub Actions 工作流配置正确 (deploy.yml)
- [x] 1.2 触发 GitHub Actions 工作流 (推送代码或手动触发)
- [x] 1.3 查看 OIDC 认证日志确认 AssumeRole 成功
- [x] 1.4 验证临时凭证获取并用于部署操作

## 2. FC 函数部署验证

- [x] 2.1 确认 FC 服务和函数配置正确 (s.yaml)
- [ ] 2.2 验证 FC 函数部署成功 (查询函数状态)
- [ ] 2.3 检查 VPC 配置正确绑定到函数
- [ ] 2.4 确认 OSS secrets bucket 权限正常

## 3. 数据库连接验证

- [ ] 3.1 测试 FC 函数连接 RDS PostgreSQL
- [ ] 3.2 验证数据库凭证从 OSS 正确读取
- [ ] 3.3 执行简单 SQL 查询确认连接正常

## 4. API 端点验证

- [ ] 4.1 获取 FC 函数 HTTP 触发器 URL
- [ ] 4.2 发送 HTTP 请求测试 API 响应
- [ ] 4.3 确认健康检查端点返回正确状态

## 5. 清理和收尾

- [ ] 5.1 记录测试结果和发现的问题
- [ ] 5.2 更新 oidc-deploy-security tasks.md 完成相关任务
- [ ] 5.3 如测试成功，准备禁用长期 AccessKey