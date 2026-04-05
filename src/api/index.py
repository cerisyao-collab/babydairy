"""
阿里云函数计算 FC Web 函数入口

此文件适配 FastAPI 应用到 FC 环境的入口点
"""

import json
import logging
from typing import Any, Dict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    FC Web 函数入口处理器

    Args:
        event: FC 事件对象，包含 HTTP 请求信息
        context: FC 上下文对象

    Returns:
        HTTP 响应对象
    """
    try:
        # 延迟导入 FastAPI 应用（支持冷启动优化）
        from src.api.main import app

        # 解析请求
        http_method = event.get("method", "GET")
        path = event.get("path", "/")
        headers = event.get("headers", {})
        query_string = event.get("queries", {})
        body = event.get("body", "")

        # 构造 ASGI scope
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": http_method,
            "scheme": headers.get("x-forwarded-proto", "https"),
            "path": path,
            "query_string": _encode_query_string(query_string),
            "root_path": "",
            "headers": _convert_headers(headers),
            "server": ("0.0.0.0", 8080),
            "client": ("0.0.0.0", 0),
            "extensions": {},
        }

        # 处理请求体
        if isinstance(body, str):
            body = body.encode("utf-8")

        # 调用 FastAPI 应用
        import asyncio
        from starlette.responses import Response

        # 创建响应收集器
        response_started = False
        response_status = 200
        response_headers = []
        response_body = bytearray()

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_started, response_status, response_headers

            if message["type"] == "http.response.start":
                response_started = True
                response_status = message.get("status", 200)
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        # 执行请求
        asyncio.run(app(scope, receive, send))

        # 返回 FC 响应格式
        return {
            "statusCode": response_status,
            "headers": _format_response_headers(response_headers),
            "body": bytes(response_body).decode("utf-8"),
            "isBase64Encoded": False,
        }

    except Exception as e:
        logger.exception("Error handling request")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": {
                    "code": "internal_error",
                    "message": str(e),
                }
            }),
            "isBase64Encoded": False,
        }


def _encode_query_string(queries: Dict[str, Any]) -> bytes:
    """将查询参数字典编码为查询字符串"""
    from urllib.parse import urlencode
    return urlencode(queries).encode("utf-8")


def _convert_headers(headers: Dict[str, str]) -> list:
    """将 FC headers 转换为 ASGI headers 格式"""
    return [
        (key.lower().encode("utf-8"), value.encode("utf-8"))
        for key, value in headers.items()
    ]


def _format_response_headers(headers: list) -> Dict[str, str]:
    """将 ASGI headers 转换为 FC 响应 headers 格式"""
    return {
        key.decode("utf-8"): value.decode("utf-8")
        for key, value in headers
    }