## Why

宝宝日记技能需要一个 OpenClaw Agent 配置文件（小龙虾 agent），以便在 OpenClaw 平台中被识别和调用。当前技能已经实现了所有核心功能，但缺少标准化的 Agent 配置文件来定义技能的能力、端点和交互方式。

## What Changes

- 创建 OpenClaw 小龙虾 agent core file
- 定义技能元数据（名称、描述、版本、作者）
- 配置所有可用的技能端点（record_create, record_query, record_list, record_get, record_update, record_delete, image_view, list_images, image_gallery）
- 定义每个端点的参数 schema 和描述
- 配置技能的触发条件和上下文

## Capabilities

### New Capabilities
- `openclaw-agent-config`: OpenClaw 小龙虾 agent 配置能力，定义技能的标准化接口

### Modified Capabilities
- 无

## Impact

- 新增文件：`baby_diary.agent.yaml` 或 `baby_diary.json`（OpenClaw agent core file）
- OpenClaw 平台可以正确识别和调用宝宝日记技能
- 用户体验提升：通过自然语言与技能交互
