## Why

当前项目采用 ECS + RDS 部署方案，对于试运行阶段存在成本过高、运维复杂的问题。函数计算(FC)方案更适合低频调用的试运行场景：
- **成本更低**：ECS 固定成本 ~90-140元/月 → FC 按量付费 ~35-70元/月（节省50%+）
- **免运维**：无需管理服务器、Docker、系统更新
- **自动伸缩**：零配置自动应对流量波动
- **一键部署**：Serverless Devs 工具支持快速迭代

## What Changes

- **移除** ECS 实例及相关的 Terraform 配置
- **新增** 阿里云函数计算(FC) Web 函数部署配置
- **新增** Serverless Devs (s.yaml) 配置文件
- **新增** FC 专用数据库连接池配置
- **新增** FC 入口适配代码
- **修改** Terraform 配置仅保留 RDS 和网络资源
- **保留** 现有 API 代码结构，仅需适配入口

## Capabilities

### New Capabilities

- `fc-deployment`: 阿里云函数计算部署配置（Serverless Devs、s.yaml、Web函数）
- `fc-database-connection`: FC 专用数据库连接池配置（小连接池、短超时、连接复用）

### Modified Capabilities

- `aliyun-infra`: 基础设施配置从 ECS+RDS 改为 FC+RDS（移除 ECS，新增 FC 相关 VPC 配置）

## Impact

- **代码变更**：
  - 新增 `src/api/index.py` FC 入口文件
  - 新增 `src/db/session_fc.py` FC 专用数据库连接
  - 新增 `s.yaml` Serverless Devs 配置
- **Terraform 变更**：
  - 移除 ECS 相关资源
  - 调整 VPC 配置适配 FC 函数
  - RDS 规格可选用 serverless 版本
- **部署方式变更**：
  - 从 `terraform apply` + Docker 部署
  - 改为 `s deploy` 一键部署
- **成本影响**：月成本从 ~90-140元 降至 ~35-70元
- **性能影响**：首次冷启动延迟 1-3 秒（后续请求正常）