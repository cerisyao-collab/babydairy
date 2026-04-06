## Why

宝宝日记技能已具备完整的记录管理和图片查看功能，并通过 OpenClaw agent 配置文件定义了技能端点。为了让 agent 在 Clawd 环境中具有一致的行为准则、身份认同和工作方式，需要创建一套 core files 来定义 agent 的人格、工具使用规范、记忆机制和启动引导流程。

## What Changes

- 创建 8 个 agent core files，位于 `/Users/hanyuxiao/clawd/` 目录：
  - `AGENTS.md` - Agent 协作规范
  - `SOUL.md` - 核心行为准则和人格定义
  - `TOOLS.md` - 工具使用指南
  - `IDENTITY.md` - 身份简讯
  - `USER.md` - 用户偏好和协作方式
  - `HEARTBEAT.md` - 会话节奏规范
  - `BOOTSTRAP.md` - 启动引导流程
  - `MEMORY.md` - 记忆系统索引和规范

## Capabilities

### New Capabilities
- `agent-core-files`: 定义 baby diary agent 的完整 core files 体系，包括人格、工具、记忆、启动流程

### Modified Capabilities
- (无)

## Impact

- 文件位置：`/Users/hanyuxiao/clawd/`
- 依赖：无
- 影响：agent 在 Clawd 环境中启动时将读取这些文件以建立一致的行为模式
