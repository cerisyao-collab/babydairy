---
name: baby-diary
description: 新生儿日常记录技能 - 创建和查询喂奶、大小便、营养品、洗澡、睡眠、生长指标等记录
license: MIT
compatibility: Requires Python 3.7+ and baby-diary module in src/baby-diary/
metadata:
  author: babyjour
  version: "1.0.0"
  generatedBy: "update-skill-docs"
---

# Baby Diary Skill - 新生儿日常记录技能

这是一个为 0-1 岁新生儿设计的日常记录工具，支持通过自然语言调用技能进行记录。

## 可用的技能端点

### 1. record_create - 创建记录

创建一条新的新生儿日常记录。

**参数：**
- `record_type` (必需): 记录类型
  - `feeding` - 喂奶
  - `bowel` - 大便
  - `urine` - 小便
  - `medication` - 营养品
  - `bathing` - 洗澡
  - `sleep` - 睡眠
  - `growth` - 生长指标
- `details` (必需): 类型特定的详情
- `timestamp` (可选): ISO 时间戳，默认当前时间
- `images` (可选): 图片路径列表

**示例：**
```
创建一个喂奶记录，母乳，20 分钟，左侧
```

```json
{
  "skill": "baby_diary",
  "action": "record_create",
  "params": {
    "record_type": "feeding",
    "details": {
      "feeding_type": "breast",
      "duration_minutes": 20,
      "amount_ml": 150,
      "side": "left"
    }
  }
}
```

**各类型的 details 字段：**

| 类型 | 字段 |
|------|------|
| feeding | feeding_type (breast/formula), duration_minutes, amount_ml, side (left/right) |
| bowel | type, color, amount |
| urine | count, amount |
| medication | name, dosage, notes |
| bathing | water_temperature, duration_minutes, notes |
| sleep | sleep_start, sleep_end, nap |
| growth | temperature, weight_kg, height_cm |
| illness | symptom (症状), cause (病因), diagnosis (诊断), treatment (治疗), severity (严重程度), temperature (体温), hospital_visit (是否就医), notes (备注) |

**记录类型详细说明：**

| 类型 | 名称 | 字段说明 |
|------|------|----------|
| feeding | 喂奶 | feeding_type: 喂奶类型 (breast=母乳，formula=配方奶), duration_minutes: 时长（分钟）, amount_ml: 奶量（毫升）, side: 喂奶侧边 (left=左侧，right=右侧) |
| bowel | 大便 | type: 大便类型，color: 颜色，amount: 量 |
| urine | 小便 | count: 次数，amount: 量 |
| medication | 营养品 | name: 药品/补充剂名称，dosage: 剂量，notes: 备注 |
| bathing | 洗澡 | water_temperature: 水温，duration_minutes: 时长（分钟）, notes: 备注 |
| sleep | 睡眠 | sleep_start: 入睡时间，sleep_end: 醒来时间，nap: 是否小睡 |
| growth | 生长指标 | temperature: 体温，weight_kg: 体重（公斤）, height_cm: 身长（厘米） |
| illness | 病情 | symptom: 症状描述，cause: 可能病因，diagnosis: 医生诊断，treatment: 治疗方案，severity: 严重程度 (轻/中/重), temperature: 体温，hospital_visit: 是否就医，notes: 其他备注 |

### 2. record_query - 查询记录

按条件查询记录。

**参数：**
- `start_date` (可选): 开始日期 (YYYY-MM-DD)
- `end_date` (可选): 结束日期 (YYYY-MM-DD)
- `record_type` (可选): 记录类型过滤

**示例：**
```
查询 2026-03-25 的所有喂奶记录
```

```json
{
  "skill": "baby_diary",
  "action": "record_query",
  "params": {
    "start_date": "2026-03-25",
    "end_date": "2026-03-25",
    "record_type": "feeding"
  }
}
```

### 3. record_list - 列出某日记录

列出指定日期的所有记录。

**参数：**
- `date` (可选): 日期 (YYYY-MM-DD)，默认今天

**示例：**
```
查看今天的记录
```

```json
{
  "skill": "baby_diary",
  "action": "record_list",
  "params": {
    "date": "2026-03-25"
  }
}
```

### 4. record_get - 获取记录详情

按 ID 获取单条记录的完整信息。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID（UUID 格式） |

**返回值：** 记录字典，包含 id, type, timestamp, date, details, images 字段

**示例：**

自然语言调用：
```
获取记录 7e0c68f9-7fc9-45c0-b770-db1a8771c587 的详情
查看这条记录的完整信息
```

