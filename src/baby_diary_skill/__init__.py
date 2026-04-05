"""
Baby Diary Skill for OpenClaw

新生儿日常记录技能
直接从 baby-diary 包导入功能
"""

import importlib.util
from pathlib import Path

# Load baby-diary module dynamically
baby_diary_path = Path(__file__).parent / "baby-diary" / "__init__.py"
spec = importlib.util.spec_from_file_location("baby_diary_module", baby_diary_path)
baby_diary_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baby_diary_module)

# Import functions from baby-diary module
record_create = baby_diary_module.record_create
record_query = baby_diary_module.record_query
record_list = baby_diary_module.record_list
record_get = baby_diary_module.record_get
record_update = baby_diary_module.record_update
record_delete = baby_diary_module.record_delete
daily_summary = baby_diary_module.daily_summary
compare_with_standards = baby_diary_module.compare_with_standards
get_baby_config = baby_diary_module.get_baby_config
set_baby_config = baby_diary_module.set_baby_config
image_view = baby_diary_module.image_view
list_images = baby_diary_module.list_images
image_gallery = baby_diary_module.image_gallery
generate_thumbnail = baby_diary_module.generate_thumbnail
refresh_index = baby_diary_module.refresh_index
format_records_for_display = baby_diary_module.format_records_for_display
init_storage = baby_diary_module.init_storage
RECORD_TYPES = baby_diary_module.RECORD_TYPES
RECORD_TYPE_DETAILS = baby_diary_module.RECORD_TYPE_DETAILS
THUMBNAIL_SIZE = baby_diary_module.THUMBNAIL_SIZE
DuplicateRecordError = baby_diary_module.DuplicateRecordError

# 技能元数据
SKILL_METADATA = {
    "name": "baby_diary",
    "description": "新生儿日常记录技能，支持喂奶、大小便、营养品、洗澡、睡眠、生长指标、病情等记录的创建、查询、更新和删除，支持图片查看",
    "version": "1.3.0",
    "author": "babyjour",
}

# 技能端点定义
SKILL_ENDPOINTS = {
    "record_create": {
        "description": "创建新记录",
        "function": record_create,
    },
    "record_query": {
        "description": "查询记录",
        "function": record_query,
    },
    "record_list": {
        "description": "列出某日记录",
        "function": record_list,
    },
    "record_get": {
        "description": "按 ID 获取单条记录",
        "function": record_get,
    },
    "record_update": {
        "description": "更新现有记录",
        "function": record_update,
    },
    "record_delete": {
        "description": "删除记录",
        "function": record_delete,
    },
    "daily_summary": {
        "description": "生成每日总结",
        "function": daily_summary,
    },
    "get_baby_config": {
        "description": "获取宝宝配置",
        "function": get_baby_config,
    },
    "set_baby_config": {
        "description": "设置宝宝配置",
        "function": set_baby_config,
    },
    "image_view": {
        "description": "查看记录中的图片",
        "function": image_view,
    },
    "list_images": {
        "description": "列出记录中的所有图片",
        "function": list_images,
    },
    "image_gallery": {
        "description": "以画廊形式展示图片",
        "function": image_gallery,
    },
    "generate_thumbnail": {
        "description": "生成缩略图",
        "function": generate_thumbnail,
    },
    "refresh_index": {
        "description": "刷新索引",
        "function": refresh_index,
    },
}
