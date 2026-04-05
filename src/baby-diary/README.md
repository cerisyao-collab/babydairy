# 新生儿日常记录助手

## 简介

这是一个为 0-1 岁新生儿设计的日常记录工具，支持通过 OpenClaw 调用技能进行记录。

## 功能

- **喂奶记录**: 母乳/配方奶、时长、奶量、左右侧
- **大小便记录**: 类型、颜色、量
- **营养品记录**: 补充剂、剂量
- **洗澡记录**: 水温、时长
- **睡眠记录**: 入睡/醒来时间
- **生长指标**: 体温、体重、身长
- **病情记录**: 症状、病因、诊断、治疗方案
- **图片支持**: 为记录附加图片、生成缩略图
- **每日总结**: 自动生成每日近况总结，对比生长标准值
- **宝宝配置**: 设置宝宝出生日期、昵称

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

### 7. 查看图片

```python
from baby_diary import image_view, list_images, image_gallery

# 查看单张图片
result = image_view(record_id, image_index=0)

# 列出所有图片
result = list_images(record_id)

# 画廊模式查看所有图片
result = image_gallery(record_id)
```

### 8. 宝宝配置

```python
from baby_diary import get_baby_config, set_baby_config

# 设置宝宝出生日期
set_baby_config(birth_date="2026-03-01", baby_name="小明")

# 获取配置
config = get_baby_config()
print(f"宝宝昵称：{config.get('baby_name')}")
print(f"出生日期：{config.get('birth_date')}")
```

### 9. 每日总结

```python
from baby_diary import daily_summary

# 生成今日总结（自动对比生长标准值）
summary = daily_summary(date="2026-03-25")
print(summary)

# 或指定出生日期
summary = daily_summary(date="2026-03-25", birth_date="2026-03-01")
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

### daily_summary - 每日总结

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

### get_baby_config - 获取宝宝配置

```json
{
  "skill": "baby_diary",
  "action": "get_baby_config"
}
```

### set_baby_config - 设置宝宝配置

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

### image_view - 查看图片

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

## 数据存储

记录存储在 JSON 文件中，按日归档：

```
src/baby-diary/
├── records/
│   ├── 2026-03-25.json    # 每日记录文件
│   ├── 2026-03-26.json
│   └── ...
├── records/images/
│   └── {record_id}-{original_name}
└── baby_config.json       # 宝宝配置
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
- `symptom`: 症状描述
- `cause`: 可能病因
- `diagnosis`: 医生诊断
- `treatment`: 治疗方案
- `severity`: 严重程度 (轻/中/重)
- `temperature`: 体温
- `hospital_visit`: 是否就医
- `notes`: 其他备注

## 特性

- **文件锁**: 使用 fcntl 实现读写锁，支持并发安全
- **缓存失效**: 跨 Session 自动刷新索引，确保数据一致性
- **重复检测**: 创建记录时自动检测时间窗口内的相似记录
- **生长标准**: 内置婴儿生长发育标准值（崔玉涛建议、浙江省妇保标准）
- **图片缩略图**: 自动生成缩略图用于快速预览

## 安全

### 图片访问限制

- **记录关联**: 只能查看与记录关联的图片，通过 record_id 验证
- **路径遍历防护**: 阻止 `../`、`..\\`、`/` 等路径遍历攻击
- **隐藏文件阻止**: 不允许访问以 `.` 开头的隐藏文件
- **目录限制**: 图片路径必须在 images 目录内
- **安全日志**: 所有访问拒绝尝试会被记录到 security.log

## 依赖

- Python >= 3.7
- Pillow (可选，用于图片处理和缩略图生成)

## License

MIT
