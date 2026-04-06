## Context

宝宝日记技能已有完整的功能实现和 OpenClaw agent 配置，但缺少 Clawd 环境下的 core files 来定义 agent 的行为准则和工作方式。Clawd 是一个 agent 运行框架，通过 core files 来持久化 agent 的身份、工具使用规范、记忆机制等。

## Goals / Non-Goals

**Goals:**
- 创建 8 个 core files，位于 `/Users/hanyuxiao/clawd/` 目录
- 基于 baby diary 技能的特性定制内容
- 保持简洁、实用、易于维护

**Non-Goals:**
- 不修改 baby diary 技能的代码
- 不改变 OpenClaw agent 配置
- 不创建复杂的代理逻辑

## Decisions

### 1. 文件结构
**Decision:** 遵循 Clawd core files 标准结构

**Rationale:**
- 与 Clawd 生态系统兼容
- 便于未来扩展
- 社区标准格式

### 2. 内容风格
**Decision:** 简洁、直接、实用主义

**Rationale:**
- agent 需要快速读取和理解
- 避免冗余的客套话
- 聚焦于可执行的行为准则

### 3. 记忆系统
**Decision:** 使用文件系统作为持久化记忆

**Rationale:**
- 简单可靠
- 易于调试
- 与 Clawd 设计一致

## Risks / Trade-offs

**Risk:** Clawd 规范可能变化
→ **Mitigation:** 保持文件内容简洁，易于更新

**Trade-off:** 简洁 vs 完整
→ 选择简洁优先，聚焦核心行为准则
