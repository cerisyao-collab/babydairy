## Context

当前 Baby Diary API 已完成 FastAPI 开发，原计划使用 ECS + RDS 部署。经评估，函数计算(FC)更适合试运行阶段：
- 流量低频：试运行阶段日均调用预计 < 1000 次
- 成本敏感：需要最小化试运行成本
- 快速迭代：需要频繁部署测试

**约束条件**：
- 必须保持 API 功能不变
- 需要连接 RDS PostgreSQL
- 冷启动延迟可接受（1-3秒）

## Goals / Non-Goals

**Goals:**
- 将部署方案从 ECS 改为函数计算(FC)
- 配置 Serverless Devs 一键部署
- 优化数据库连接池适配 FC 场景
- 降低月运行成本 50%+

**Non-Goals:**
- 高可用多副本部署
- 自定义域名和 HTTPS（后续阶段）
- 高级监控告警
- 性能极限优化

## Decisions

### 1. 部署工具：Serverless Devs

**选择**: 阿里云官方 Serverless Devs (s CLI)

**理由**:
- 阿里云官方支持，与 FC 集成最好
- 支持本地调试和一键部署
- 配置文件 s.yaml 清晰易维护
- 支持 CI/CD 集成

**备选方案**:
- Terraform + FC Provider：配置复杂，调试不便
- 控制台手动配置：不可重复，不利于版本管理

### 2. 函数类型：Web 函数

**选择**: FC Web 函数（非事件函数）

**理由**:
- 原生支持 HTTP 触发
- 无需修改 FastAPI 代码结构
- 自动处理请求/响应转换
- 支持自定义域名绑定

### 3. 数据库连接：连接池 + FC 优化

**选择**: SQLAlchemy 连接池，FC 专用配置

**配置参数**:
| 参数 | 传统配置 | FC 配置 | 原因 |
|------|----------|---------|------|
| pool_size | 5-10 | 2 | 单实例低并发 |
| max_overflow | 10 | 0 | 避免连接泄漏 |
| pool_recycle | 3600 | 60 | FC 实例回收快 |
| pool_pre_ping | True | True | 检测失效连接 |

**理由**: FC 函数实例生命周期短，需要小连接池避免连接泄漏和超时问题。

### 4. 运行时：Python 3.9

**选择**: Python 3.9 运行时

**理由**:
- FC 官方支持
- 与现有代码兼容
- 性能稳定

### 5. 函数规格：256MB 内存

**选择**: 256MB 内存，1 核

**理由**:
- FastAPI 应用内存占用 ~100MB
- 256MB 留有余量
- 成本最优：每百万次调用约 5 元

### 6. RDS 规格：Serverless 版本

**选择**: RDS PostgreSQL Serverless 版

**理由**:
- 自动伸缩，按使用付费
- 与 FC 搭配最佳
- 试运行阶段成本更低

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| 冷启动延迟 1-3 秒 | 使用预留实例（可后续配置）；试运行阶段可接受 |
| 数据库连接池耗尽 | 使用小连接池 + pre_ping；监控连接数 |
| VPC 冷启动延迟 | 函数与 RDS 同可用区；使用 VPC 预热 |
| 调试复杂度增加 | 使用 Serverless Devs 本地调试模式 |
| 部署配置变更 | 保留原 ECS Terraform 配置作为回退方案 |

## Migration Plan

### 部署步骤

1. **准备工作**
   - 配置阿里云 AccessKey
   - 安装 Serverless Devs: `npm install -g @serverless-devs/s`
   - 配置 s.yaml

2. **创建 RDS（如未创建）**
   - 使用 Terraform 创建 RDS PostgreSQL Serverless
   - 配置 VPC 和安全组

3. **适配代码**
   - 创建 FC 入口文件
   - 配置 FC 专用数据库连接

4. **部署函数**
   ```bash
   s deploy
   ```

5. **验证部署**
   - 调用健康检查端点
   - 执行数据库迁移
   - 测试核心 API

### 回滚策略

如遇问题可快速回退到 ECS 方案：
1. 保留原 `terraform/` 目录
2. 使用 `terraform apply` 部署 ECS
3. 切换 DNS 或重新配置小程序 API 地址