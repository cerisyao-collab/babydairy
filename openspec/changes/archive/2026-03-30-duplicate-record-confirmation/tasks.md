## 1. 准备工作

- [x] 1.1 备份当前 `__init__.py` 文件
- [x] 1.2 读取现有 `record_create` 函数理解当前逻辑

## 2. 实现重复检测功能

- [x] 2.1 实现 `check_duplicate_records` 函数检测时间窗口内的相似记录
- [x] 2.2 实现 `DuplicateRecordError` 异常类
- [x] 2.3 添加时间窗口默认值常量 `DEFAULT_DUPLICATE_WINDOW_MINUTES = 5`

## 3. 修改记录创建流程

- [x] 3.1 在 `record_create` 函数中调用重复检测
- [x] 3.2 检测到相似记录时抛出 `DuplicateRecordError` 或返回确认请求
- [x] 3.3 添加 `skip_confirmation` 参数支持跳过确认

## 4. 实现确认交互

- [x] 4.1 创建确认提示信息格式化函数 `format_duplicate_confirmation_message`
- [x] 4.2 在 OpenClaw 工具层处理确认请求并等待用户响应

## 5. 测试验证

- [x] 5.1 测试检测到重复记录的场景
- [x] 5.2 测试无重复记录正常创建的场景
- [x] 5.3 测试用户确认继续创建的场景 (通过 skip_confirmation 验证)
- [x] 5.4 测试用户取消创建的场景 (通过捕获异常验证)
- [x] 5.5 测试 `skip_confirmation` 参数的场景

## 6. 部署与同步

- [x] 6.1 同步代码到 OpenClaw 技能目录 `~/.openclaw/skills/baby_diary_skill/`
- [x] 6.2 清理 `__pycache__` 缓存
- [x] 6.3 重启 OpenClaw Gateway
- [x] 6.4 执行最终确认流程测试
