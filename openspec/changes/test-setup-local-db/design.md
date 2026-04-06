## Context

当前项目测试情况：
- 已有部分单元测试（test_ai_analyzer.py, test_llm_service.py, api_test.py）
- 使用 mock 对象模拟数据库，无真实数据库交互
- 新创建的 test_secrets_service.py 无法运行（缺少 pytest 环境）
- macOS 环境，Python 3.14 externally-managed，需要虚拟环境

约束条件：
- 使用 Docker PostgreSQL 作为本地测试数据库（与生产环境一致）
- 测试环境与开发环境隔离（.env.test）
- 测试不依赖外部服务（OSS、微信 API、LLM）

## Goals / Non-Goals

**Goals:**
- 配置 Python 虚拟环境安装测试依赖
- 使用 Docker PostgreSQL 作为本地测试数据库
- 创建 pytest 配置和 fixtures 支持集成测试
- 编写数据库集成测试验证模型和服务
- 确保 secrets_service 单元测试可以运行

**Non-Goals:**
- 不配置 CI/CD 测试流水线（后续任务）
- 不测试外部服务（OSS、微信、LLM）- 使用 mock
- 不创建生产数据库实例（仅本地开发）

## Decisions

### 1. 测试数据库方案

**决策：Docker PostgreSQL 容器**

理由：
- 与生产环境 RDS PostgreSQL 一致
- Docker 可快速启动/清理
- 数据隔离，不影响开发数据

替代方案：
- SQLite → 拒绝：与生产 PostgreSQL 不一致，部分特性不支持
- 本地安装 PostgreSQL → 拒绝：macOS 系统复杂，Docker 更简洁

实现方式：
```yaml
# docker-compose.test.yml
services:
  test-db:
    image: postgres:14
    environment:
      POSTGRES_DB: baby_diary_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5433:5432"  # 避免与本地 PostgreSQL 冲突
    tmpfs:
      - /var/lib/postgresql/data  # 使用内存存储，测试更快
```

### 2. Python 环境方案

**决策：Python venv + requirements.txt**

理由：
- macOS Python 3.14 externally-managed，必须使用虚拟环境
- venv 是 Python 标准库，无需额外安装
- requirements.txt 已有测试依赖定义

实现方式：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. pytest 配置方案

**决策：pytest.ini + conftest.py**

理由：
- pytest.ini 定义全局配置（标记、输出格式）
- conftest.py 定义 fixtures（数据库会话、测试数据）
- 测试隔离：每个测试独立的数据库事务

实现方式：
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (no database)
    integration: Integration tests (with database)
addopts = -v --tb=short
```

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def test_db():
    """Session-scoped test database"""
    # Start Docker container
    # Create tables
    yield db
    # Cleanup

@pytest.fixture(scope="function")
def db_session(test_db):
    """Function-scoped session with transaction rollback"""
    session = Session()
    yield session
    session.rollback()
```

### 4. 测试数据方案

**决策：Factory fixtures + pytest fixture**

理由：
- Factory 模式可灵活创建测试数据
- fixture 自动清理（事务回滚）
- 避免硬编码测试数据

实现方式：
```python
# tests/fixtures/factories.py
class UserFactory:
    @staticmethod
    def create(session, **kwargs):
        user = User(
            openid=kwargs.get("openid", "test_openid"),
            nickname=kwargs.get("nickname", "测试用户"),
        )
        session.add(user)
        return user

class RecordFactory:
    @staticmethod
    def create(session, user, **kwargs):
        record = Record(
            user_id=user.id,
            type=kwargs.get("type", "feeding"),
            ...
        )
        session.add(record)
        return record
```

### 5. 集成测试结构

**决策：tests/integration/ 目录分离**

理由：
- 与单元测试目录分离（tests/）
- 便于选择性运行（pytest -m integration）
- 清晰区分测试类型

结构：
```
tests/
  conftest.py           # pytest fixtures
  fixtures/
    factories.py        # 测试数据工厂
  integration/
    test_models.py      # 模型与数据库映射测试
    test_services.py    # 服务层集成测试
    test_api.py         # API endpoints 集成测试
  test_*.py             # 单元测试
```

## Risks / Trade-offs

### Risk 1: Docker 未安装或无法启动
→ **Mitigation**: 提供安装文档和启动脚本，检测 Docker 是否可用

### Risk 2: 测试数据库端口冲突
→ **Mitigation**: 使用非标准端口 5433，并提供端口配置选项

### Risk 3: 测试数据污染
→ **Mitigation**: 每个测试使用独立事务，测试结束自动回滚

### Trade-off: Docker 增加测试启动时间
→ **Acceptance**: Docker PostgreSQL 启动约 2-3 秒，使用 tmpfs 加速；session-scoped fixture 一次启动复用

## Migration Plan

### Phase 1: 环境配置
1. 创建 Python 虚拟环境
2. 安装测试依赖
3. 创建 pytest.ini 和 conftest.py

### Phase 2: 测试数据库
1. 创建 docker-compose.test.yml
2. 创建启动/停止脚本
3. 验证数据库连接

### Phase 3: 测试 fixtures
1. 创建数据库 session fixture
2. 创建测试数据 factories
3. 创建测试用户 fixture

### Phase 4: 集成测试编写
1. 模型集成测试
2. 服务层集成测试
3. API endpoints 集成测试（需要认证 fixture）

### Phase 5: 单元测试修复
1. 确保 secrets_service 测试可运行
2. 更新现有测试使用新 fixtures