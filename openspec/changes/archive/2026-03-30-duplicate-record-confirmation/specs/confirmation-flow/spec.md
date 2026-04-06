## ADDED Requirements

### Requirement: 检测到相似记录时必须请求用户确认
系统 SHALL 在检测到相似记录时暂停创建流程并请求用户确认。

#### Scenario: 用户确认继续创建
- **WHEN** 系统展示相似记录并请求确认，用户选择继续
- **THEN** 系统创建新记录

#### Scenario: 用户取消创建
- **WHEN** 系统展示相似记录并请求确认，用户选择取消
- **THEN** 系统放弃创建新记录并返回取消状态

### Requirement: 展示相似记录信息
系统 SHALL 向用户展示已有相似记录的关键信息以供决策。

#### Scenario: 展示相似记录的 timestamp
- **WHEN** 请求用户确认
- **THEN** 展示已有记录的时间戳

#### Scenario: 展示相似记录的详情
- **WHEN** 请求用户确认
- **THEN** 展示已有记录的关键详情（如喂奶类型、奶量等）

### Requirement: 支持跳过确认
系统 SHALL 允许调用方指定跳过确认流程。

#### Scenario: 使用 skip_confirmation 参数
- **WHEN** 调用 record_create 时传入 skip_confirmation=True
- **THEN** 系统跳过确认流程直接创建记录

### Requirement: 确认超时自动取消
系统 SHALL 在确认请求超时后自动取消创建。

#### Scenario: 确认超时
- **WHEN** 用户在规定时间内未响应确认请求
- **THEN** 系统自动取消创建并返回超时状态
