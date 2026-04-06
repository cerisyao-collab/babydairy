## 1. 项目依赖配置

- [x] 1.1 添加 dashscope 和 tenacity 到 requirements.txt
- [x] 1.2 更新 .env.example 添加 DASHSCOPE_API_KEY 和 QWEN_MODEL
- [x] 1.3 更新 src/config.py 添加 Qwen 相关配置项

## 2. 喂养标准数据

- [x] 2.1 创建 src/data/ 目录
- [x] 2.2 创建 feeding_standards.json 标准数据文件
- [x] 2.3 创建 src/services/standards_service.py 标准数据加载服务
- [x] 2.4 实现按日龄/月龄查询标准的函数
- [x] 2.5 实现缺失日龄的插值计算

## 3. 数据模型扩展

- [x] 3.1 更新 BabyConfig 模型添加 gender 字段
- [x] 3.2 更新 BabyConfig 模型添加 birth_weight 字段
- [x] 3.3 更新 BabyConfig 模型添加 feeding_type 字段
- [x] 3.4 创建数据库迁移脚本添加新字段
- [x] 3.5 更新 Pydantic 模型支持新字段

## 4. AI 分析服务

- [x] 4.1 创建 src/services/ai_analyzer.py
- [x] 4.2 实现 FeedingAnalyzer 类
- [x] 4.3 实现奶量分析函数 analyze_milk_volume
- [x] 4.4 实现频率分析函数 analyze_feeding_frequency
- [x] 4.5 实现间隔分析函数 analyze_intervals
- [x] 4.6 实现问题识别函数 identify_issues
- [x] 4.7 实现建议生成函数 generate_recommendations
- [x] 4.8 实现下次喂养时间计算 calculate_next_feeding
- [x] 4.9 实现 AnalysisResult 数据类

## 5. 通义千问集成

- [x] 5.1 创建 src/services/llm_service.py
- [x] 5.2 实现 LLMService 类初始化
- [x] 5.3 实现通义千问 API 调用封装
- [x] 5.4 设计 System Prompt 模板（喂养分析场景）
- [x] 5.5 实现 User Prompt 构建函数
- [x] 5.6 实现响应解析和验证
- [x] 5.7 实现错误处理和重试机制
- [x] 5.8 实现响应缓存（相同数据1小时内）

## 6. API 端点

- [x] 6.1 创建 src/api/ai.py
- [x] 6.2 实现 POST /api/ai/analyze 端点
- [x] 6.3 实现 POST /api/ai/chat 端点
- [x] 6.4 更新 PUT /api/config/baby 支持新字段
- [x] 6.5 添加请求/响应 Pydantic 模型
- [x] 6.6 在 main.py 注册 ai 路由

## 7. 每日报告增强

- [x] 7.1 更新 SummaryService 集成 AI 分析
- [x] 7.2 实现 AI 生成个性化总结文本
- [x] 7.3 更新每日报告 API 返回 AI 总结

## 8. 测试

- [x] 8.1 创建 tests/test_ai_analyzer.py 单元测试
- [x] 8.2 创建 tests/test_llm_service.py 单元测试
- [x] 8.3 创建 tests/test_standards_service.py 单元测试
- [x] 8.4 创建 AI 端点集成测试

## 9. 文档更新

- [x] 9.1 更新 README 添加 AI 功能说明
- [x] 9.2 更新 API 文档添加新端点说明
- [x] 9.3 添加喂养标准数据来源说明