## Why

用户在短时间内可能意外创建重复记录（如 1 分钟内多条相同类型的喂奶记录），导致数据冗余和统计不准确。需要在创建记录前检测短时间内的相似记录并请求用户确认，防止重复录入。

## What Changes

- **重复检测逻辑**: 在 `record_create` 函数中添加检测逻辑，检查指定时间窗口内是否存在相似记录
- **用户确认机制**: 检测到相似记录时暂停创建，向用户展示已有记录并请求确认
- **可配置时间窗口**: 允许用户定义"短时间"的时长（默认 5 分钟）
- **相似记录定义**: 按记录类型判断相似性（同类型即视为相似）

## Capabilities

### New Capabilities

- `duplicate-detection`: 检测短时间内是否存在相似记录的功能
- `confirmation-flow`: 创建记录前的用户确认交互流程

### Modified Capabilities

- `record-create`: 修改创建流程，在写入前增加重复检测和确认步骤

## Impact

- **受影响模块**: `src/baby_diary_skill/baby-diary/__init__.py` 中的 `record_create` 函数
- **API 变化**: `record_create` 函数可能需要返回确认状态或抛出确认异常
- **依赖**: 无额外依赖
- **向后兼容**: 现有调用方式需要处理确认流程
