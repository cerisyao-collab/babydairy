## Why

当前 Baby Diary 技能是一个基于本地文件存储的单用户应用，无法支撑商用微信小程序的需求。为了支持多用户、云端存储、API访问，需要将其改造为完整的后端服务。

**核心痛点**：
- 无用户认证：当前所有数据存储在本地，无法区分不同用户的数据
- 无API层：作为Python技能模块存在，无法直接服务于微信小程序
- 无数据库：使用本地JSON文件存储，不适合多用户商用场景
- 无云部署：无基础设施配置，无法部署到阿里云

## What Changes

- **新增** WeChat 用户认证 API（微信登录、用户信息获取）
- **新增** RESTful API 层（记录 CRUD、每日总结、配置管理等）
- **新增** PostgreSQL 数据库存储（用户数据、记录数据隔离）
- **新增** Terraform 基础设施配置（阿里云 ECS、RDS、安全组等最小规格）
- **新增** FastAPI 应用框架（替代当前纯 Python 模块）
- **修改** 数据存储层（从文件存储改为数据库 ORM）
- **修改** 记录结构（增加 user_id 字段实现数据隔离）

## Capabilities

### New Capabilities

- `wechat-auth`: 微信小程序用户认证（登录、openid获取、用户信息管理）
- `rest-api`: RESTful API 服务层（记录管理、每日总结、配置等端点）
- `database-storage`: PostgreSQL 数据库存储层（用户表、记录表、配置表）
- `aliyun-infra`: 阿里云基础设施配置（Terraform：ECS、RDS PostgreSQL、安全组、VPC）

### Modified Capabilities

无现有规格需要修改。当前项目无正式规格文档，本变更将首次建立规格体系。

## Impact

- **代码结构**：需要重构为 FastAPI 应用，新增 `api/`、`models/`、`services/` 目录
- **数据模型**：现有记录结构需增加 `user_id` 字段，建立用户-记录关联
- **依赖变更**：新增 FastAPI、SQLAlchemy、psycopg2、wechatpy 等依赖
- **部署方式**：从本地运行变为阿里云 ECS 部署，需 Docker 容器化
- **API 兼容**：保持原有功能语义不变，仅改变调用方式（从函数调用改为 HTTP API）