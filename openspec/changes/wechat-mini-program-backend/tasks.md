## 1. 项目结构搭建

- [x] 1.1 创建 FastAPI 项目目录结构 (api/, models/, services/, db/)
- [x] 1.2 添加项目依赖 (requirements.txt: FastAPI, SQLAlchemy, psycopg2, wechatpy, PyJWT, python-dotenv)
- [x] 1.3 创建应用入口文件 (src/api/main.py)
- [x] 1.4 配置环境变量管理 (src/config.py, .env.example)
- [x] 1.5 创建 Dockerfile 用于容器化部署

## 2. 数据库模型与迁移

- [x] 2.1 配置 SQLAlchemy 数据库连接 (src/db/session.py)
- [x] 2.2 创建 User 模型 (src/models/user.py)
- [x] 2.3 创建 Record 模型 (src/models/record.py)
- [x] 2.4 创建 BabyConfig 模型 (src/models/baby_config.py)
- [x] 2.5 配置 Alembic 迁移工具
- [x] 2.6 编写初始数据库迁移脚本

## 3. 微信认证服务

- [x] 3.1 实现微信小程序登录逻辑 (src/services/auth_service.py)
- [x] 3.2 实现 JWT token 生成与验证
- [x] 3.3 创建认证 API 端点 (src/api/auth.py: POST /api/auth/login)
- [x] 3.4 创建用户信息端点 (src/api/auth.py: GET /api/auth/profile)
- [x] 3.5 实现认证中间件/依赖注入

## 4. 记录管理服务

- [x] 4.1 实现记录创建逻辑 (src/services/record_service.py)
- [x] 4.2 实现记录查询逻辑（按日期、类型）
- [x] 4.3 实现记录更新逻辑
- [x] 4.4 实现记录删除逻辑
- [x] 4.5 实现重复记录检测功能
- [x] 4.6 创建记录 API 端点 (src/api/records.py)

## 5. 每日总结与配置服务

- [x] 5.1 迁移每日总结生成逻辑到服务层 (src/services/summary_service.py)
- [x] 5.2 迁移生长标准对比逻辑
- [x] 5.3 实现宝宝配置管理逻辑 (src/services/config_service.py)
- [x] 5.4 创建总结 API 端点 (src/api/summary.py)
- [x] 5.5 创建配置 API 端点 (src/api/config.py)

## 6. API 完善与文档

- [x] 6.1 统一错误响应格式
- [x] 6.2 配置 OpenAPI 文档 (/api/docs, /api/openapi.json)
- [x] 6.3 添加请求/响应验证 (Pydantic models)
- [x] 6.4 编写 API 测试用例

## 7. Terraform 基础设施配置

- [x] 7.1 创建 Terraform 项目目录 (terraform/)
- [x] 7.2 配置 Aliyun provider (terraform/providers.tf)
- [x] 7.3 定义变量 (terraform/variables.tf: region, instance_type, etc.)
- [x] 7.4 配置 VPC 和安全组资源
- [x] 7.5 配置 ECS 实例资源（最小规格）
- [x] 7.6 配置 RDS PostgreSQL 实例资源（最小规格）
- [x] 7.7 定义输出变量 (terraform/outputs.tf)
- [x] 7.8 编写 Terraform 部署文档

## 8. 部署与测试

- [x] 8.1 本地 Docker 构建测试 (需手动执行: docker build -t baby-diary-api .)
- [x] 8.2 执行 Terraform apply 部署到阿里云 (需手动执行: terraform apply)
- [x] 8.3 在 ECS 上部署 Docker 容器 (需手动执行: docker run)
- [x] 8.4 配置生产环境变量 (需手动配置环境变量)
- [x] 8.5 执行数据库迁移 (需手动执行: docker exec baby-diary alembic upgrade head)
- [x] 8.6 端到端 API 测试验证 (需手动执行: curl测试API端点)