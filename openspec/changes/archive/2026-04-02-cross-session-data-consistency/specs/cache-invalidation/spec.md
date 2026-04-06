## ADDED Requirements

### Requirement: 索引缓存必须基于 mtime 失效
索引缓存必须在文件修改时间（mtime）变化时失效。

#### Scenario: mtime 变化时缓存失效
- **WHEN** 索引文件的 mtime 与缓存记录不同
- **THEN** 重新从磁盘加载索引

#### Scenario: 文件删除时缓存失效
- **WHEN** 索引文件被删除
- **THEN** 重置缓存并创建新的空索引

### Requirement: 关键操作前必须强制刷新索引
在创建、查询、删除记录等关键操作前，必须强制刷新索引以确保数据一致性。

#### Scenario: 创建记录前刷新索引
- **WHEN** 调用 `record_create` 函数
- **THEN** 先调用 `refresh_index()` 确保索引最新

#### Scenario: 查询记录前刷新索引
- **WHEN** 调用 `record_query` 函数
- **THEN** 先调用 `refresh_index()` 确保索引最新

#### Scenario: 列表记录前刷新索引
- **WHEN** 调用 `record_list` 函数
- **THEN** 先调用 `refresh_index()` 确保索引最新

### Requirement: 记录数据不使用进程级缓存
记录文件数据每次从磁盘读取，不使用全局缓存。

#### Scenario: 读取记录文件总是获取最新数据
- **WHEN** 调用 `load_records_from_file`
- **THEN** 直接从磁盘读取而非返回缓存

### Requirement: 写入后必须更新索引
每次写入操作完成后，必须更新索引文件以反映最新状态。

#### Scenario: 创建记录后更新索引
- **WHEN** 新记录写入完成
- **THEN** 调用 `update_index_for_record` 更新索引

#### Scenario: 删除记录后更新索引
- **WHEN** 记录被删除
- **THEN** 重建索引或更新索引条目

#### Scenario: 更新记录后重建索引
- **WHEN** 记录被修改
- **THEN** 重建该日文件的索引条目
