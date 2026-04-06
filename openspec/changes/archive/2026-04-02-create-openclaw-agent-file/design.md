## Context

宝宝日记技能目前已经实现了完整的记录管理功能（创建、查询、更新、删除）和图片查看功能。为了在 OpenClaw 平台上作为标准 Agent 被调用，需要创建一个符合 OpenClaw 规范的小龙虾 agent core file。

## Goals / Non-Goals

**Goals:**
- 创建符合 OpenClaw 规范的 agent 配置文件
- 定义所有 9 个技能端点及其参数 schema
- 配置技能元数据（名称、描述、版本、作者）
- 支持自然语言触发技能调用

**Non-Goals:**
- 不修改现有技能实现
- 不改变技能的数据存储方式
- 不添加新的业务逻辑

## Decisions

### 1. 文件格式
**Decision:** 使用 YAML 格式作为 agent 配置文件

**Rationale:**
- YAML 比 JSON 更易读
- OpenClaw 社区标准格式
- 支持注释，便于维护

### 2. 文件位置
**Decision:** 文件放置在 `src/baby_diary_skill/baby_diary.agent.yaml`

**Rationale:**
- 与技能代码在同一目录，便于管理
- 遵循 OpenClaw 命名规范

### 3. 端点定义
**Decision:** 完整定义 9 个端点：record_create, record_query, record_list, record_get, record_update, record_delete, image_view, list_images, image_gallery

**Rationale:**
- 覆盖所有现有功能
- 提供完整的技能接口文档

## Risks / Trade-offs

**Risk:** OpenClaw 规范可能变化
→ **Mitigation:** 保持配置文件简洁，易于更新

**Trade-off:** 详细 schema vs 维护成本
→ 选择平衡：关键字段定义 schema，简单字段简化处理
