## Why

当前 baby-diary 系统支持创建和查询记录，但缺少修改和删除功能。当用户记录错误时（如时间、奶量、类型等输入错误），无法进行修正，只能保留错误数据，影响记录的准确性和可用性。需要添加记录的编辑和删除能力，让用户可以修正错误记录。

## What Changes

- 新增 `record_update` 接口：支持修改现有记录的任意字段
- 新增 `record_delete` 接口：支持删除单条记录
- 扩展 OpenClaw Skill 端点：
  - `record_update`: 按 ID 更新记录
  - `record_delete`: 按 ID 删除记录
- 新增记录查询接口 `record_get`: 按 ID 获取单条记录详情
- 数据持久化逻辑更新：支持记录的删除和修改

## Capabilities

### New Capabilities
- `record-management`: 记录管理能力，定义记录的更新、删除、获取单条记录的接口和行为

### Modified Capabilities
- `conversation-interface`: 新增修改和删除记录的自然语言交互场景

## Impact

- 修改：`src/baby-diary/__init__.py` - 新增 `record_update`, `record_delete`, `record_get` 函数
- 修改：`src/baby_diary_skill.py` - 新增 `record_update`, `record_delete`, `record_get` 技能端点
- 修改：`src/baby-diary/README.md` - 新增使用示例文档
- 数据影响：现有 JSON 记录文件需要支持删除和修改操作
