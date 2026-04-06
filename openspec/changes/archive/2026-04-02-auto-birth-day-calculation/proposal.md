## Why

当前 `daily_summary` 函数需要手动传入 `birth_date` 参数才能计算出生天数，用户每次使用都需要记住并提供宝宝的出生日期，体验不佳。需要自动存储和读取宝宝的出生日期，实现一键生成总结。

## What Changes

- **宝宝信息存储**: 新增 `baby_config.json` 配置文件，存储宝宝出生日期等基本信息
- **自动读取出生日期**: `daily_summary` 函数自动从配置文件读取出生日期
- **简化调用**: 用户无需再手动传入 `birth_date` 参数

## Capabilities

### New Capabilities

- `baby-config`: 宝宝基本信息配置管理，包含出生日期等

### Modified Capabilities

- `daily-summary`: 修改为自动读取出生日期，无需手动传入参数

## Impact

- **新增数据文件**: `baby_config.json` 存储宝宝配置信息
- **修改函数**: `daily_summary()` 不再需要 `birth_date` 参数（向后兼容，仍支持手动传入）
- **向后兼容**: 配置文件不存在时，行为与当前一致（需要手动传入 `birth_date`）
