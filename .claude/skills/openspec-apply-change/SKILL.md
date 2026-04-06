# Openspec Apply Change - 实现变更

实现 OpenSpec 变更中的任务。

**输入**：可选指定变更名称。如果省略，检查是否可以从对话上下文中推断。如果模糊或歧义，必须提示选择可用变更。

## 可用的技能端点

### 1. apply - 实现变更任务

按照 tasks.md 中的任务列表逐步实现变更。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| change_name | 可选 | 字符串 | 从上下文推断 | 变更名称 |

**示例：**

自然语言调用：
```
实现 add-user-auth 变更
继续实现 data-export 功能
/opsx:apply fix-cross-session-visibility
```

JSON 格式：
```json
{
  "skill": "openspec_apply_change",
  "action": "apply",
  "params": {
    "change_name": "add-user-auth"
  }
}
```

## 使用方法

### 步骤流程

1. **选择变更**

   如果提供了名称，使用它。否则：
   - 从对话上下文中推断（如果用户提到了变更）
   - 如果只有一个活动变更，自动选择
   - 如果模糊或歧义，运行 `openspec list --json` 并使用 AskUserQuestion 工具让用户选择

   总是宣布："Using change: <name>" 以及如何覆盖（例如 `/opsx:apply <other>`）。

2. **检查状态以理解 schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 了解：
   - `schemaName`: 使用的工作流（如 "spec-driven"）
   - 哪个 artifact 包含 tasks（通常 "tasks" 用于 spec-driven）

3. **获取 apply 指令**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   返回：
   - `contextFiles`: 上下文文件路径（因 schema 而异）
   - `progress`: 进度（total, complete, remaining）
   - `tasks`: 任务列表及状态
   - `instruction`: 基于当前状态的动态指令
   - `state`: 当前状态

   **处理状态：**
   - `state: "blocked"`（缺少 artifacts）：显示消息，建议使用 `/opsx:continue`
   - `state: "all_done"`：祝贺，建议 archive
   - 其他：继续实现

4. **读取上下文文件**

   读取 apply instructions 输出中 `contextFiles` 列出的文件。
   文件取决于使用的 schema：
   - **spec-driven**: proposal, specs, design, tasks
   - 其他 schema: 遵循 CLI 输出的 contextFiles

5. **显示当前进度**

   显示：
   - 使用的 schema
   - 进度："N/M tasks complete"
   - 剩余任务概述
   - CLI 的动态指令

6. **实现任务（循环直到完成或受阻）**

   对于每个待处理任务：
   - 显示正在处理的任务
   - 进行所需的代码更改
   - 保持更改最小化和专注
   - 在 tasks 文件中标记完成：`- [ ]` → `- [x]`
   - 继续下一个任务

   **暂停条件：**
   - 任务不清晰 → 询问澄清
   - 实现揭示设计问题 → 建议更新 artifacts
   - 遇到错误或阻塞 → 报告并等待指导
   - 用户中断

7. **完成或暂停时显示状态**

   显示：
   - 本次会话完成的任务
   - 总体进度："N/M tasks complete"
   - 如果全部完成：建议 archive
   - 如果暂停：解释原因并等待指导

### 输出示例

#### 实现过程中
```
## Implementing: add-user-auth (schema: spec-driven)

Working on task 3/7: 实现 JWT 令牌生成
[...实现进行中...]
✓ Task complete

Working on task 4/7: 添加认证中间件
[...实现进行中...]
✓ Task complete
```

#### 完成时
```
## Implementation Complete

**Change:** add-user-auth
**Schema:** spec-driven
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1: 创建用户模型
- [x] Task 2: 实现密码加密
- [x] Task 3: 实现 JWT 令牌生成
- [x] Task 4: 添加认证中间件
- [x] Task 5: 实现登录端点
- [x] Task 6: 实现登出端点
- [x] Task 7: 添加认证测试

All tasks complete! You can archive this change with `/opsx:archive`.
```

#### 暂停时
```
## Implementation Paused

**Change:** add-user-auth
**Schema:** spec-driven
**Progress:** 4/7 tasks complete

### Issue Encountered
JWT 过期时间配置不明确。design.md 中没有指定期望的过期时间。

**Options:**
1. 使用默认的 24 小时过期时间
2. 添加配置文件支持自定义过期时间
3. 更新 design.md 明确过期时间要求

What would you like to do?
```

## 注意事项

1. **任务进度跟踪**：每完成一个任务，立即在 tasks.md 中更新复选框
2. **上下文文件**：始终在开始实现前读取上下文文件
3. **最小化更改**：保持代码更改最小化，专注于当前任务
4. **暂停条件**：遇到模糊、错误或阻塞时暂停，不要猜测
5. **Fluid 工作流**：可以在任何时间调用，即使 artifacts 未全部完成

## Guardrails

- 继续处理任务直到完成或受阻
- 开始前总是读取上下文文件（从 apply instructions 输出）
- 如果任务模糊，实现前询问
- 如果实现揭示问题，建议更新 artifacts
- 保持代码更改最小化，限定在每个任务范围
- 完成每个任务后立即更新复选框
- 遇到错误、阻塞器或不清楚的需求时暂停——不要猜测
- 使用 contextFiles（从 CLI 输出），不要假设特定文件名

## Fluid Workflow Integration

此技能支持"变更上的行动"模型：

- **随时调用**：在所有 artifacts 完成前（如果有 tasks）、部分实现后、与其他行动交错
- **允许 artifact 更新**：如果实现揭示设计问题，建议更新 artifacts——不是阶段锁定，灵活工作
