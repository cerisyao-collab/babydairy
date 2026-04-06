## Why

当前项目已有部分单元测试，但使用 mock 对象模拟数据库。缺少与真实数据库交互的集成测试，无法验证：
- 数据库迁移的正确性
- SQLAlchemy 模型与数据库的实际映射
- 服务层与数据库的实际交互行为

同时，之前实现的 secrets_service 测试无法在当前环境运行（缺少 pytest 和 cryptography）。需要配置本地开发测试环境。

## What Changes

- **本地测试数据库**: 使用 Docker PostgreSQL 作为本地开发/测试数据库
- **测试环境配置**: 创建 `.env.test` 和 pytest 配置，支持本地测试运行
- **虚拟环境**: 创建 Python 虚拟环境安装测试依赖
- **集成测试**: 添加数据库集成测试（models、services、API endpoints）
- **测试数据 fixtures**: 创建测试数据 fixtures 用于集成测试

## Capabilities

### New Capabilities

- `local-test-database`: 本地 PostgreSQL Docker 容器用于开发和测试
- `integration-testing`: 数据库集成测试框架，验证服务层与数据库交互
- `test-environment`: Python 虚拟环境和 pytest 配置，支持本地运行测试

### Modified Capabilities

无（这是新增测试能力，不改变现有功能行为）

## Impact

### 新增文件

| 文件 | 说明 |
|------|------|
| `docker-compose.test.yml` | 测试数据库 Docker Compose 配置 |
| `.env.test` | 测试环境配置文件 |
| `pytest.ini` | pytest 配置 |
| `tests/conftest.py` | pytest fixtures 和数据库测试配置 |
| `tests/integration/` | 集成测试目录 |
| `tests/fixtures/` | 测试数据 fixtures |

### 依赖变更

- 需要安装 Docker 用于本地数据库
- 需要创建 Python 虚拟环境