## MODIFIED Requirements

### Requirement: Skill Interface for OpenClaw
系统必须提供 OpenClaw 兼容的 Skill 接口。

#### Scenario: Skill registration
- **WHEN** Skill 加载
- **THEN** 注册所需能力供 OpenClaw 调用

**更新内容：** 新增技能端点 `record_get`、`record_update`、`record_delete`

### Requirement: Create Record Function
系统必须提供创建新记录的接口。

#### Scenario: Create via skill
- **WHEN** OpenClaw 调用 `record_create` 技能
- **THEN** 创建并存储新记录，返回成功消息和记录 ID

**更新内容：** 返回的记录 ID 可用于后续的 `record_update` 和 `record_delete` 操作
