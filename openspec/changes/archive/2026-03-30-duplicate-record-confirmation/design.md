## Context

当前 `record_create` 函数在创建记录时不检查是否存在重复，用户可能因误操作在短时间内创建多条相似记录。例如：
- 1 分钟内创建 2 条喂奶记录
- 同一时间段重复记录小便

这需要一种机制在写入前检测并请求确认。

## Goals / Non-Goals

**Goals:**
- 检测短时间内（默认 5 分钟）的相似记录（同类型）
- 检测到相似记录时暂停创建并请求用户确认
- 用户确认后继续创建，取消则放弃
- 配置灵活，时间窗口可调

**Non-Goals:**
- 不检测完全相同的记录（完全重复由去重逻辑处理）
- 不跨类型检测（如喂奶和小便不互判为重复）
- 不修改历史数据

## Decisions

### 1. 重复检测策略

**决策**: 基于时间窗口和记录类型判断相似性

**理由**:
- 简单直接，易于理解和预测
- 同一类型在短时间内多次出现可能是误操作
- 不需要复杂的相似度计算

**实现**:
```python
def check_duplicate_records(record_type: str, timestamp: datetime, window_minutes: int = 5) -> List[Dict]:
    """检查时间窗口内是否存在相似记录"""
    # 加载当日已有记录
    records = load_records_from_file(get_record_file_path(timestamp))

    # 过滤同类型且在时间窗口内的记录
    similar = []
    for r in records:
        r_time = datetime.fromisoformat(r["timestamp"])
        if r["type"] == record_type and abs((timestamp - r_time).total_seconds()) <= window_minutes * 60:
            similar.append(r)
    return similar
```

### 2. 确认流程设计

**决策**: 使用异常机制中断创建流程，由调用方处理确认

**理由**:
- OpenClaw 技能通过函数返回值与用户交互
- 抛出特殊异常或返回确认请求可让上层决定如何交互
- 保持 `record_create` 函数职责单一

**实现**:
```python
class DuplicateRecordError(Exception):
    def __init__(self, similar_records: List[Dict]):
        self.similar_records = similar_records

def record_create(...):
    similar = check_duplicate_records(...)
    if similar:
        raise DuplicateRecordError(similar)
    # 继续创建...
```

### 3. 时间窗口配置

**决策**: 默认 5 分钟，通过函数参数或配置文件可调

**理由**:
- 5 分钟适合大多数婴儿记录场景
- 不同记录类型可能需要不同窗口（如喂奶 vs 洗澡）
- 允许用户自定义

### 4. 跳过确认的场景

**决策**: 以下场景跳过确认：
- 明确指定 `skip_confirmation=True`
- 系统自动补录场景

**理由**:
- 保留灵活性
- 某些场景用户明确知道要创建多条记录

## Risks / Trade-offs

**[误判重复] →** 正常多次记录被拦截
- *缓解*: 用户可确认继续，或调整时间窗口
- *缓解*: 提供 `skip_confirmation` 参数跳过

**[交互复杂性] →** 创建流程变长
- *缓解*: 仅检测到相似时触发，正常创建无影响
- *缓解*: 确认提示信息清晰展示已有记录

**[性能影响] →** 每次创建需读取文件检查
- *缓解*: 仅读取单个日文件，开销小
- *缓解*: 可与索引刷新合并

## Migration Plan

1. 添加 `DuplicateRecordError` 异常类
2. 实现 `check_duplicate_records` 函数
3. 修改 `record_create` 调用检测逻辑
4. 更新 OpenClaw 工具定义处理确认
5. 测试验证

**回滚**: 恢复原始 `record_create` 逻辑

## Open Questions

- 是否需要按记录类型定义不同时间窗口？
- 确认时需要展示哪些字段？
