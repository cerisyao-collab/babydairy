## Why

当前技能文档存在格式不统一、详细程度不一致、触发条件和参数说明不够清晰的问题。这导致用户在使用技能时可能感到困惑，也无法充分利用技能的全部功能。需要统一改进技能文档，提升用户体验。

## What Changes

- **统一文档格式**: 所有技能文档采用一致的结构（参照 baby-diary 技能格式）
- **增加详细度和示例**: 为每个技能添加更多使用场景和代码示例
- **更新触发条件/参数**: 明确每个技能的触发条件、必需/可选参数、默认值
- **扩展技能类型说明**: 添加技能类型表格、最佳实践、注意事项

## Capabilities

### New Capabilities

本变更不引入新的代码能力，而是改进现有技能文档：
- `skill-doc-format`: 统一的技能文档格式规范
- `skill-examples`: 丰富的使用示例库

### Modified Capabilities

无修改现有代码能力，仅更新文档。

## Impact

- **受影响文件**:
  - `.claude/skills/openspec-explore/SKILL.md`
  - `.claude/skills/openspec-propose/SKILL.md`
  - `.claude/skills/openspec-apply-change/SKILL.md`
  - `.claude/skills/openspec-archive-change/SKILL.md`
  - `.claude/skills/baby-diary/SKILL.md`（作为参考基准）
- **依赖**: 无
- **向后兼容**: 完全兼容，仅文档更新
