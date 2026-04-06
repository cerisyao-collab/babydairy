## ADDED Requirements

### Requirement: File Storage Structure
系统必须按月归档记录，存储在指定目录结构中。

#### Scenario: Directory structure creation
- **WHEN** 系统初始化
- **THEN** 创建`records/`目录和`records/images/`子目录

### Requirement: Monthly Archive Naming
记录文件必须按`YYYY-MM.json`格式命名。

#### Scenario: File naming for March 2026
- **WHEN** 创建2026年3月的记录
- **THEN** 数据保存到`records/2026-03.json`文件

### Requirement: JSON Data Format
记录必须以JSON格式存储，包含完整元数据。

#### Scenario: Write record to file
- **WHEN** 创建新记录
- **THEN** 记录以JSON格式追加到对应月份文件，包含id、type、timestamp、date、details、images字段

### Requirement: Image Storage
图片必须存储在`records/images/`目录，文件名包含record_id。

#### Scenario: Save image attachment
- **WHEN** 记录附带图片
- **THEN** 图片保存到`records/images/{record_id}-{original_name}`路径，记录中存储相对路径

### Requirement: Data Persistence
系统必须确保数据写入磁盘。

#### Scenario: Record persists after restart
- **WHEN** 创建记录后系统重启
- **THEN** 重启后仍可查询到该记录

### Requirement: Read-Only Query Access
查询时必须只读访问文件，不修改数据。

#### Scenario: Query without modification
- **WHEN** 执行查询操作
- **THEN** 不修改任何记录文件的内容或时间戳
