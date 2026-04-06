## ADDED Requirements

### Requirement: 系统必须内置婴儿生长发育标准值
系统 SHALL 内置 0-12 个月婴儿的各项指标标准范围，无需联网查询。

#### Scenario: 加载标准值数据
- **WHEN** 系统启动或首次访问标准值
- **THEN** 从本地文件加载标准值数据

#### Scenario: 按出生天数查询标准值
- **WHEN** 查询第 N 天的标准值
- **THEN** 返回对应天数的各项指标标准范围

### Requirement: 标准值必须包含核心指标
标准值数据 SHALL 包含以下指标：
- 体重（kg）
- 身长（cm）
- 排尿次数（次/天）
- 大便次数（次/天）
- 喂养次数（次/天）

#### Scenario: 体重标准值
- **WHEN** 查询任意天数的体重标准
- **THEN** 返回包含 min、max、avg 的范围值

#### Scenario: 排尿次数标准值
- **WHEN** 查询任意天数的排尿次数标准
- **THEN** 返回包含 min、max 的范围值

### Requirement: 标准值来源必须权威
标准值 SHALL 基于崔玉涛建议和浙江省妇保标准综合制定。

#### Scenario: 标准值标注来源
- **WHEN** 展示标准值数据
- **THEN** 标注数据来源为崔玉涛建议和浙江省妇保标准

### Requirement: 标准值数据文件结构
标准值 SHALL 以 JSON 格式存储，按天数索引。

#### Scenario: 标准值文件格式
- **WHEN** 读取标准值文件
- **THEN** 文件格式为标准 JSON，可按天数键名访问
