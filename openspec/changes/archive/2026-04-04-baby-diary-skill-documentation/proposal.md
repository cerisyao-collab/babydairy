## Why

baby-diary 技能当前缺少符合 OpenClaw 规范的 SKILL.md 文档。现有文档分散在 README.md 和代码注释中，用户无法通过统一的技能文档了解如何使用该技能。需要创建标准格式的 SKILL.md，使技能可被发现、理解和复用。

**备注**: 验证发现 SKILL.md 已存在且包含完整的 20 个函数文档，此变更是对现有文档的确认和规范化。

## What Changes

- **验证 SKILL.md 文档**: 确认现有 SKILL.md 符合 OpenClaw 技能规范
- **整理技能端点**: 明确列出所有可用的技能端点和参数
- **添加使用示例**: 提供自然语言触发和 JSON 格式调用的示例
- **规范化技能结构**: 确保符合技能创建流程的要求

## Capabilities

### New Capabilities

- `skill-doc-format`: OpenClaw 技能文档格式规范，包含 YAML frontmatter 和 Markdown 指令

### Modified Capabilities

<!-- 无现有能力修改 -->

## Impact

- **验证文件**: `.claude/skills/baby-diary/SKILL.md` (已存在)
- **技能触发**: 通过自然语言如"记录宝宝喝奶"、"查询今天的大小便"等触发
- **向后兼容**: 不影响现有代码功能，纯文档验证
