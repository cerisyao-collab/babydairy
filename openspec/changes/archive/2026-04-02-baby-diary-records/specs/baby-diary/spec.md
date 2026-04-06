## ADDED Requirements

### Requirement: Baby Diary Record Structure
系统必须定义标准化的新生儿记录数据结构，包含通用字段和类型特定字段。

#### Scenario: Record creation with valid data
- **WHEN** 创建一条喂奶记录，包含时间、时长、奶量、左右侧信息
- **THEN** 系统存储包含`id`、`type`、`timestamp`、`date`、`details`字段的记录，其中`details`包含`feeding_type`、`duration_minutes`、`amount_ml`、`side`字段

### Requirement: Multiple Record Types
系统必须支持多种记录类型：
- 喂奶（feeding）：记录母乳或配方奶喂养
- 大便（bowel）：记录大便类型、颜色、量
- 小便（urine）：记录小便次数和量
- 营养品（medication）：记录补充剂如维生素D
- 洗澡（bathing）：记录洗澡时间、水温
- 睡眠（sleep）：记录入睡和醒来时间
- 生长指标（growth）：记录体温、体重、身长

#### Scenario: Create feeding record
- **WHEN** 创建喂奶记录，feed_type为"breast"或"formula"
- **THEN** 记录包含`details.feeding_type`、`duration_minutes`、`amount_ml`、`side`字段

#### Scenario: Create bowel record
- **WHEN** 创建大便记录
- **THEN** 记录包含`details.type`、`color`、`amount`字段

#### Scenario: Create bathing record
- **WHEN** 创建洗澡记录
- **THEN** 记录包含`details.water_temperature`、`duration_minutes`、`notes`字段

#### Scenario: Create sleep record
- **WHEN** 创建睡眠记录
- **THEN** 记录包含`details.sleep_start`、`sleep_end`、`nap`字段

#### Scenario: Create growth record
- **WHEN** 创建生长指标记录
- **THEN** 记录包含`details.temperature`、`weight_kg`、`height_cm`字段

### Requirement: Image Attachments
系统必须支持为记录附加图片。

#### Scenario: Add images to record
- **WHEN** 创建记录时附带图片路径
- **THEN** 记录的`images`字段包含图片路径数组，图片文件存储在指定目录

### Requirement: Query by Date Range
系统必须支持按日期范围查询记录。

#### Scenario: Query records for specific date
- **WHEN** 查询2026-03-25的所有记录
- **THEN** 返回该日期的所有记录

#### Scenario: Query records by date range and type
- **WHEN** 查询2026-03-01到2026-03-31的喂奶记录
- **THEN** 返回该时间范围内所有喂奶类型记录
