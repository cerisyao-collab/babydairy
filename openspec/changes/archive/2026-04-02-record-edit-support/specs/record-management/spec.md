## ADDED Requirements

### Requirement: Get Record Function
系统必须提供按 ID 获取单条记录的接口。

#### Scenario: Get record by ID
- **WHEN** 调用 `record_get` 接口并传入有效的记录 ID
- **THEN** 返回该记录的完整信息

#### Scenario: Record not found
- **WHEN** 调用 `record_get` 接口但记录 ID 不存在
- **THEN** 返回错误消息，提示记录不存在

### Requirement: Update Record Function
系统必须提供按 ID 更新记录的接口。

#### Scenario: Update record details
- **WHEN** 调用 `record_update` 接口并传入记录 ID 和新的详情字段
- **THEN** 更新该记录的详情字段并返回成功消息

#### Scenario: Update record timestamp
- **WHEN** 调用 `record_update` 接口并传入记录 ID 和新的时间戳
- **THEN** 更新该记录的时间戳并返回成功消息

#### Scenario: Update record images
- **WHEN** 调用 `record_update` 接口并传入记录 ID 和新的图片列表
- **THEN** 更新该记录的图片引用并返回成功消息

#### Scenario: Update non-existent record
- **WHEN** 调用 `record_update` 接口但记录 ID 不存在
- **THEN** 返回错误消息，提示记录不存在

### Requirement: Delete Record Function
系统必须提供按 ID 删除记录的接口。

#### Scenario: Delete record
- **WHEN** 调用 `record_delete` 接口并传入有效的记录 ID
- **THEN** 删除该记录并返回成功消息

#### Scenario: Delete record with images
- **WHEN** 调用 `record_delete` 接口删除带有图片的记录
- **THEN** 删除记录并清理关联的图片文件

#### Scenario: Delete non-existent record
- **WHEN** 调用 `record_delete` 接口但记录 ID 不存在
- **THEN** 返回错误消息，提示记录不存在

### Requirement: Human-Readable Response for Edit Operations
系统必须为修改和删除操作生成自然语言响应。

#### Scenario: Update success response
- **WHEN** 记录更新成功
- **THEN** 返回包含更新后记录详情的友好提示

#### Scenario: Delete success response
- **WHEN** 记录删除成功
- **THEN** 返回确认删除的友好提示

#### Scenario: Error response
- **WHEN** 操作失败（记录不存在、ID 无效等）
- **THEN** 返回清晰的错误原因和可能的解决建议

## MODIFIED Requirements

### Requirement: Skill Interface for OpenClaw
系统必须提供 OpenClaw 兼容的 Skill 接口。

#### Scenario: Skill registration
- **WHEN** Skill 加载
- **THEN** 注册所需能力供 OpenClaw 调用

**更新内容：** 新增技能端点 `record_get`、`record_update`、`record_delete`
