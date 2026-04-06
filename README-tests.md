# Baby Diary API - 测试说明

本文档说明如何运行单元测试和集成测试。

## 环境准备

### 1. 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动测试数据库（集成测试需要）

确保已安装 Docker，然后运行：

```bash
# 启动测试数据库
./scripts/start_test_db.sh

# 停止测试数据库
./scripts/stop_test_db.sh
```

测试数据库配置：
- 主机：localhost
- 端口：5433
- 数据库：baby_diary_test
- 用户：test
- 密码：test

## 运行测试

### 运行所有测试

```bash
# 激活虚拟环境后
pytest
```

### 运行单元测试（不需要数据库）

```bash
pytest -m unit
```

### 运行集成测试（需要 Docker 数据库）

```bash
# 先启动测试数据库
./scripts/start_test_db.sh

# 运行集成测试
pytest -m integration
```

### 运行特定测试文件

```bash
# 运行 secrets_service 测试
pytest tests/test_secrets_service.py -v

# 运行模型集成测试
pytest tests/integration/test_models.py -v
```

### 运行特定测试类或方法

```bash
# 运行特定类
pytest tests/integration/test_models.py::TestUserModel -v

# 运行特定方法
pytest tests/integration/test_models.py::TestUserModel::test_create_user -v
```

## 测试结构

```
tests/
├── conftest.py              # pytest fixtures 和配置
├── fixtures/
│   └── factories.py         # 测试数据工厂
├── integration/
│   ├── test_models.py       # 模型集成测试
│   ├── test_services.py     # 服务层集成测试
│   └── test_api.py          # API endpoints 集成测试
├── test_secrets_service.py  # secrets_service 单元测试
├── test_ai_analyzer.py      # AI 分析器单元测试
├── test_llm_service.py      # LLM 服务单元测试
└── api_test.py              # API 单元测试
```

## 测试标记

- `@pytest.mark.unit` - 单元测试（不需要数据库）
- `@pytest.mark.integration` - 集成测试（需要 Docker 数据库）

## 测试覆盖率

安装 pytest-cov 后可以查看覆盖率：

```bash
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

## 常见问题

### 1. 数据库连接失败

确保测试数据库已启动：

```bash
docker-compose -f docker-compose.test.yml ps
```

如果未启动，运行：

```bash
./scripts/start_test_db.sh
```

### 2. 端口 5433 被占用

检查是否有其他 PostgreSQL 实例：

```bash
lsof -i :5433
```

可以修改 `docker-compose.test.yml` 使用其他端口。

### 3. pytest 找不到模块

确保在项目根目录运行测试，并且已激活虚拟环境：

```bash
# 从项目根目录运行
cd /path/to/babyjour
source .venv/bin/activate
pytest
```

### 4. 测试数据冲突

集成测试使用事务回滚，每次测试后数据会自动清理。如果仍有问题，可以手动清理：

```bash
./scripts/stop_test_db.sh
./scripts/start_test_db.sh
```

## CI/CD 配置（未来）

可以配置 GitHub Actions 或其他 CI 系统自动运行测试：

```yaml
# 示例 GitHub Actions 配置
- name: Start Test Database
  run: docker-compose -f docker-compose.test.yml up -d

- name: Run Tests
  run: |
    source .venv/bin/activate
    pytest --cov=src

- name: Stop Test Database
  run: docker-compose -f docker-compose.test.yml down -v
```