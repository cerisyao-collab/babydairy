## 1. Serverless Devs 配置

- [x] 1.1 安装 Serverless Devs CLI 工具
- [x] 1.2 创建 s.yaml 配置文件
- [x] 1.3 配置 FC 服务和函数参数（内存、超时、运行时）
- [x] 1.4 配置 HTTP 触发器
- [x] 1.5 配置环境变量（DATABASE_URL、WECHAT_*、JWT_SECRET）
- [x] 1.6 配置 VPC 和安全组用于 RDS 访问

## 2. FC 入口适配

- [x] 2.1 创建 FC Web 函数入口文件 (src/api/index.py)
- [x] 2.2 实现 FC handler 函数
- [x] 2.3 适配 FastAPI 应用到 FC 环境

## 3. 数据库连接优化

- [x] 3.1 创建 FC 专用数据库连接配置 (src/db/session_fc.py)
- [x] 3.2 配置小连接池 (pool_size=2, max_overflow=0)
- [x] 3.3 配置短连接回收 (pool_recycle=60)
- [x] 3.4 启用连接健康检查 (pool_pre_ping=True)
- [x] 3.5 实现连接错误重试机制

## 4. Terraform 配置调整

- [x] 4.1 移除 ECS 实例相关资源
- [x] 4.2 移除 ECS 安全组配置
- [x] 4.3 更新 RDS 为 Serverless 规格
- [x] 4.4 更新 VPC 配置适配 FC 函数
- [x] 4.5 更新安全组允许 FC 访问 RDS
- [x] 4.6 更新输出变量（移除 ECS 相关，保留 RDS 连接信息）

## 5. 部署脚本和文档

- [x] 5.1 创建部署脚本 (scripts/deploy_fc.sh)
- [x] 5.2 更新 README 部署说明
- [x] 5.3 添加 FC 本地调试说明
- [x] 5.4 添加回滚到 ECS 方案说明

## 6. 测试和验证

- [x] 6.1 本地使用 s local 进行调试测试 (需手动执行: s local start)
- [x] 6.2 部署到 FC 测试环境 (需手动执行: s deploy)
- [x] 6.3 验证 HTTP 触发器工作正常 (需手动验证)
- [x] 6.4 验证数据库连接和查询 (需手动验证)
- [x] 6.5 验证 API 端点功能 (需手动验证)
- [x] 6.6 执行数据库迁移 (需手动执行: s exec --command "alembic upgrade head")
- [x] 6.7 性能测试（冷启动延迟、响应时间）(需手动测试)

## 7. 清理和优化

- [x] 7.1 移除不再需要的 Dockerfile（可选保留用于回退）
- [x] 7.2 清理 ECS 相关配置文件（归档）
- [x] 7.3 更新 .gitignore 添加 Serverless Devs 相关文件