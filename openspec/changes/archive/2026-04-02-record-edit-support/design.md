## Context

baby-diary 系统已实现记录创建和查询功能，数据存储在按月归档的 JSON 文件中。当用户记录错误时，目前无法修改或删除，需要添加记录编辑和删除能力。

**约束条件：**
- 保持现有数据存储格式（JSON 按月归档）
- 通过 OpenClaw Skill 接口调用
- 修改/删除操作需实时反映到文件
- 删除的图片需要清理

## Goals / Non-Goals

**Goals:**
1. 实现按 ID 获取单条记录的 `record_get` 接口
2. 实现按 ID 更新记录的 `record_update` 接口
3. 实现按 ID 删除记录的 `record_delete` 接口
4. 扩展 OpenClaw Skill 支持新增的三个端点
5. 删除记录时同步清理关联的图片文件
6. 提供友好的错误处理（记录不存在、ID 无效等）

**Non-Goals:**
1. 批量修改/删除功能
2. 操作历史记录/审计日志
3. 软删除功能
4. 版本控制/回滚功能
5. 云同步功能

## Decisions

### 1. 记录更新策略：整条替换
**理由：**
- JSON 存储结构简单，直接替换整条记录
- 不合并字段，避免复杂的部分更新逻辑
- 保留原始记录的 id 字段，不允许修改

### 2. 记录删除策略：物理删除 + 图片清理
**理由：**
- JSON 文件小，删除后重写文件成本低
- 删除记录时同步删除关联图片，避免孤立文件
- 不提供软删除，简化实现

### 3. ID 作为唯一标识
**理由：**
- 现有记录已使用 UUID 作为 id
- 通过 ID 定位记录，不依赖日期
- 需要先查询记录确定所在月份文件

### 4. Skill 接口参数设计
**record_update 参数：**
- `record_id` (必需): 要更新的记录 ID
- `details` (可选): 更新的详情字段
- `timestamp` (可选): 更新时间戳
- `images` (可选): 更新的图片列表

**record_delete 参数：**
- `record_id` (必需): 要删除的记录 ID

### 5. 错误处理
**场景：**
- 记录不存在：返回错误消息
- ID 格式无效：返回错误消息
- 文件读写失败：返回错误消息

## Risks / Trade-offs

| 风险 | 缓解方案 |
|------|----------|
| 删除记录时图片清理失败 | 操作前记录图片路径，删除失败时提示用户手动清理 |
| 并发修改导致数据丢失 | 当前为单用户场景，暂不考虑；未来可加文件锁 |
| 修改记录后日期变化导致文件迁移复杂 | 暂不支持修改 date 字段，如需要则先删除后创建 |
| JSON 文件频繁读写性能 | 初期数据量小可接受；未来可考虑缓存层 |

## Migration Plan

1. 在 `src/baby-diary/__init__.py` 中实现：
   - `record_get(record_id)`: 按 ID 获取记录
   - `record_update(record_id, details, timestamp, images)`: 更新记录
   - `record_delete(record_id)`: 删除记录

2. 在 `src/baby_diary_skill.py` 中添加 Skill 端点：
   - `record_get` 端点
   - `record_update` 端点
   - `record_delete` 端点

3. 更新 `src/baby-diary/README.md` 文档，添加使用示例

4. 测试：
   - 创建记录后更新
   - 创建记录后删除
   - 删除带图片的记录
   - 错误场景测试

## Open Questions

1. 是否需要支持部分字段更新（而非整条替换）？
2. 是否需要操作确认步骤（如删除前确认）？
3. 是否需要记录最后修改时间？
