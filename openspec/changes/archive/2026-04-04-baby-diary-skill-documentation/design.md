## Context

baby-diary 技能当前状态：
- 代码位于 `~/.openclaw/skills/baby_diary_skill/baby-diary/`
- 有 README.md 但没有符合 OpenClaw 规范的 SKILL.md
- 技能触发依赖隐式的文件名匹配，缺少明确的触发条件文档

OpenClaw 技能规范要求：
- SKILL.md 必须包含 YAML frontmatter（name 和 description）
- description 是主要触发机制
- 核心内容在 SKILL.md，详细内容可放在 references 文件

## Goals / Non-Goals

**Goals:**
- 创建符合 OpenClaw 规范的 SKILL.md 文档
- 明确技能触发条件和端点
- 提供清晰的使用示例
- 遵循技能创建流程的最佳实践

**Non-Goals:**
- 不修改现有代码逻辑
- 不创建新的技能端点
- 不重构现有技能结构

## Decisions

### 1. SKILL.md 结构

**决策**: 使用标准 OpenClaw 技能格式

**理由**:
- 与官方技能保持一致
- 便于 AI 理解和解析
- 支持技能打包和分发

### 2. 触发条件定义

**决策**: description 字段明确列出主要触发场景

**理由**:
- OpenClaw 通过 description 匹配技能
- 用户自然语言请求需要被准确识别
- 避免技能误触发

### 3. 文档组织

**决策**: 核心用法在 SKILL.md，详细 API 文档在 references

**理由**:
- 简洁优先，上下文窗口是公共资源
- 渐进式披露，用户需要时再加载详情

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SKILL.md 与实际代码不一致 | 定期审查和更新文档 |
| 触发条件过宽导致误触发 | 使用具体的描述词汇 |
| 触发条件过窄导致漏触发 | 列举常见使用场景 |

## Migration Plan

1. 创建 SKILL.md 初稿
2. 验证 YAML frontmatter 格式
3. 测试技能触发
4. 更新到所有技能目录

## Open Questions

- 是否需要为 baby-diary 创建 `.skill` 打包文件？
- 是否需要添加更多自然语言触发示例？