```json
{
  "skill": "baby_diary",
  "action": "record_get",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### 5. record_update - 更新记录

更新现有记录的信息。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID |
| details | 可选 | 对象 | - | 更新的详情字段 |
| timestamp | 可选 | 字符串 | - | 更新时间戳 |
| images | 可选 | 数组 | - | 更新的图片列表 |

**注意：** 如果更新 `timestamp` 且日期发生变化，记录会自动移动到新月份的文件。

**示例：**

自然语言调用：
```
更新记录的奶量为 180ml
修改这条记录的详情
```

```json
{
  "skill": "baby_diary",
  "action": "record_update",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    "details": {
      "feeding_type": "formula",
      "amount_ml": 180,
      "duration_minutes": 20
    }
  }
}
```

### 6. record_delete - 删除记录

删除指定记录及其关联的图片。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID |

**返回值：** True 如果删除成功

**注意：** 删除记录会同时删除关联的图片文件。

**示例：**

自然语言调用：
```
删除这条记录
移除记录 7e0c68f9-7fc9-45c0-b770-db1a8771c587
```

```json
{
  "skill": "baby_diary",
  "action": "record_delete",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### 7. daily_summary - 每日近况总结

生成每日近况总结，自动汇总当天记录并与婴儿生长发育标准值对比分析。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| date | 可选 | 字符串 | 今天 | 日期 (YYYY-MM-DD) |
| birth_date | 可选 | 字符串 | 从配置读取 | 宝宝出生日期 (YYYY-MM-DD) |

**返回值：** 格式化的总结报告字符串，包含：
- 今日记录总数
- 喂养情况（次数、总奶量、与标准值对比）
- 排泄情况（小便次数、大便次数及性状、与标准值对比）
- 生长指标（体重、身长、体温、与标准值对比评估）
- 其他记录（营养品、洗澡、睡眠、病情）

**示例：**

自然语言调用：
```
生成今天的每日总结
查看 2026-03-25 的近况总结
宝宝今天发育情况如何
```

```json
{
  "skill": "baby_diary",
  "action": "daily_summary",
  "params": {
    "date": "2026-03-25",
    "birth_date": "2026-03-01"
  }
}
```

**示例输出：**
```
【2026-03-25】宝宝每日近况总结
出生天数：第 25 天

今日记录总数：8 条

🍼 喂养情况
  喂养次数：8 次
  总奶量：960 ml
  亲喂：6 次
  瓶喂：2 次
  对比标准：正常 (在标准范围内 6-12 次)
  建议：发育良好，继续保持

💩 排泄情况
  小便：10 次
  大便：3 次 (黄色，绿色，黄色)
  排尿对比：正常 (在标准范围内 6-12 次)
  大便对比：正常 (在标准范围内 1-6 次)

📏 生长指标
  [2026-03-25 10:00] 体重 4.2 kg, 身长 55.0 cm
    体重评估：正常 - 发育良好，继续保持
    身长评估：正常 - 发育良好，继续保持
```

### 8. compare_with_standards - 对比分析

对比实际数据与婴儿生长发育标准值，输出评估结果和建议。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| actual | 必需 | 数字 | - | 实际测量值 |
| standard | 必需 | 对象 | - | 标准值 {min, max, avg} |
| metric_name | 可选 | 字符串 | - | 指标名称（用于输出） |

**返回值：** 对比结果对象
```json
{
  "status": "正常",
  "advice": "发育良好，继续保持",
  "difference": "在标准范围内 (3.5-5.0)"
}
```

**状态说明：**
- `正常`: 实际值在标准范围内
- `偏低`/`偏少`: 实际值低于标准下限
- `偏高`/`偏多`: 实际值高于标准上限

**示例：**

```json
{
  "skill": "baby_diary",
  "action": "compare_with_standards",
  "params": {
    "actual": 4.2,
    "standard": {"min": 3.5, "max": 5.0, "avg": 4.25},
    "metric_name": "体重"
  }
}
```

### 9. get_baby_config - 获取宝宝配置

获取宝宝的配置信息，包括出生日期、昵称等。

**参数：** 无

**返回值：** 配置字典
```json
{
  "birth_date": "2026-03-01",
  "baby_name": "宝宝"
}
```

**示例：**

自然语言调用：
```
查看宝宝的出生日期
宝宝叫什么名字
```

```json
{
  "skill": "baby_diary",
  "action": "get_baby_config"
}
```

### 10. set_baby_config - 设置宝宝配置

设置宝宝的配置信息，包括出生日期、昵称等。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| birth_date | 可选 | 字符串 | - | 出生日期 (YYYY-MM-DD) |
| baby_name | 可选 | 字符串 | - | 宝宝昵称 |

**返回值：** True 如果保存成功

**示例：**

自然语言调用：
```
设置宝宝出生日期为 2026 年 3 月 1 日
宝宝昵称改为小明
```

```json
{
  "skill": "baby_diary",
  "action": "set_baby_config",
  "params": {
    "birth_date": "2026-03-01",
    "baby_name": "小明"
  }
}
```

### 11. image_view - 查看记录图片

查看指定记录的某张图片，支持返回图片 Base64 编码用于显示。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID |
| image_index | 可选 | 整数 | 0 | 图片索引（从 0 开始） |

**返回值：** 图片信息字典
```json
{
  "success": true,
  "image_base64": "data:image/jpeg;base64,...",
  "image_path": "images/record_id-photo.jpg",
  "thumbnail_base64": "data:image/jpeg;base64,..."
}
```

**示例：**

自然语言调用：
```
查看这条记录的图片
显示记录的第一张照片
```

```json
{
  "skill": "baby_diary",
  "action": "image_view",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    "image_index": 0
  }
}
```

### 12. list_images - 列出记录图片列表

列出指定记录的所有图片信息。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID |

**返回值：** 图片列表信息
```json
{
  "success": true,
  "record_id": "xxx",
  "images": [
    {"index": 0, "filename": "photo1.jpg", "size": "100KB"},
    {"index": 1, "filename": "photo2.jpg", "size": "150KB"}
  ],
  "count": 2
}
```

**示例：**

自然语言调用：
```
列出这条记录的所有图片
查看记录有多少张照片
```

```json
{
  "skill": "baby_diary",
  "action": "list_images",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### 13. image_gallery - 图片画廊模式

以画廊模式查看记录的所有图片，返回所有图片的 Base64 编码。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_id | 必需 | 字符串 | - | 记录 ID |

**返回值：** 画廊信息，包含所有图片
```json
{
  "success": true,
  "record_id": "xxx",
  "gallery": [
    {"index": 0, "base64": "...", "thumbnail": "..."},
    {"index": 1, "base64": "...", "thumbnail": "..."}
  ],
  "count": 2
}
```

**示例：**

自然语言调用：
```
以画廊模式查看所有图片
显示这条记录的完整相册
```

```json
{
  "skill": "baby_diary",
  "action": "image_gallery",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### 14. generate_thumbnail - 生成图片缩略图

为指定图片生成缩略图，用于快速预览。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| image_path | 必需 | 字符串 | - | 图片路径 |
| size | 可选 | 数组 | [100, 100] | 缩略图尺寸 [宽，高] |

**返回值：** 缩略图 Base64 编码

**示例：**

```json
{
  "skill": "baby_diary",
  "action": "generate_thumbnail",
  "params": {
    "image_path": "images/record_id-photo.jpg",
    "size": [100, 100]
  }
}
```

### 15. refresh_index - 刷新索引

强制刷新索引文件，确保获取最新的记录列表。在跨 Session 场景下确保数据一致性。

**参数：** 无

**返回值：** 刷新后的索引字典

**说明：** 此函数主要由系统内部调用，确保在查询前获取最新数据。

**示例：**

```json
{
  "skill": "baby_diary",
  "action": "refresh_index"
}
```

### 16. check_duplicate_records - 检查重复记录

检查指定时间窗口内是否存在相似记录，用于防止重复录入。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| record_type | 必需 | 字符串 | - | 记录类型 |
| timestamp | 必需 | 字符串 | - | 时间戳 |
| window_minutes | 可选 | 整数 | 5 | 时间窗口（分钟） |

**返回值：** 相似记录列表

**说明：** 此函数主要由 record_create 内部调用，检测到重复记录时抛出 DuplicateRecordError。

### 17. format_duplicate_confirmation_message - 格式化重复记录提示

格式化重复记录的确认提示信息。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| similar_records | 必需 | 数组 | - | 相似记录列表 |

**返回值：** 格式化的提示消息字符串

### 18. load_growth_standards - 加载生长标准数据

加载婴儿生长发育标准值数据文件。

**参数：** 无

**返回值：** 标准值字典
```json
{
  "standards": {
    "day_1": {
      "weight_kg": {"min": 2.5, "max": 4.0, "avg": 3.2},
      "height_cm": {"min": 45, "max": 55, "avg": 50}
    }
  },
  "source": "崔玉涛建议、浙江省妇保标准"
}
```

### 19. get_standard_for_day - 获取指定天数的标准值

获取指定出生天数的某项指标标准值。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| day | 必需 | 整数 | - | 出生天数（从 1 开始） |
| metric | 必需 | 字符串 | - | 指标名称 |

**返回值：** 标准值字典 {min, max, avg} 或 None

**支持的指标：**
- `weight_kg`: 体重（公斤）
- `height_cm`: 身长（厘米）
- `urine_count`: 排尿次数（次/天）
- `bowel_count`: 大便次数（次/天）
- `feeding_times`: 喂养次数（次/天）
- `milk_volume_ml`: 奶量参考（ml/天）

**示例：**

```json
{
  "skill": "baby_diary",
  "action": "get_standard_for_day",
  "params": {
    "day": 25,
    "metric": "weight_kg"
  }
}
```

### 20. get_birth_day - 计算出生天数

根据宝宝出生日期计算指定日期的出生天数。

**参数：**

| 参数 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| birth_date | 必需 | 日期 | - | 出生日期 |
| target_date | 可选 | 日期 | 今天 | 目标日期 |

**返回值：** 出生天数（出生当天为第 1 天）

**说明：** 此函数主要由 daily_summary 内部调用，用于确定使用哪天的标准值进行对比。

## 使用方法

### 通过自然语言调用

用户可以使用自然语言请求，例如：
- "记录宝宝刚才喝了 150ml 配方奶，用了 15 分钟"
- "查询昨天所有的喂奶记录"
- "今天宝宝有什么记录？"
- "记录宝宝刚才大便了，黄色，正常量"
- "宝宝今天体重和身高是多少？"
- "记录宝宝洗澡，水温 37 度，用了 10 分钟"
- "生成今天的每日总结"
- "宝宝发育情况怎么样"

### 通过 Python 代码调用

```python
import sys
sys.path.insert(0, 'src/baby-diary')
from __init__ import (
    record_create,
    record_query,
    record_list,
    format_records_for_display,
    daily_summary,
    compare_with_standards,
    load_growth_standards
)

# 创建记录
record = record_create(
    record_type="feeding",
    details={"feeding_type": "formula", "amount_ml": 120, "duration_minutes": 15}
)

# 查询记录
records = record_query(start_date="2026-03-25", end_date="2026-03-25")

# 格式化输出
print(format_records_for_display(records))

# 生成每日总结
summary = daily_summary(date="2026-03-25", birth_date="2026-03-01")
print(summary)

# 对比分析
result = compare_with_standards(
    actual=4.2,
    standard={"min": 3.5, "max": 5.0, "avg": 4.25},
    metric_name="体重"
)
print(result)
```

## 数据存储

记录存储在 JSON 文件中，**按月归档**，支持按日查询和总结：

```
src/baby-diary/
├── records/
│   ├── 2026-03.json    # 3 月所有记录
│   ├── 2026-04.json    # 4 月所有记录
│   └── ...
├── records/images/
│   └── {record_id}-{original_name}
└── growth_standards.json    # 婴儿生长发育标准值数据
```

**存储说明：**
- 记录文件：按月归档（`YYYY-MM.json`），每个文件包含该月所有记录
- 图片文件：存储在 `records/images/` 目录，文件名为 `{record_id}-{original_name}`
- 标准值数据：`growth_standards.json` 存储 0-12 个月婴儿的生长发育标准值

**查询说明：**
- `record_query`: 跨月查询，自动遍历相关月份文件
- `record_list`: 查询指定日期记录，从对应月份文件中过滤
- `daily_summary`: 生成指定日期的总结，自动计算出生天数并对比标准值

## 生长标准数据

内置婴儿生长发育标准值，基于**崔玉涛建议**和**浙江省妇保标准**综合制定。

**标准值指标：**
- 体重（kg）
- 身长（cm）
- 头围（cm）
- 排尿次数（次/天）
- 大便次数（次/天）
- 喂养次数（次/天）
- 奶量参考（ml/天）

**适用范围：** 0-12 个月婴儿（0-365 天）

**对比评估：**
- **正常**：实际值在标准范围内
- **偏低/偏少**：实际值低于标准下限
- **偏高/偏多**：实际值高于标准上限

## 注意事项

1. **首次使用**：首次使用前需要初始化存储目录
2. **图片路径**：图片路径是相对于 `records/images/` 目录的相对路径
3. **日期格式**：日期格式必须为 `YYYY-MM-DD`
4. **时间戳格式**：时间戳格式为 ISO 8601
5. **记录类型**：支持 8 种记录类型（feeding, bowel, urine, medication, bathing, sleep, growth, illness）
6. **必填字段**：每个记录类型的 `details` 字段要求不同，请参考上表
7. **出生天数计算**：出生当天为第 1 天，自动根据出生日期计算
8. **标准值数据**：存储在 `growth_standards.json` 文件中，首次使用时自动加载
