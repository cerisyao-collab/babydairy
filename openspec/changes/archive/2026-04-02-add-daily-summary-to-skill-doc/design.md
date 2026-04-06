## Context

`daily-summary-with-standards` 变更已完成实现，包括：
- 生长标准数据文件 `growth_standards.json`
- `daily_summary()` 函数 - 汇总当日记录
- `compare_with_standards()` 函数 - 对比分析
- `load_growth_standards()` 函数 - 加载标准值

但技能文档（SKILL.md）仍停留在初始版本，没有添加这些新功能的说明。

**当前状态**：
- 代码已实现并部署到 `~/.openclaw/skills/baby_diary_skill/`
- 技能文档未更新
- 用户无法通过技能文档了解新功能

## Goals / Non-Goals

**Goals:**
- 更新技能文档，添加 `daily_summary` 函数说明
- 添加生长标准数据说明
- 添加使用示例
- 明确数据存储结构（按月归档，按日查询）

**Non-Goals:**
- 不修改代码实现
- 不改变数据存储结构
- 不添加新功能

## Decisions

### 1. 文档结构

**决策**：在现有技能文档中添加新的技能端点章节

**理由**：保持与现有文档格式一致，便于用户查找

### 2. 标准值数据说明

**决策**：在注意事项中添加标准值数据来源说明

**理由**：用户需要知道数据来源和适用范围

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 文档与代码实现不一致 | 读取已实现的代码和 specs，确保文档准确 |
| 示例不正确 | 基于实际实现编写示例 |
