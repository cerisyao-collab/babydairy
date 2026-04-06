## Why

`daily-summary-with-standards` 变更已实现完成，但技能文档（SKILL.md）没有更新以反映新增的功能。用户无法通过技能文档了解如何使用每日近况总结、生长标准对比等功能。需要更新技能文档，添加这些已实现功能的说明。

## What Changes

- **更新 baby-diary 技能文档**：添加 `daily_summary`、`compare_with_standards` 等新函数的说明
- **添加生长标准数据说明**：说明标准值数据来源和使用方式
- **更新使用方法示例**：添加每日总结的使用示例
- **更新存储结构说明**：明确数据存储仍按月归档，但支持按日查询和总结

## Capabilities

### New Capabilities

- `skill-doc-update`: 技能文档更新，添加已实现功能的说明

### Modified Capabilities

- `baby-diary-skill`: 添加新功能文档说明（不修改代码，仅更新文档）

## Impact

- **影响文件**: `.claude/skills/baby-diary/SKILL.md` 和 `~/.openclaw/skills/baby_diary_skill/SKILL.md`
- **新增函数说明**: `daily_summary()`, `compare_with_standards()`, `load_growth_standards()`
- **向后兼容**: 不影响现有功能，纯文档更新
