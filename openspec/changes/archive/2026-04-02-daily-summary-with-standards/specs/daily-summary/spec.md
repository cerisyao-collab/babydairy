## ADDED Requirements

### Requirement: 系统必须能生成每日近况总结
系统 SHALL 自动生成指定日期的近况总结报告。

#### Scenario: 生成当日总结
- **WHEN** 用户请求生成今日总结
- **THEN** 汇总今日所有记录并生成报告

#### Scenario: 生成历史日期总结
- **WHEN** 用户请求生成历史某日总结
- **THEN** 汇总该日期所有记录并生成报告

### Requirement: 总结必须包含当日概况
近况总结 SHALL 包含当日记录概况信息。

#### Scenario: 记录总数统计
- **WHEN** 生成总结时
- **THEN** 显示当日记录总数

#### Scenario: 数据类型分布
- **WHEN** 生成总结时
- **THEN** 按记录类型（喂奶、大小便、生长指标等）分类统计

### Requirement: 总结必须按类别组织
近况总结 SHALL 按生长指标、喂养情况、排泄情况分类展示。

#### Scenario: 生长指标汇总
- **WHEN** 生成总结时
- **THEN** 汇总体重、身长、体温等生长指标记录

#### Scenario: 喂养情况汇总
- **WHEN** 生成总结时
- **THEN** 汇总喂奶次数、奶量、喂养方式等信息

#### Scenario: 排泄情况汇总
- **WHEN** 生成总结时
- **THEN** 汇总小便次数、大便次数及性状信息

### Requirement: 总结输出格式必须清晰
近况总结 SHALL 使用结构化的文本格式输出。

#### Scenario: 格式化输出
- **WHEN** 输出总结报告
- **THEN** 使用标题、分段、列表等格式化元素
