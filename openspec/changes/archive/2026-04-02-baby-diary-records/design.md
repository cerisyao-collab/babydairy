## Context

这是一个为0-1岁新生儿设计的日常记录工具。当前阶段需要实现基本的记录能力，后续可能扩展数据分析、成长曲线等功能。

**约束条件：**
- 本地文件存储，无需后端服务
- 通过对话界面交互（OpenClaw skill）
- 文件格式需易读易手动编辑
- 图片需本地存储

## Goals / Non-Goals

**Goals:**
1. 支持多类型日常记录（喂奶、大小便、营养品、洗澡、睡眠、生长指标）
2. 图片attachments存储
3. 简单的日期范围查询
4. JSON格式存储，便于查看和备份
5. 按日期自动归档到不同文件

**Non-Goals:**
1. 云同步功能
2. 多用户支持
3. 数据导出为PDF等格式
4. 图表可视化（后续可能添加）
5. 数据库支持

## Decisions

### 1. 数据存储格式：JSON
**理由：**
- 人类可读，便于手动查看和编辑
- Edwardsím 读写简单
- 适合本地小规模数据

### 2. 文件组织：按月归档
**结构：** `records/` 目录下按 `YYYY-MM.json` 命名
```
baby-diary/
├── records/
│   ├── 2026-03.json
│   ├── 2026-04.json
│   └── ...
```
**理由：** 数据分散在多个小文件，便于管理和备份

### 3. 记录数据结构
```json
{
  "id": "uuid",
  "type": "feeding|bowel|urine|bathing|sleep|medication|growth",
  "timestamp": "2026-03-25T10:30:00Z",
  "date": "2026-03-25",
  "details": {...},
  "images": ["path/to/image.jpg"]
}
```
**理由：** 统一结构便于查询，type字段区分记录类型

### 4. 图片存储
- 图片保存在 `records/images/` 目录
- 文件名格式：`{record_id}-{original_name}`
**理由：** 图片与记录关联紧密，放在records目录下便于管理

### 5. OpenClaw Skill接口
Skill需提供：
- `record_create`: 创建新记录
- `record_query`: 按日期/类型查询
- `record_list`: 列出某日所有记录

## Risks / Trade-offs

| 风险 | 缓解方案 |
|------|----------|
| 图片文件过多导致目录混乱 | 定期清理或归档，图片命名包含record_id便于追踪 |
| JSON文件手动编辑出错 | 提供清晰的模板和注释 |
| 查询性能随数据量增长下降 | 初期可接受，未来可考虑简单索引或数据库迁移 |
| 图片路径硬编码问题 | 使用相对路径，移动目录时需同步更新 |

## Migration Plan

1. 创建目录结构：`src/baby-diary/records/` 和 `src/baby-diary/records/images/`
2. 实现数据模型和存储逻辑
3. 实现Skill接口
4. 测试记录创建和查询功能

## Open Questions

1. 是否需要支持记录编辑功能？
2. 图片是否需要缩略图生成？
3. 是否需要备份自动压缩功能？
