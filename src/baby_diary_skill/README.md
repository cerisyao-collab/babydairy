# Baby Diary Skill

新生儿日常记录技能，支持创建、查询、更新和删除宝宝记录。

## 功能

- **record_create**: 创建新记录（喂奶、大小便、营养品、洗澡、睡眠、生长指标）
- **record_query**: 查询记录（支持日期范围、类型过滤）
- **record_list**: 列出某日所有记录
- **record_get**: 按 ID 获取单条记录
- **record_update**: 更新现有记录
- **record_delete**: 删除记录（同步清理图片）
- **image_view**: 查看记录中的单张图片
- **list_images**: 列出记录中的所有图片（带缩略图）
- **image_gallery**: 以画廊形式展示多张图片

## 安装和使用方式

### 方式一：作为 Python 模块直接使用（推荐）

技能包已经可以正常工作，无需 OpenClaw：

```bash
cd /Users/hanyuxiao/project/babyjour/src/baby_diary_skill

# 测试技能包
python3 -c "from __init__ import record_create; r = record_create('feeding', {'feeding_type': 'formula', 'amount_ml': 120}); print('Created:', r['id'])"
```

### 方式二：通过 Claude Code Skill 调用（已配置）

在 Claude Code 中直接使用自然语言：

```
记录宝宝喝了 150ml 奶粉
查询今天的记录
更新刚才那条记录的奶量为 180ml
删除刚才那条记录
```

技能文件位于：`.claude/skills/baby-diary/SKILL.md`

### 方式三：通过 OpenClaw 调用（需要 ClawHub 发布）

**注意**: OpenClaw 的技能列表是固定的（54 个），需要通过 ClawHub 发布才能使用。

1. 安装 clawhub:
```bash
npm install -g clawhub
```

## OpenClaw Agent 配置

宝宝日记技能已配置 OpenClaw 小龙虾 agent 文件：

- **文件位置**: `baby_diary.agent.yaml`
- **功能**: 定义技能的 9 个端点及其参数 schema
- **触发条件**: 支持自然语言触发（如"记录宝宝..."、"查询记录..."等）

Agent 文件包含：
- 技能元数据（名称、描述、版本、作者）
- 8 种记录类型定义
- 9 个技能端点完整配置
- 自然语言触发模式
- 使用示例

2. 发布技能到 ClawHub:
```bash
clawhub publish /path/to/baby_diary_skill
```

3. 安装技能:
```bash
openclaw skills install baby_diary
```

## 使用方法（Python API）

```python
import sys
sys.path.insert(0, '/path/to/baby_diary_skill')
from __init__ import (
    record_create, record_query, record_list,
    record_get, record_update, record_delete,
    format_records_for_display
)

# 创建记录
record = record_create(
    record_type="feeding",
    details={"feeding_type": "formula", "amount_ml": 120, "duration_minutes": 15}
)

# 获取记录
record = record_get(record["id"])

# 更新记录
record_update(record["id"], details={"amount_ml": 150})

# 删除记录
record_delete(record["id"])

# 查询记录
records = record_query(start_date="2026-03-01", end_date="2026-03-31")
print(format_records_for_display(records))
```

## 技能结构

```
baby_diary_skill/
├── SKILL.md                # OpenClaw 技能文档
├── skill.toml              # 技能元数据
├── __init__.py             # 技能入口（导出 SKILL_METADATA 和 SKILL_ENDPOINTS）
├── install.py              # 安装脚本
├── openclaw.plugin.json    # OpenClaw 插件配置
├── README.md               # 本文档
└── baby-diary/             # 核心逻辑
    ├── __init__.py         # 核心函数实现
    ├── README.md           # 详细文档
    └── records/            # 数据存储目录
        ├── *.json          # 月度记录文件
        └── images/         # 图片存储目录
```

## 记录类型

| 类型 | 字段 |
|------|------|
| feeding | feeding_type, duration_minutes, amount_ml, side |
| bowel | type, color, amount |
| urine | count, amount |
| medication | name, dosage, notes |
| bathing | water_temperature, duration_minutes, notes |
| sleep | sleep_start, sleep_end, nap |
| growth | temperature, weight_kg, height_cm |

## 依赖

- Python >= 3.7
- Pillow >= 9.0.0 (图片处理)
- pillow-heif >= 0.12.0 (HEIC 格式支持，可选)

## License

MIT
