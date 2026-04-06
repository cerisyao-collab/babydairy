## Why

当前技能支持喂奶、大小便、睡眠等日常记录，但缺少病情记录功能。父母需要记录宝宝的疾病症状、就医情况、用药治疗等信息，以便追踪健康状况和向医生提供完整的病史。这是一个重要的健康管理需求。

## What Changes

- 新增 `illness`（病情）记录类型
- 支持记录症状、病因、诊断结果、治疗方案等字段
- 支持记录体温、精神状态等病情相关指标
- 支持关联就医记录和用药记录
- 在查询和列表功能中支持病情记录

## Capabilities

### New Capabilities
- `illness-record`: 病情记录能力，支持记录宝宝疾病、症状、就医、治疗等信息

### Modified Capabilities
- `baby-diary`: 新增 illness 记录类型到 RECORD_TYPES 和 RECORD_TYPE_DETAILS

## Impact

- 前端：无变化
- 后端：
  - `RECORD_TYPES` 添加 "illness"
  - `RECORD_TYPE_DETAILS` 添加病情字段定义
  - `RECORD_TYPE_NAMES` 添加中文名称
- 数据存储：病情记录存储在同一 JSON 文件中，无结构变更
- OpenClaw 技能：添加新的端点说明
