## Context

当前 baby-diary 技能使用按日存储的 JSON 文件结构，通过 `index.json` 跟踪每日文件的元数据。为优化性能实现了进程级缓存（`_index_cache`），但在多 Session 场景下导致数据可见性问题：

**现状**：
- 索引缓存使用全局变量 `_index_cache` 和 `_index_mtime`
- 已有基于 mtime 的缓存失效检查，但仅在 `load_index()` 中实现
- 记录数据加载 (`load_records_from_file`) 无缓存失效检查
- 无文件锁定机制，存在并发写入风险

**问题根因**：
1. OpenClaw Gateway 作为长时间运行的进程，Python 模块加载后 `_index_cache` 可能长期不失效
2. mtime 检查存在但不够可靠（同一秒内的多次修改可能漏检）
3. 记录数据直接读取但索引过期会导致文件列表不完整
4. 无文件锁，极端情况下并发写入可能导致数据损坏

## Goals / Non-Goals

**Goals:**
- 确保任何 Session 创建/修改的记录，其他 Session 立即可见
- 实现可靠的文件锁定防止并发写入问题
- 保持 API 向后兼容，不影响现有调用方式
- 性能影响最小化（保留索引缓存，优化失效策略）

**Non-Goals:**
- 不引入复杂的数据库系统（保持 JSON 文件存储）
- 不支持分布式多节点场景（仅单机多进程）
- 不改变现有的数据格式和存储结构

## Decisions

### 1. 文件锁定方案

**决策**: 使用 `fcntl` 实现排他性文件锁（仅 Unix/macOS）

**理由**:
- Python 标准库支持，无需额外依赖
- 适合当前单机场景
- `fasteners` 等库虽然跨平台但增加依赖

**实现**:
```python
import fcntl

def save_records_to_file(file_path: Path, records: List[Dict[str, Any]]) -> bool:
    with open(file_path, "w", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(records, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

**替代方案**:
- `fasteners` 库：跨平台支持，但增加依赖 → 舍弃
- 自定义锁文件：实现复杂，原子性问题 → 舍弃

### 2. 缓存失效策略

**决策**: 双重失效检查 + 关键操作强制刷新

**理由**:
- mtime 检查快速但可能漏检同一秒内的修改
- 每次读取都检查内容 hash 太慢
- 折中：关键操作（创建、删除、查询）前强制刷新索引

**实现**:
- `record_create`: 创建前刷新索引，创建后重建索引
- `record_query`: 查询前强制刷新索引
- `record_list`: 列表操作前强制刷新索引
- `load_index`: 保留 mtime 检查作为快速路径

### 3. 记录数据读取

**决策**: 记录数据不使用进程级缓存，每次从磁盘读取

**理由**:
- 记录文件较小（<200KB），读取开销低
- 确保数据新鲜度优先
- 索引缓存仍保留，减少文件系统访问

### 4. 写入后索引重建

**决策**: 每次写入后重建该日记录对应的索引条目

**理由**:
- 避免增量更新可能导致的元数据不一致
- 重建单个文件索引开销低
- 确保 `record_count`、`file_size` 等元数据准确

## Risks / Trade-offs

**[文件锁阻塞] →** 极端高并发下可能有锁竞争
- *缓解*: 当前场景为低频写入（每天几次），风险极低
- *监控*: 如出现性能问题可引入超时机制

**[频繁磁盘 I/O] →** 移除记录缓存可能影响读取性能
- *缓解*: 仅写入操作频繁时影响大，读操作影响有限
- *优化*: 未来可引入 LRU 缓存带 TTL

**[fcntl 跨平台兼容性] →** Windows 不支持 fcntl
- *缓解*: 当前仅运行在 macOS，如未来需 Windows 支持可条件导入

## Migration Plan

1. **备份现有代码**: 备份 `__init__.py`
2. **更新代码**: 应用新的文件锁和缓存失效逻辑
3. **同步到技能目录**: 复制到 `~/.openclaw/skills/baby_diary_skill/`
4. **清理缓存**: 删除 `__pycache__`
5. **重启 OpenClaw**: 确保新代码加载
6. **测试验证**: 双 Session 并发测试

**回滚**: 恢复备份的原始文件并重启 OpenClaw

## Open Questions

- 是否需要添加配置选项允许用户选择是否启用文件锁？
- 是否需要记录锁等待日志用于调试？
