## 1. 准备工作

- [x] 1.1 备份当前 `__init__.py` 文件
- [x] 1.2 确认 `fcntl` 模块在目标系统可用（macOS 自带）

## 2. 实现文件锁定机制

- [x] 2.1 在文件顶部导入 `fcntl` 模块
- [x] 2.2 修改 `save_records_to_file` 函数添加排他锁（LOCK_EX）
- [x] 2.3 修改 `save_index` 函数添加排他锁
- [x] 2.4 修改 `load_records_from_file` 函数添加共享锁（LOCK_SH）
- [x] 2.5 修改 `load_index` 函数添加共享锁

## 3. 实现缓存失效机制

- [x] 3.1 修改 `record_create` 函数在创建前调用 `refresh_index()`
- [x] 3.2 修改 `record_query` 函数在查询前调用 `refresh_index()`
- [x] 3.3 修改 `record_list` 函数在列表前调用 `refresh_index()`
- [x] 3.4 确保 `update_index_for_record` 在写入后正确重建索引

## 4. 移除记录数据的进程级缓存

- [x] 4.1 确认 `load_records_from_file` 不使用任何全局缓存
- [x] 4.2 验证每次调用都从磁盘读取最新数据

## 5. 测试验证

- [x] 5.1 双进程并发写入测试（验证文件锁）
- [x] 5.2 跨 Session 数据可见性测试（验证缓存失效）
- [x] 5.3 性能回归测试（验证 I/O 开销可接受）

## 6. 部署与同步

- [x] 6.1 同步代码到 OpenClaw 技能目录 `~/.openclaw/skills/baby_diary_skill/`
- [x] 6.2 清理 `__pycache__` 缓存
- [x] 6.3 重启 OpenClaw Gateway
- [x] 6.4 执行最终跨 Session 可见性测试
