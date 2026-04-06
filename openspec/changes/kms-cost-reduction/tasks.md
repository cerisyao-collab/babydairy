## 1. OSS 基础设施准备

- [x] 1.1 创建 Terraform OSS bucket 资源（启用 SSE-OSS 加密）
- [x] 1.2 配置 OSS bucket 版本控制
- [x] 1.3 创建 RAM Policy 限制 OSS bucket 仅 FC 角色可访问
- [ ] 1.4 验证 OSS bucket 配置正确

## 2. 本地加密服务实现

- [x] 2.1 创建 src/services/secrets_service.py
- [x] 2.2 实现 generate_master_key() 方法（256-bit 随机密钥）
- [x] 2.3 实现 generate_data_key() 方法
- [x] 2.4 实现 encrypt_with_data_key() 方法（AES-256-GCM）
- [x] 2.5 实现 decrypt_with_data_key() 方法
- [x] 2.6 实现 encrypt_data_key() 方法（用主密钥加密数据密钥）
- [x] 2.7 实现 decrypt_data_key() 方法
- [x] 2.8 实现 encrypt_secret() 方法（完整信封加密流程）
- [x] 2.9 实现 decrypt_secret() 方法（完整信封解密流程）

## 3. OSS 密钥存储集成

- [x] 3.1 实现 upload_master_key_to_oss() 方法
- [x] 3.2 实现 download_master_key_from_oss() 方法
- [x] 3.3 实现 upload_encrypted_secret_to_oss() 方法
- [x] 3.4 实现 download_encrypted_secret_from_oss() 方法
- [x] 3.5 添加 OSS SDK 依赖（oss2）

## 4. 配置管理更新

- [x] 4.1 更新 src/config.py 添加 OSS bucket 配置
- [x] 4.2 实现 load_secrets_from_oss() 方法
- [x] 4.3 实现 get_secret() 方法（从 OSS 读取并解密）
- [x] 4.4 添加凭证内存缓存（避免重复解密）
- [x] 4.5 移除 KMS SDK 依赖（已迁移到 OSS 方案）

## 5. 密钥轮换机制

- [x] 5.1 创建 FC 定时触发器 Terraform 配置（30 天检查周期）
- [x] 5.2 创建 src/services/key_rotation_service.py
- [x] 5.3 实现 check_master_key_age() 方法
- [x] 5.4 实现 rotate_master_key() 方法
- [x] 5.5 实现 re_encrypt_all_secrets() 方法
- [x] 5.6 实现备份旧主密钥方法
- [x] 5.7 添加轮换日志记录
- [x] 5.8 添加轮换失败告警

## 6. 部署脚本

- [x] 6.1 创建 scripts/init_secrets.py（初始化主密钥和凭证）
- [x] 6.2 实现生成主密钥并上传到 OSS
- [x] 6.3 实现加密现有凭证并上传到 OSS
- [x] 6.4 创建密钥备份脚本
- [x] 6.5 创建密钥恢复脚本（从备份恢复）

## 7. 测试验证

- [x] 7.1 编写 secrets_service 单元测试
- [x] 7.2 测试信封加密/解密正确性
- [ ] 7.3 测试密钥轮换流程
- [ ] 7.4 测试 OSS 访问权限限制
- [ ] 7.5 测试备份恢复流程
- [ ] 7.6 集成测试：FC 启动时正确加载凭证
- [ ] 7.7 验证所有服务连接正常（数据库、微信、LLM）

## 8. 文档更新

- [ ] 8.1 更新 security-enhancement 提案，标记密钥管理方案变更
- [ ] 8.2 编写密钥管理使用文档
- [ ] 8.3 编写密钥轮换操作手册
- [ ] 8.4 编写密钥备份恢复指南