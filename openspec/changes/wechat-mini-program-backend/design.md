## Context

当前 Baby Diary 是一个 Python 技能模块，使用本地 JSON 文件存储数据。主要功能包括：
- 记录管理（创建、查询、更新、删除）
- 8种记录类型（喂养、大小便、营养品、洗澡、睡眠、生长、病情）
- 每日总结生成
- 图片管理

**约束条件**：
- 试运行阶段，使用阿里云最小规格资源
- 需支持微信小程序登录（openid 认证）
- 数据按用户隔离存储
- 成本优先：选择最经济的云资源配置

## Goals / Non-Goals

**Goals:**
- 建立 RESTful API 服务层，供微信小程序调用
- 实现微信用户认证与数据隔离
- 使用 PostgreSQL 数据库替代文件存储
- 提供阿里云基础设施 Terraform 配置
- 保持现有功能语义完整

**Non-Goals:**
- 高可用架构（试运行阶段无需多副本）
- 复杂的权限系统（仅用户数据隔离）
- 微信支付功能
- 大规模并发优化
- 国际化支持

## Decisions

### 1. Web Framework: FastAPI

**选择**: FastAPI + Uvicorn

**理由**:
- 性能优秀，适合 API 服务
- 自动生成 OpenAPI 文档，便于小程序对接
- 类型提示支持，开发体验好
- 轻量级，适合小规模部署

**备选方案**:
- Flask：更成熟但无自动文档
- Django：功能过重，不适合小规模 API

### 2. Database: PostgreSQL on Aliyun RDS

**选择**: 阿里云 RDS PostgreSQL（最小规格）

**理由**:
- PostgreSQL 成度高，适合结构化数据
- RDS 提供托管服务，降低运维成本
- SQLAlchemy ORM 支持完善
- 最小规格（1核1G）满足试运行需求

**备选方案**:
- MySQL：也可，但 PostgreSQL 与 Python 生态更契合
- MongoDB：文档型数据库，但关系型更适合用户-记录关联

### 3. WeChat Authentication: wechatpy

**选择**: wechatpy 库处理微信登录

**理由**:
- 微信官方 Python SDK
- 完整支持小程序登录流程
- 维护活跃

### 4. Infrastructure: Terraform + Aliyun ECS + RDS

**选择**: Terraform 配置阿里云资源

**资源配置**:
| 资源 | 规格 | 月成本估算 |
|------|------|-----------|
| ECS | ecs.tiny-c1m1.small (1核1G) | ~40元 |
| RDS PostgreSQL | rds.pg.tiny.ha (1核1G) | ~50元 |
| VPC/安全组 | 免费 | 0元 |
| **总计** | | **~90元/月** |

**理由**:
- Terraform 提供可复用、版本化的基础设施配置
- 最小规格满足试运行需求
- 可随时升级规格

### 5. Data Model Design

**用户表 (users)**:
```sql
- id: UUID (主键)
- openid: VARCHAR (微信 openid，唯一)
- nickname: VARCHAR
- avatar_url: VARCHAR
- created_at, updated_at: TIMESTAMP
```

**记录表 (records)**:
```sql
- id: UUID (主键)
- user_id: UUID (外键 → users.id)
- type: VARCHAR (feeding/bowel/urine/...)
- timestamp: TIMESTAMP
- date: DATE
- details: JSONB
- images: TEXT[]
- created_at, updated_at: TIMESTAMP
```

**宝宝配置表 (baby_configs)**:
```sql
- id: UUID (主键)
- user_id: UUID (外键 → users.id)
- baby_name: VARCHAR
- birth_date: DATE
- created_at, updated_at: TIMESTAMP
```

### 6. Project Structure

```
src/
├── api/                  # FastAPI 端点
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── auth.py           # 认证端点
│   ├── records.py        # 记录端点
│   ├── config.py         # 配置端点
│   └── summary.py        # 总结端点
├── models/               # SQLAlchemy 模型
│   ├── __init__.py
│   ├── user.py
│   ├── record.py
│   └── baby_config.py
├── services/             # 业务逻辑层
│   ├── __init__.py
│   ├── auth_service.py
│   ├── record_service.py
│   └── summary_service.py
├── db/                   # 数据库配置
│   ├── __init__.py
│   ├── session.py
│   └── migrations/       # Alembic 迁移
└── config.py             # 应用配置
terraform/
├── main.tf               # 主配置
├── variables.tf          # 变量定义
├── outputs.tf            # 输出定义
└── providers.tf          # Aliyun provider
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| 最小规格可能不足以支撑增长 | Terraform 配置易于升级规格；监控资源使用 |
| 单 ECS 无高可用 | 试运行阶段可接受；后续可扩展为多副本 |
| 微信小程序 AppID/AppSecret 需配置管理 | 使用环境变量 + Terraform secrets |
| 数据迁移需从文件到数据库 | 提供迁移脚本；试运行可重新开始 |
| 安全组配置不当导致暴露 | Terraform 明确配置仅开放必要端口 |