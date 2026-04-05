"""
Baby Diary Skill for OpenClaw

OpenClaw 技能定义文件
提供新生儿日常记录功能
"""

import sys
from pathlib import Path

# Add baby-diary directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "baby-diary"))

from __init__ import (
    record_create,
    record_query,
    record_list,
    record_get,
    record_update,
    record_delete,
    format_records_for_display,
    init_storage,
    RECORD_TYPES,
    RECORD_TYPE_DETAILS,
)

# 技能元数据
SKILL_METADATA = {
    "name": "baby_diary",
    "description": "新生儿日常记录技能，支持喂奶、大小便、营养品、洗澡等记录，以及记录的查询、更新和删除",
    "version": "1.1.0",
    "author": "babyjour",
}

# 技能端点定义
SKILL_ENDPOINTS = {
    "record_create": {
        "description": "创建新记录",
        "parameters": {
            "record_type": {
                "type": "string",
                "required": True,
                "description": "记录类型: feeding, bowel, urine, medication, bathing, sleep, growth",
                "options": RECORD_TYPES,
            },
            "details": {
                "type": "object",
                "required": True,
                "description": "类型特定的详情，参见 RECORD_TYPE_DETAILS",
            },
            "timestamp": {
                "type": "string",
                "required": False,
                "description": "ISO时间戳，默认当前时间",
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "required": False,
                "description": "图片路径列表",
            },
        },
        "returns": "创建的记录对象",
    },
    "record_query": {
        "description": "查询记录",
        "parameters": {
            "start_date": {
                "type": "string",
                "required": False,
                "description": "开始日期 (YYYY-MM-DD)",
            },
            "end_date": {
                "type": "string",
                "required": False,
                "description": "结束日期 (YYYY-MM-DD)",
            },
            "record_type": {
                "type": "string",
                "required": False,
                "description": "记录类型过滤",
                "options": RECORD_TYPES,
            },
        },
        "returns": "记录列表",
    },
    "record_list": {
        "description": "列出某日的所有记录",
        "parameters": {
            "date": {
                "type": "string",
                "required": False,
                "description": "日期 (YYYY-MM-DD)，默认今天",
            },
        },
        "returns": "该日的记录列表",
    },
    "record_get": {
        "description": "按 ID 获取单条记录",
        "parameters": {
            "record_id": {
                "type": "string",
                "required": True,
                "description": "记录 ID",
            },
        },
        "returns": "单条记录对象，未找到返回 null",
    },
    "record_update": {
        "description": "更新现有记录",
        "parameters": {
            "record_id": {
                "type": "string",
                "required": True,
                "description": "要更新的记录 ID",
            },
            "details": {
                "type": "object",
                "required": False,
                "description": "更新的详情字段",
            },
            "timestamp": {
                "type": "string",
                "required": False,
                "description": "更新时间戳 (ISO 格式)",
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "required": False,
                "description": "更新的图片路径列表",
            },
        },
        "returns": "更新后的记录对象",
    },
    "record_delete": {
        "description": "删除记录",
        "parameters": {
            "record_id": {
                "type": "string",
                "required": True,
                "description": "要删除的记录 ID",
            },
        },
        "returns": "删除成功返回 true",
    },
}
