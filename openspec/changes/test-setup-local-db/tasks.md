## 1. Python 虚拟环境配置

- [ ] 1.1 创建 Python 虚拟环境 (.venv) - **需要用户执行**
- [ ] 1.2 激活虚拟环境并安装测试依赖 - **需要用户执行**
- [ ] 1.3 验证 pytest 可以运行 - **需要用户执行**

## 2. pytest 配置

- [x] 2.1 创建 pytest.ini 配置文件
- [x] 2.2 创建 tests/conftest.py 基础结构
- [x] 2.3 创建 .env.test 测试环境配置文件

## 3. Docker 测试数据库

- [x] 3.1 创建 docker-compose.test.yml 配置
- [x] 3.2 创建 scripts/start_test_db.sh 启动脚本
- [x] 3.3 创建 scripts/stop_test_db.sh 停止脚本
- [ ] 3.4 验证 Docker PostgreSQL 可以启动 - **需要用户执行**

## 4. pytest fixtures

- [x] 4.1 实现 session-scoped test_db fixture（启动数据库）
- [x] 4.2 实现 function-scoped db_session fixture（事务回滚）
- [x] 4.3 创建 tests/fixtures/factories.py 测试数据工厂
- [x] 4.4 实现 UserFactory 创建测试用户
- [x] 4.5 实现 RecordFactory 创建测试记录
- [x] 4.6 实现 test_user fixture（预创建测试用户）

## 5. 模型集成测试

- [x] 5.1 创建 tests/integration/test_models.py
- [x] 5.2 测试 User 模型创建和查询
- [x] 5.3 测试 Record 模型创建和查询
- [x] 5.4 测试 BabyConfig 模型创建和查询
- [x] 5.5 测试 User-Record 关系映射

## 6. 服务层集成测试

- [x] 6.1 创建 tests/integration/test_services.py
- [x] 6.2 测试 AuthService 登录流程（mock 微信 API）
- [x] 6.3 测试 RecordService CRUD 操作
- [x] 6.4 测试 ConfigService 配置读写

## 7. API 集成测试

- [x] 7.1 创建 tests/integration/test_api.py
- [x] 7.2 实现 authenticated_client fixture
- [x] 7.3 测试认证 endpoints（登录、profile）
- [x] 7.4 测试 records endpoints CRUD
- [x] 7.5 测试 config endpoints

## 8. 单元测试修复

- [ ] 8.1 确保 test_secrets_service.py 可以运行 - **需要用户验证**
- [ ] 8.2 更新现有单元测试使用新 fixtures
- [ ] 8.3 运行所有测试验证通过 - **需要用户执行**

## 9. 文档

- [x] 9.1 创建测试运行说明文档（README-tests.md）
- [x] 9.2 添加测试覆盖率检查配置