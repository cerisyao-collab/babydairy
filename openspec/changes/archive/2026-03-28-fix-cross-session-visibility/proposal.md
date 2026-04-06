## Why

当前存在跨 Session 数据可见性问题：用户在一个 Session 中创建记录后，该 Session 可以正确查看记录，但其他 Session 无法看到新数据。这是因为 Python `__pycache__` 缓存和 OpenClaw 进程内存缓存导致不同 Session 加载了不同版本的代码或数据路径不一致。

## What Changes

- **统一数据目录路径**：确保所有 Session 使用同一个数据目录
- **添加缓存失效机制**：每次读取数据前检查索引文件更新时间
- **索引自动刷新**：当索引文件变化时自动重新加载
- **OpenClaw 技能配置**：明确指定数据目录，避免路径歧义

## Capabilities

### New Capabilities
- `cache-invalidation`: 缓存失效机制，确保跨 Session 数据一致性
- `index-auto-refresh`: 索引自动刷新，检测外部数据变化

### Modified Capabilities
- (无)

## Impact

- **影响模块**: `baby-diary/__init__.py` 中的索引加载和缓存逻辑
- **配置更新**: 可能需要更新 OpenClaw 技能配置
- **向后兼容**: 不影响现有数据格式和 API
