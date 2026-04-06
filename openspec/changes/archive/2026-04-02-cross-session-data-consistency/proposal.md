## Why

跨 Session 数据可见性问题导致用户在不同 Session 中查看数据时结果不一致：一个 Session 创建的记录，另一个 Session 无法看到。这是因为 Python 进程级内存缓存（`_index_cache`）和 `__pycache__` 导致的，需要实现可靠的缓存失效机制和文件锁定来确保数据一致性。

## What Changes

- **增强的缓存失效机制**：在现有 mtime 检查基础上，增加每次读取数据文件时的 freshness 检查
- **文件锁定机制**：在读写记录文件时使用文件锁，防止并发写入导致的数据损坏
- **强制刷新 API**：在关键查询操作前自动调用 `refresh_index()` 确保获取最新数据
- **移除进程级缓存**：对于记录数据（非索引）改用每次从磁盘读取的方式
- **添加会话标识**：可选地添加 session ID 追踪，便于调试跨 Session 问题

## Capabilities

### New Capabilities

- `file-locking`: 实现文件级锁定机制，确保并发读写时的数据一致性
- `cache-invalidation`: 增强的缓存失效策略，包括基于时间和基于事件的失效

### Modified Capabilities

- `record-storage`: 修改数据读取逻辑，移除记录数据的进程级缓存，确保每次读取最新文件内容

## Impact

- **受影响模块**: `src/baby_diary_skill/baby-diary/__init__.py`
- **依赖**: 可能需要引入 `fasteners` 或 `fcntl` 库实现文件锁定
- **向后兼容**: 现有 API 不变，内部实现优化
- **性能影响**: 移除记录缓存可能增加磁盘 I/O，但索引缓存仍保留
