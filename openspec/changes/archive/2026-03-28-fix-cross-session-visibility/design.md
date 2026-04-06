## Context

当前宝宝日记技能使用按日存储结构，数据存储在 `/Users/hanyuxiao/Documents/baby-diary/records/`。但存在跨 Session 数据可见性问题：
- Session A 创建记录后可立即查看
- Session B 无法看到 Session A 创建的数据
- 原因：Python 缓存、索引未实时刷新、数据路径不一致

## Goals / Non-Goals

**Goals:**
- 确保所有 Session 能实时看到一致的数据
- 实现索引自动刷新机制
- 统一数据目录路径
- 清除缓存导致的 inconsistencies

**Non-Goals:**
- 不改变数据存储格式
- 不改变 API 接口
- 不迁移现有数据

## Decisions

### 1. 索引缓存策略
**Decision:** 每次查询时检查索引文件的修改时间，如果索引文件变化则重新加载

**Rationale:**
- 保证数据一致性优先
- 索引文件很小（<2KB），读取开销低
- 避免复杂的缓存同步逻辑

### 2. 数据目录固定
**Decision:** 固定使用 `~/Documents/baby-diary/records/` 作为唯一数据目录

**Rationale:**
- 消除路径歧义
- Documents 目录独立于技能代码
- 便于备份和管理

### 3. 强制刷新 API
**Decision:** 添加 `refresh_index()` 函数，允许主动刷新缓存

**Rationale:**
- 创建记录后可以主动刷新
- 提供调试和诊断能力

## Risks / Trade-offs

**Risk:** 每次读取索引可能增加延迟
→ **Mitigation:** 索引文件很小，实际延迟可忽略（<1ms）

**Risk:** 多进程同时写入索引可能冲突
→ **Mitigation:** 单进程写入（record_create），其他操作只读

**Trade-off:** 实时性 vs 性能
→ 选择实时性优先，索引文件足够小
