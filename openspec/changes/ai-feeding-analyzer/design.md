## Context

当前 Baby Diary API 已具备喂养记录、数据统计、基础标准对比功能。用户反馈需要更智能的分析和建议，而非仅展示数据。本设计引入 AI 分析能力，采用"规则引擎 + LLM"混合架构，既保证分析准确性，又提供人性化的表达。

**约束条件**：
- LLM 使用阿里云通义千问，与现有阿里云基础设施保持一致
- 分析依据为各省妇幼保健院权威指南
- V1 阶段免费，专注用户获客
- 不做医疗诊断，仅提供建议参考

## Goals / Non-Goals

**Goals:**
- 实现喂养数据智能分析（奶量、频率、间隔）
- 提供个性化的可执行建议
- 集成通义千问生成自然语言输出
- 在首页展示下次建议喂养时间

**Non-Goals:**
- 微信订阅消息推送（简化为页面展示）
- 付费订阅功能（V1 免费）
- 多宝宝支持（V2）
- 复杂的趋势预测模型（V3）

## Decisions

### 1. AI 架构：规则引擎 + LLM 混合

**选择**: 规则引擎做数据分析 + 通义千问生成自然语言

**理由**:
- 规则引擎保证分析准确性和可解释性
- LLM 提供人性化表达，提升用户体验
- 成本可控：规则引擎零成本，LLM 仅在生成文案时调用
- 风险可控：规则引擎输出可验证，LLM 不参与决策

**备选方案**:
- 纯规则系统：准确性高但输出生硬
- 纯 LLM Agent：灵活但不可控，有医疗风险
- 微调模型：成本高，需要大量标注数据

### 2. LLM 提供商：阿里云通义千问

**选择**: qwen-turbo 模型

**理由**:
- 与现有阿里云基础设施（FC、RDS）保持一致
- 国内访问稳定，无跨域问题
- 价格优势：¥0.002/1K tokens 输入，¥0.006/1K tokens 输出
- 中文表达质量好

**备选方案**:
- Claude API：质量高但国内访问不稳定
- OpenAI：需要代理，合规风险

### 3. 喂养标准数据：结构化 JSON 文件

**选择**: 本地 JSON 文件存储标准数据

**理由**:
- 标准数据变化频率低
- 无需数据库查询，响应快
- 便于版本管理和更新

**数据来源**:
- 《中国居民膳食指南2022》婴幼儿喂养部分
- WHO 婴儿喂养标准
- 各省妇幼保健院新生儿喂养建议

### 4. 分析输出结构

```python
class AnalysisResult:
    # 状态判断
    status: str  # "normal" | "low" | "high"
    confidence: float  # 0.0 - 1.0

    # 指标数据
    metrics: Dict[str, MetricAnalysis]
    # {
    #   "milk_volume": {"value": 520, "min": 700, "max": 1000, "status": "low"},
    #   "feeding_times": {"value": 6, "min": 6, "max": 8, "status": "normal"},
    #   "interval": {"value": 4.0, "min": 3, "max": 4, "status": "normal"}
    # }

    # 识别的问题
    issues: List[Issue]
    # [{"type": "low_milk_volume", "severity": "medium", "description": "..."}]

    # LLM 生成的建议
    ai_summary: str
    recommendations: List[str]

    # 下次建议喂养时间
    next_feeding_suggestion: Optional[datetime]
```

### 5. API 设计

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/ai/analyze` | POST | 分析喂养数据，返回 AI 分析结果 |
| `/api/ai/chat` | POST | AI 问答，基于用户数据回答问题 |
| `/api/config/baby` | PUT | 更新宝宝信息（新增性别、体重、喂养方式） |

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| LLM 输出不可控 | 使用严格的 System Prompt 约束；添加输出格式验证 |
| 医疗风险 | 免责声明；使用"建议"语气；异常情况引导就医 |
| API 调用失败 | 重试机制（tenacity）；降级为规则输出 |
| 标准数据不准确 | 引用权威来源；支持版本更新 |
| 冷启动延迟 | 分析结果缓存；预热常用查询 |