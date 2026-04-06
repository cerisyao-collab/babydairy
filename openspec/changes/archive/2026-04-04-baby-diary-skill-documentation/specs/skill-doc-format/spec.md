## ADDED Requirements

### Requirement: SKILL.md 必须包含 YAML frontmatter
SKILL.md 文件 MUST 以 YAML frontmatter 开头，包含 name 和 description 字段。

#### Scenario: name 字段存在
- **WHEN** 解析 SKILL.md 时
- **THEN** MUST 找到 name 字段，值为技能名称（kebab-case 格式）

#### Scenario: description 字段存在
- **WHEN** 解析 SKILL.md 时
- **THEN** MUST 找到 description 字段，值描述技能功能

#### Scenario: description 包含触发场景
- **WHEN** 用户查看 SKILL.md 时
- **THEN** description MUST 列出常见的自然语言触发请求

### Requirement: SKILL.md 必须包含技能端点文档
SKILL.md MUST 记录所有可用的技能端点及其参数。

#### Scenario: 端点参数表格
- **WHEN** 用户查看端点文档时
- **THEN** MUST 看到参数表格（参数名、必需性、类型、默认值、说明）

#### Scenario: 端点使用示例
- **WHEN** 用户查看端点文档时
- **THEN** MUST 看到自然语言和 JSON 格式的调用示例

### Requirement: SKILL.md 必须包含使用方法说明
SKILL.md MUST 提供清晰的使用方法说明。

#### Scenario: 自然语言触发示例
- **WHEN** 用户查看 SKILL.md 时
- **THEN** MUST 看到 3 个以上的自然语言触发示例

#### Scenario: 端点调用格式
- **WHEN** 用户需要调用特定端点时
- **THEN** MUST 找到对应的参数说明和返回值

### Requirement: 技能命名必须符合规范
技能名称 MUST 遵循 OpenClaw 命名规范。

#### Scenario: 命名格式验证
- **WHEN** 创建技能时
- **THEN** 名称 MUST 仅使用小写字母、数字和连字符

#### Scenario: 名称长度验证
- **WHEN** 创建技能时
- **THEN** 名称长度 MUST 不超过 64 个字符
