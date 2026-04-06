## Why

新手父母面临"宝宝吃得够不够"的核心焦虑，现有系统仅提供基础记录和简单统计，缺乏智能分析和决策建议能力。需要引入 AI 分析功能，基于权威喂养指南提供个性化的喂养评估和可执行建议，降低育儿焦虑，建立用户信任。

## What Changes

- **新增** 喂养标准数据库（基于各省妇幼保健院指南）
- **新增** AI 喂养分析服务（规则引擎 + 通义千问 LLM）
- **新增** AI 分析 API 端点（分析、问答）
- **新增** 首页喂养建议展示（下次建议喂养时间）
- **增强** 每日报告功能（AI 生成个性化总结）
- **新增** 数据模型字段（宝宝性别、出生体重、喂养方式）

## Capabilities

### New Capabilities

- `feeding-standards`: 喂养标准数据库（按月龄/日龄的奶量、次数、间隔标准）
- `ai-analyzer`: AI 喂养分析服务（数据解读、状态判断、问题识别、建议生成）
- `qwen-integration`: 阿里云通义千问集成（LLM 调用、Prompt 管理、响应处理）

### Modified Capabilities

- `rest-api`: 新增 AI 分析相关端点（POST /api/ai/analyze, POST /api/ai/chat）
- `database-storage`: BabyConfig 模型增加 gender、birth_weight、feeding_type 字段

## Impact

- **代码变更**：
  - 新增 `src/services/ai_analyzer.py` (喂养分析核心)
  - 新增 `src/services/llm_service.py` (通义千问集成)
  - 新增 `src/api/ai.py` (AI 端点)
  - 新增 `src/data/feeding_standards.json` (标准数据)
  - 修改 `src/models/baby_config.py` (新增字段)
  - 修改 `src/services/summary_service.py` (AI 增强报告)

- **依赖变更**：
  - 新增 `dashscope>=1.14.0` (通义千问 SDK)
  - 新增 `tenacity>=8.2.0` (API 重试)

- **API 变更**：
  - 新增 POST /api/ai/analyze (分析喂养数据)
  - 新增 POST /api/ai/chat (AI 问答)
  - 修改 PUT /api/config/baby (支持新字段)

- **成本影响**：
  - 通义千问 API 调用：预估 ~5-10元/月 (100活跃用户)