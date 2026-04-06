## ADDED Requirements

### Requirement: 系统必须能存储宝宝基本信息配置
系统 SHALL 提供宝宝基本信息配置的持久化存储能力。

#### Scenario: 保存宝宝配置
- **WHEN** 用户设置宝宝出生日期
- **THEN** 配置保存到 `baby_config.json` 文件

#### Scenario: 读取宝宝配置
- **WHEN** 系统需要获取宝宝出生日期
- **THEN** 从 `baby_config.json` 文件读取配置

### Requirement: 宝宝配置必须包含出生日期
宝宝配置数据 SHALL 包含宝宝的出生日期（YYYY-MM-DD 格式）。

#### Scenario: 设置出生日期
- **WHEN** 用户设置出生日期
- **THEN** 日期格式为 YYYY-MM-DD

#### Scenario: 验证出生日期格式
- **WHEN** 设置无效的日期格式
- **THEN** 返回错误提示，不保存配置

### Requirement: 系统必须能自动读取配置计算出生天数
系统 SHALL 在生成每日总结时自动读取配置并计算出生天数。

#### Scenario: 自动生成总结
- **WHEN** 用户调用 `daily_summary(date)` 且未传入 `birth_date`
- **THEN** 自动从配置读取出生日期并计算出生天数

#### Scenario: 手动覆盖配置
- **WHEN** 用户调用 `daily_summary(date, birth_date)` 且传入 `birth_date`
- **THEN** 使用传入的 `birth_date` 而非配置中的值

#### Scenario: 配置不存在时的降级
- **WHEN** 配置文件不存在且未传入 `birth_date`
- **THEN** 生成不含出生天数的总结或提示用户设置

### Requirement: 必须提供配置管理函数
系统 SHALL 提供 `set_baby_config()` 和 `get_baby_config()` 函数。

#### Scenario: 设置配置
- **WHEN** 调用 `set_baby_config(birth_date="2026-03-01")`
- **THEN** 保存配置并返回成功状态

#### Scenario: 获取配置
- **WHEN** 调用 `get_baby_config()`
- **THEN** 返回当前配置的字典
