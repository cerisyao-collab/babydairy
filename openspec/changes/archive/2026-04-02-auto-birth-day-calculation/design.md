## Context

当前 `daily_summary(date, birth_date)` 函数需要每次调用时手动传入 `birth_date` 参数。用户需要先查询或记住宝宝的出生日期，使用体验不够便捷。

**现状**:
- 出生天数计算功能已实现 (`get_birth_day` 函数)
- 需要手动传入 `birth_date` 参数
- 无宝宝基本信息存储

**需求**:
- 存储宝宝出生日期
- 自动生成总结时自动计算出生天数
- 保持向后兼容

## Goals / Non-Goals

**Goals:**
- 实现宝宝出生日期的持久化存储
- `daily_summary` 自动读取并使用出生日期
- 支持手动覆盖出生日期参数
- 提供设置/修改出生日期的功能

**Non-Goals:**
- 不存储复杂的宝宝信息（仅出生日期）
- 不支持多宝宝场景（单宝宝设计）
- 不修改现有的记录创建逻辑

## Decisions

### 1. 配置数据结构

**决策**: 使用 JSON 文件存储宝宝配置

**理由**:
- 与现有数据存储格式一致
- 易于扩展（未来可添加昵称、性别等）
- 可离线访问

**实现**:
```json
{
  "baby_name": "宝宝",
  "birth_date": "2026-03-01",
  "notes": "预产期提前/推后可在此备注"
}
```

### 2. 函数签名设计

**决策**: `daily_summary(date, birth_date)` 保持参数不变，内部自动读取

**理由**:
- 向后兼容：已传入 `birth_date` 时使用传入值
- 简化调用：不传 `birth_date` 时自动读取配置
- 灵活性：可临时覆盖配置中的出生日期

**实现**:
```python
def daily_summary(date=None, birth_date=None):
    if birth_date is None:
        config = load_baby_config()
        birth_date = config.get('birth_date')
    # 继续原有逻辑...
```

### 3. 配置管理函数

**决策**: 新增 `set_baby_config()` 和 `get_baby_config()` 函数

**理由**:
- 提供清晰的配置管理接口
- 便于用户设置和查看配置
- 可扩展其他配置项

### 4. 配置文件位置

**决策**: 与 `growth_standards.json` 同目录存储

**理由**:
- 配置相关文件集中管理
- 易于备份和迁移

## Risks / Trade-offs

**[配置文件不存在] →** 用户未设置出生日期
- *缓解*: 函数降级为当前行为（需要手动传入）
- *缓解*: 提供友好的提示信息

**[配置文件数据错误] →** 日期格式不正确
- *缓解*: 验证日期格式，错误时使用默认行为
- *缓解*: 提供配置检查和修复功能

**[多宝宝场景] →** 不支持
- *缓解*: 当前设计针对单宝宝，未来可扩展

## Migration Plan

1. 创建 `baby_config.json` 文件
2. 实现 `load_baby_config()` 和 `set_baby_config()` 函数
3. 修改 `daily_summary()` 自动读取配置
4. 同步代码到 OpenClaw 技能目录
5. 清理缓存并重启 Gateway
6. 测试验证

**回滚**: 恢复备份的原始文件

## Open Questions

- 是否需要提供命令行工具设置出生日期？
- 是否需要在配置中存储宝宝昵称用于总结输出？
