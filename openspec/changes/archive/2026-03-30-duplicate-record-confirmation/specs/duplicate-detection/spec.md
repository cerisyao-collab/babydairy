## ADDED Requirements

### Requirement: 系统必须检测时间窗口内的相似记录
系统 SHALL 在创建新记录前检查指定时间窗口内是否存在相同类型的已有记录。

#### Scenario: 检测到相似记录
- **WHEN** 用户尝试创建一条记录，且 5 分钟内已存在同类型记录
- **THEN** 系统检测到相似记录并返回相似记录列表

#### Scenario: 未检测到相似记录
- **WHEN** 用户尝试创建一条记录，且时间窗口内无同类型记录
- **THEN** 系统允许继续创建流程

#### Scenario: 时间窗口可配置
- **WHEN** 调用检测函数时传入不同的窗口参数
- **THEN** 系统使用指定的时间窗口进行检测

### Requirement: 相似记录判定基于记录类型
系统 SHALL 仅比较记录类型，同类型即视为相似。

#### Scenario: 同类型记录判定为相似
- **WHEN** 新记录类型为 feeding，已有记录类型也为 feeding
- **THEN** 判定为相似记录

#### Scenario: 不同类型记录不判定为相似
- **WHEN** 新记录类型为 feeding，已有记录类型为 urine
- **THEN** 不判定为相似记录

### Requirement: 时间窗口计算基于 timestamp
系统 SHALL 使用记录的 timestamp 字段计算时间差。

#### Scenario: 时间差在窗口内
- **WHEN** 新记录 timestamp 与已有记录 timestamp 相差 3 分钟，窗口为 5 分钟
- **THEN** 判定为相似记录

#### Scenario: 时间差超出窗口
- **WHEN** 新记录 timestamp 与已有记录 timestamp 相差 10 分钟，窗口为 5 分钟
- **THEN** 不判定为相似记录
