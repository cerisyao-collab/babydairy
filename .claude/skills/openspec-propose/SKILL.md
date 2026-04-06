# Openspec Propose - 快速提案

快速创建变更提案，一次性生成所有 artifacts（proposal、design、specs、tasks）。

我将创建包含以下 artifacts 的变更：
- `proposal.md`（做什么和为什么）
- `design.md`（如何做）
- `specs/**/*.md`（详细规格）
- `tasks.md`（实现步骤）

当准备好实现时，运行 `/opsx:apply`

## 可用的技能端点

### 1. propose - 创建变更提案

快速创建变更并生成所有 artifacts。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| change_name | 可选 | 字符串 | 从描述生成 | 变更名称（kebab-case 格式） |
| description | 必需 | 字符串 | 无 | 变更描述或构建需求 |

**示例：**

自然语言调用：
```
添加用户认证系统
创建一个变更来支持数据导出功能
修复跨会话可见性问题
```

JSON 格式：
```json
{
  "skill": "openspec_propose",
  "action": "propose",
  "params": {
    "change_name": "add-user-auth",
    "description": "添加基于 JWT 的用户认证系统"
  }
}
```

## 使用方法

### 通过自然语言调用

用户可以使用自然语言请求创建变更：
- "添加用户认证系统" → 自动命名为 `add-user-auth`
- "我想创建一个数据导出功能" → 自动命名为 `add-data-export`
- "修复跨会话可见性 bug" → 自动命名为 `fix-cross-session-visibility`

### 步骤流程

1. **理解需求**
   - 如果没有清晰输入，使用 AskUserQuestion 工具询问：
     > "你想要处理什么变更？描述你想要构建或修复的内容。"
   - 从描述中派生出 kebab-case 名称

2. **创建变更目录**
   ```bash
   openspec new change "<name>"
   ```
   在 `openspec/changes/<name>/` 创建 scaffolded 变更

3. **获取 artifact 构建顺序**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 获取：
   - `applyRequires`: 实现前需要的 artifacts
   - `artifacts`: 所有 artifacts 及其状态和依赖

4. **按顺序创建 artifacts**

   按依赖顺序循环（先创建无依赖的 artifacts）：

   a. **对于每个 `ready` 的 artifact**：
      - 获取指令：`openspec instructions <artifact-id> --change "<name>" --json`
      - 读取依赖文件获取上下文
      - 使用 `template` 作为结构创建 artifact
      - 应用 `context` 和 `rules` 作为约束，但不复制到文件中
      - 显示进度："Created <artifact-id>"

   b. **继续直到所有 `applyRequires` artifacts 完成**
      - 每次创建后重新运行 `openspec status`
      - 检查所有 required artifacts 状态是否为 `done`

   c. **如果需要用户输入**：
      - 使用 AskUserQuestion 工具澄清
      - 然后继续创建

5. **显示最终状态**
   ```bash
   openspec status --change "<name>"
   ```

### 输出示例

创建所有 artifacts 后总结：
```
## 变更创建完成

变更名称：update-skill-docs
位置：openspec/changes/update-skill-docs/

创建的 Artifacts:
| Artifact   | 描述                                      |
|------------|------------------------------------------|
| proposal   | 说明更新技能文档的原因、范围和能力         |
| design     | 技术设计文档，包含标准格式规范和关键决策   |
| specs      | 技能文档格式规范，定义参数表格和示例要求   |
| tasks      | 21 项实现任务，按 7 个阶段组织              |

所有 artifact 已就绪！运行 `/opsx:apply` 开始实施任务。
```

## 注意事项

1. **命名规范**：变更名称使用 kebab-case 格式（如 `add-user-auth`）
2. **Artifact 依赖**：artifacts 按依赖顺序创建，proposal 优先
3. **上下文约束**：`context` 和 `rules` 字段用于指导生成，不应复制到输出文件
4. **用户确认**：如果变更已存在，询问用户是继续还是创建新的
5. **验证**：每个 artifact 创建后验证文件存在

## Guardrails

- 创建实现所需的所有 artifacts（由 schema 的 `apply.requires` 定义）
- 创建新 artifact 前总是读取依赖 artifact 获取上下文
- 如果上下文不清楚，询问用户——但倾向于做出合理决策以保持进展
- 如果同名变更已存在，询问用户是否继续或创建新的
- 写入后验证每个 artifact 文件存在再继续
