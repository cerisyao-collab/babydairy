## 1. 核心功能实现

- [x] 1.1 实现 `record_get(record_id)` 函数：按 ID 获取单条记录
- [x] 1.2 实现 `record_update(record_id, details, timestamp, images)` 函数：更新记录
- [x] 1.3 实现 `record_delete(record_id)` 函数：删除记录
- [x] 1.4 实现图片清理函数：删除记录时同步删除关联图片

## 2. Skill 端点扩展

- [x] 2.1 在 `baby_diary_skill.py` 中添加 `record_get` 端点定义
- [x] 2.2 在 `baby_diary_skill.py` 中添加 `record_update` 端点定义
- [x] 2.3 在 `baby_diary_skill.py` 中添加 `record_delete` 端点定义
- [x] 2.4 更新 SKILL_ENDPOINTS 元数据

## 3. 错误处理

- [x] 3.1 实现记录不存在错误处理
- [x] 3.2 实现无效 ID 格式错误处理
- [x] 3.3 实现文件读写错误处理

## 4. 文档更新

- [x] 4.1 更新 `src/baby-diary/README.md` 添加 record_get 使用示例
- [x] 4.2 更新 `src/baby-diary/README.md` 添加 record_update 使用示例
- [x] 4.3 更新 `src/baby-diary/README.md` 添加 record_delete 使用示例
- [x] 4.4 更新 OpenClaw Skill 调用示例文档

## 5. 测试

- [x] 5.1 测试 record_get 获取单条记录
- [x] 5.2 测试 record_update 更新记录详情
- [x] 5.3 测试 record_update 更新时间戳
- [x] 5.4 测试 record_delete 删除记录
- [x] 5.5 测试删除带图片的记录（验证图片清理）
- [x] 5.6 测试记录不存在时的错误处理
- [x] 5.7 测试 OpenClaw Skill 调用新增端点
