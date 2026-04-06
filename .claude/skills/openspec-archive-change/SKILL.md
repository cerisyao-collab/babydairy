# Openspec Archive Change - 归档变更

归档已完成的变更。

**输入**：可选指定变更名称。如果省略，检查是否可以从对话上下文中推断。如果模糊或歧义，必须提示选择可用变更。

## 可用的技能端点

### 1. archive - 归档已完成的变更

将已完成的变更移动到 archive 目录进行长期保存。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| change_name | 可选 | 字符串 | 从上下文推断 | 要归档的变更名称 |

**示例：**

自然语言调用：
```
归档 add-user-auth 变更
/archive add-data-export
归档这个变更
```

JSON 格式：
```json
{
  "skill": "openspec_archive_change",
  "action": "archive",
  "params": {
    "change_name": "add-user-auth"
  }
}
```

## 使用方法

### 步骤流程

1. **如果未提供变更名称，提示选择**

   运行 `openspec list --json` 获取可用变更。使用 AskUserQuestion 工具让用户选择。

   仅显示活动变更（未归档的）。如果可用，包含每个变更使用的 schema。

   **重要**：不要猜测或自动选择变更。总是让用户选择。

2. **检查 artifact 完成状态**

   运行 `openspec status --change "<name>" --json` 检查 artifact 完成状态。

   解析 JSON 了解：
   - `schemaName`: 使用的工作流
   - `artifacts`: artifacts 列表及其状态（`done` 或其他）

   **如果任何 artifact 未完成：**
   - 显示警告，列出未完成的 artifacts
   - 使用 AskUserQuestion 工具确认用户想要继续
   - 如果用户确认，继续

3. **检查任务完成状态**

   读取 tasks 文件（通常 `tasks.md`）检查未完成的任务。

   计算标记为 `- [ ]`（未完成）与 `- [x]`（已完成）的任务数量。

   **如果发现有未完成的任务：**
   - 显示警告，显示未完成的任务数量
   - 使用 AskUserQuestion 工具确认用户想要继续
   - 如果用户确认，继续

   **如果不存在 tasks 文件：** 继续进行，无需任务相关警告。

4. **评估 delta spec 同步状态**

   检查 delta specs 是否在 `openspec/changes/<name>/specs/`。如果不存在，无需同步提示直接继续。

   **如果 delta specs 存在：**
   - 比较每个 delta spec 与其对应的主 spec `openspec/specs/<capability>/spec.md`
   - 确定将应用哪些更改（添加、修改、移除、重命名）
   - 在提示前显示组合摘要

   **提示选项：**
   - 如果需要更改："立即同步（推荐）"，"不同步直接归档"
   - 如果已同步："立即归档"，"仍然同步"，"取消"

   如果用户选择同步，使用 Task 工具（subagent_type: "general-purpose", prompt: "使用 Skill 工具调用 openspec-sync-specs 进行变更 '<name>'。Delta spec 分析：<包含分析的 delta spec 摘要>"）。无论选择如何，继续归档。

5. **执行归档**

   如果不存在，创建归档目录：
   ```bash
   mkdir -p openspec/changes/archive
   ```

   使用当前日期生成目标名称：`YYYY-MM-DD-<change-name>`

   **检查目标是否已存在：**
   - 如果存在：失败并报错，建议重命名现有归档或使用不同日期
   - 如果不存在：移动变更目录

   ```bash
   mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>
   ```

6. **显示摘要**

   显示归档完成摘要，包括：
   - 变更名称
   - 使用的 schema
   - 归档位置
   - specs 是否同步（如果适用）
   - 任何警告说明（未完成的 artifacts/tasks）

### 输出示例

#### 成功时
```
## Archive Complete

**Change:** add-user-auth
**Schema:** spec-driven
**Archived to:** openspec/changes/archive/2026-03-30-add-user-auth/
**Specs:** ✓ Synced to main specs

All artifacts complete. All tasks complete.
```

#### 有警告时
```
## Archive Complete

**Change:** add-user-auth
**Schema:** spec-driven
**Archived to:** openspec/changes/archive/2026-03-30-add-user-auth/
**Specs:** No delta specs

⚠️ Warnings:
- 2 incomplete artifacts (design.md pending)
- 3 incomplete tasks

User confirmed archive with incomplete items.
```

## 注意事项

1. **日期格式**：归档目录使用 `YYYY-MM-DD-<change-name>` 格式
2. **冲突处理**：如果目标已存在，需要重命名或使用不同日期
3. **Spec 同步**：如果存在 delta specs，建议先同步到主 spec
4. **警告不阻塞**：未完成 artifacts/tasks 不会阻塞归档，但会提示确认
5. **Preserve .openspec.yaml**：移动时保留 `.openspec.yaml` 文件

## Guardrails

- 总是提示用户选择变更（如果未提供）
- 使用 artifact 图（`openspec status --json`）进行完成检查
- 不要在警告时阻塞归档——只需告知并确认
- 移动时保留 `.openspec.yaml`（随目录一起移动）
- 显示清晰的发生了什么事的摘要
- 如果存在 delta specs，总是运行同步评估并在提示前显示组合摘要
- 如果请求同步，使用 openspec-sync-specs 方法（agent-driven）
