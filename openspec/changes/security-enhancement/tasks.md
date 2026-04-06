## 1. KMS 凭证管理基础设施

- [ ] 1.1 更新 Terraform 添加 KMS 密钥资源
- [ ] 1.2 创建 KMS 密钥策略（限制 FC 角色访问）
- [ ] 1.3 编写凭证加密脚本（加密现有凭证）
- [ ] 1.4 更新 s.yaml 配置 FC 角色权限
- [ ] 1.5 创建 src/services/kms_service.py
- [ ] 1.6 实现 encrypt_secret 和 decrypt_secret 方法
- [ ] 1.7 更新 src/config.py 从 KMS 读取凭证
- [ ] 1.8 添加凭证内存缓存机制
- [ ] 1.9 测试 KMS 集成

## 2. 小程序 Token 安全存储

- [ ] 2.1 创建 utils/crypto.js 加密工具模块
- [ ] 2.2 实现 AES 加密/解密函数
- [ ] 2.3 实现设备指纹生成函数
- [ ] 2.4 更新 utils/api.js Token 存储逻辑
- [ ] 2.5 实现 Token 加密存储
- [ ] 2.6 实现 Token 解密读取
- [ ] 2.7 添加设备绑定验证
- [ ] 2.8 测试 Token 安全存储流程

## 3. Refresh Token 机制

- [ ] 3.1 更新 src/services/jwt_service.py 支持 refresh token
- [ ] 3.2 实现 create_refresh_token 方法
- [ ] 3.3 实现 validate_refresh_token 方法
- [ ] 3.4 更新 src/api/auth.py 添加 /auth/refresh 端点
- [ ] 3.5 修改 access token 有效期为 15 分钟
- [ ] 3.6 更新小程序 api.js 支持 token 刷新
- [ ] 3.7 实现 token 过期自动刷新逻辑
- [ ] 3.8 测试 refresh token 流程

## 4. 请求签名机制

- [ ] 4.1 创建 utils/signing.js 签名工具模块
- [ ] 4.2 实现 HMAC-SHA256 签名函数
- [ ] 4.3 实现 nonce 生成函数
- [ ] 4.4 更新 api.js 请求拦截器添加签名头
- [ ] 4.5 创建后端签名验证中间件
- [ ] 4.6 实现 timestamp 校验（±5分钟）
- [ ] 4.7 实现 nonce 去重校验
- [ ] 4.8 实现签名重算和比对
- [ ] 4.9 测试签名验证流程
- [ ] 4.10 测试重放攻击防护

## 5. 数据库敏感字段加密

- [ ] 5.1 设计加密字段 Schema（添加 ciphertext 列）
- [ ] 5.2 创建 src/services/encryption_service.py
- [ ] 5.3 实现 generate_data_key 方法
- [ ] 5.4 实现 encrypt_field 方法（AES-256-GCM）
- [ ] 5.5 实现 decrypt_field 方法
- [ ] 5.6 更新 BabyConfig 模型支持加密字段
- [ ] 5.7 实现 blinded index 支持加密字段搜索
- [ ] 5.8 编写数据迁移脚本
- [ ] 5.9 执行历史数据迁移
- [ ] 5.10 测试加密字段读写

## 6. LLM 数据脱敏

- [ ] 6.1 创建 src/services/data_masking_service.py
- [ ] 6.2 实现 PII 识别规则（姓名、日期、电话）
- [ ] 6.3 实现姓名脱敏（替换为"宝宝"）
- [ ] 6.4 实现日期脱敏（转换为日龄）
- [ ] 6.5 实现联系方式移除
- [ ] 6.6 更新 llm_service.py 调用前脱敏
- [ ] 6.7 实现 LLM 输出校验（PII 检测）
- [ ] 6.8 实现 prompt 注入检测和过滤
- [ ] 6.9 测试数据脱敏效果

## 7. 审计日志系统

- [ ] 7.1 创建 AuditLog 数据模型
- [ ] 7.2 创建 src/services/audit_service.py
- [ ] 7.3 实现 log_event 方法
- [ ] 7.4 添加认证事件日志（登录、登出）
- [ ] 7.5 添加敏感数据访问日志（解密操作）
- [ ] 7.6 添加 LLM 调用日志
- [ ] 7.7 创建审计日志查询 API
- [ ] 7.8 实现日志保留策略（90天）
- [ ] 7.9 测试审计日志记录

## 8. 数据库连接安全

- [ ] 8.1 更新 SQLAlchemy 连接配置强制 SSL
- [ ] 8.2 更新 Terraform RDS 配置强制 SSL
- [ ] 8.3 启用 RDS SQL 审计
- [ ] 8.4 测试 SSL 连接

## 9. 小程序更新和迁移

- [ ] 9.1 更新小程序版本号
- [ ] 9.2 实现旧版 Token 格式兼容
- [ ] 9.3 添加用户引导（提示重新登录）
- [ ] 9.4 测试新旧版本兼容性
- [ ] 9.5 提交小程序审核

## 10. 文档和测试

- [ ] 10.1 更新 README 添加安全架构说明
- [ ] 10.2 编写 KMS 使用文档
- [ ] 10.3 编写数据加密迁移指南
- [ ] 10.4 创建安全测试用例
- [ ] 10.5 进行安全渗透测试
- [ ] 10.6 编写安全运维手册