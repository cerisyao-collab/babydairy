# 新生儿日常记录助手

## 简介

这是一个为0-1岁新生儿设计的日常记录工具，支持通过 OpenClaw 调用技能进行记录。

## 功能

- **喂奶记录**: 母乳/配方奶、时长、奶量、左右侧
- **大小便记录**: 类型、颜色、量
- **营养品记录**: 补充剂、剂量
- **洗澡记录**: 水温、时长
- **睡眠记录**: 入睡/醒来时间
- **生长指标**: 体温、体重、身长
- **病情记录**: 症状、病因、诊断、治疗方案、严重程度
- **图片支持**: 为记录附加图片

## 安装

```bash
# 代码位于 src/baby-diary/
cd babyjour/src/baby-diary
```

## 使用方法

### 1. 初始化存储

```python
from baby_diary import init_storage

init_storage()  # 创建 records/ 和 records/images/ 目录
```

### 2. 创建记录

```python
from baby_diary import record_create

# 喂奶记录
record_create(
    record_type="feeding",
    details={
        "feeding_type": "breast",
        "duration_minutes": 20,
        "amount_ml": 150,
        "side": "left",
    },
    # timestamp 可选，默认当前时间
    # images 可选，图片路径列表
)

# 大便记录
record_create(
    record_type="bowel",
    details={
        "type": "正常",
        "color": "黄色",
        "amount": "中等",
    },
)

# 睡眠记录
record_create(
    record_type="sleep",
    details={
        "sleep_start": "2026-03-25T22:00:00",
        "sleep_end": "2026-03-26T06:00:00",
        "nap": False,
    },
)

# 病情记录
record_create(
    record_type="illness",
    details={
        "symptom": "发烧、咳嗽",
        "cause": "可能着凉",
        "severity": "中",
        "temperature": "38.5°C",
        "hospital_visit": False,
        "notes": "多喝水，多休息",
    },
)
```

### 3. 查询记录

```python
from baby_diary import record_query, record_list

# 查询某天的所有记录
today_records = record_list("2026-03-25")

# 查询指定日期范围
records = record_query(
    start_date="2026-03-01",
    end_date="2026-03-31",
    record_type="feeding",  # 可选，类型过滤
)

print(format_records_for_display(records))  # 格式化输出
```

### 4. 获取记录详情

```python
from baby_diary import record_get

# 按 ID 获取单条记录
record = record_get("7e0c68f9-7fc9-45c0-b770-db1a8771c587")
if record:
    print(f"记录类型：{record['type']}")
    print(f"详情：{record['details']}")
else:
    print("记录未找到")
```

### 5. 更新记录

```python
from baby_diary import record_update

# 更新记录详情
record_update(
    record_id="7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    details={"feeding_type": "formula", "amount_ml": 180, "duration_minutes": 20}
)

# 更新时间戳
record_update(
    record_id="7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    timestamp="2026-03-25T10:30:00"
)

# 更新图片
record_update(
    record_id="7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    images=["images/new_photo.jpg"]
)
```

### 6. 删除记录

```python
from baby_diary import record_delete

# 删除记录（同时删除关联的图片）
success = record_delete("7e0c68f9-7fc9-45c0-b770-db1a8771c587")
if success:
    print("记录已删除")
```

## OpenClaw Skill 用法

### record_create - 创建记录

```json
{
  "skill": "baby_diary",
  "action": "record_create",
  "params": {
    "record_type": "feeding",
    "details": {
      "feeding_type": "formula",
      "duration_minutes": 15,
      "amount_ml": 120
    }
  }
}
```

### record_query - 查询记录

```json
{
  "skill": "baby_diary",
  "action": "record_query",
  "params": {
    "start_date": "2026-03-01",
    "end_date": "2026-03-31",
    "record_type": "bowel"
  }
}
```

### record_list - 列出某日记录

```json
{
  "skill": "baby_diary",
  "action": "record_list",
  "params": {
    "date": "2026-03-25"
  }
}
```

### record_get - 获取记录详情

```json
{
  "skill": "baby_diary",
  "action": "record_get",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### record_update - 更新记录

```json
{
  "skill": "baby_diary",
  "action": "record_update",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587",
    "details": {
      "feeding_type": "formula",
      "amount_ml": 180
    }
  }
}
```

### record_delete - 删除记录

```json
{
  "skill": "baby_diary",
  "action": "record_delete",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### image_view - 查看记录中的图片

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

### list_images - 列出记录中的所有图片

```json
{
  "skill": "baby_diary",
  "action": "list_images",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

### image_gallery - 以画廊形式展示图片

```json
{
  "skill": "baby_diary",
  "action": "image_gallery",
  "params": {
    "record_id": "7e0c68f9-7fc9-45c0-b770-db1a8771c587"
  }
}
```

## 数据存储

记录存储在 JSON 文件中，按月归档：

```
src/baby-diary/
├── records/
│   ├── 2026-03.json
│   ├── 2026-04.json
│   └── ...
└── records/images/
    └── {record_id}-{original_name}
```

## 记录类型详情

### feeding (喂奶)
- `feeding_type`: "breast" (母乳) 或 "formula" (配方奶)
- `duration_minutes`: 时长（分钟）
- `amount_ml`: 奶量（毫升）
- `side`: "left" (左侧) 或 "right" (右侧)

### bowel (大便)
- `type`: 大便类型
- `color`: 颜色
- `amount`: 量

### urine (小便)
- `count`: 次数
- `amount`: 量

### medication (营养品)
- `name`: 药品/补充剂名称
- `dosage`: 剂量
- `notes`: 备注

### bathing (洗澡)
- `water_temperature`: 水温
- `duration_minutes`: 时长（分钟）
- `notes`: 备注

### sleep (睡眠)
- `sleep_start`: 入睡时间
- `sleep_end`: 醒来时间
- `nap`: 是否小睡

### growth (生长指标)
- `temperature`: 体温
- `weight_kg`: 体重（公斤）
- `height_cm`: 身长（厘米）

### illness (病情)
- `symptom`: 症状描述（如：发烧、咳嗽、流鼻涕）
- `cause`: 可能病因（可选）
- `diagnosis`: 医生诊断（可选）
- `treatment`: 治疗方案（可选）
- `severity`: 严重程度 (轻/中/重)
- `temperature`: 体温（可选）
- `hospital_visit`: 是否就医（布尔值）
- `notes`: 其他备注（可选）
