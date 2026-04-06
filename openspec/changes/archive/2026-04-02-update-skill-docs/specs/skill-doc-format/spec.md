## ADDED Requirements

### Requirement: 技能文档格式规范

所有技能文档必须遵循以下格式规范：

1. **Frontmatter**: 使用 YAML frontmatter 包含 name, description, license, compatibility, metadata
2. **标题结构**: 采用 Markdown 标题层级 (# 主标题，## 主要章节，### 子章节)
3. **参数表格**: 使用 Markdown 表格列出所有参数
4. **代码示例**: 提供自然语言示例和 JSON 格式示例

#### Scenario: 文档结构验证
- **WHEN** 检查技能文档格式
- **THEN** 必须包含 frontmatter、主标题、技能端点章节、参数表格、使用示例

### Requirement: 参数说明规范

每个技能端点的参数必须包含：
- 参数名称
- 是否必需（必需/可选）
- 参数类型（字符串/数字/布尔值/对象/数组）
- 默认值（如果是可选参数）
- 参数说明

#### Scenario: 参数表格完整性
- **WHEN** 编写技能端点文档
- **THEN** 必须使用参数表格，包含所有五列信息

### Requirement: 使用示例规范

每个技能必须包含：
- 至少一个自然语言调用示例
- 至少一个 JSON 格式的参数示例
- 示例应覆盖常见使用场景

#### Scenario: 示例完整性
- **WHEN** 用户阅读技能文档
- **THEN** 能够通过示例理解如何调用该技能
