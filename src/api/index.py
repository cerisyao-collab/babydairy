"""
阿里云函数计算 FC Web 函数入口

此文件适配 FastAPI 应用到 FC HTTP 函数环境的入口点
使用 WSGI 接口 (environ, start_response)
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Callable

# Add local dependencies to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lib', 'python3.9', 'site-packages'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(environ: Dict[str, Any], start_response: Callable) -> bytes:
    """
    FC HTTP 函数入口处理器 (WSGI 格式)

    Args:
        environ: WSGI environ dict
        start_response: WSGI start_response callable

    Returns:
        Response body bytes
    """
    try:
        from src.api.main import app
        import asyncio

        # 解析 WSGI environ
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')
        query_string = environ.get('QUERY_STRING', '').encode('utf-8')
        content_type = environ.get('CONTENT_TYPE', '')
        content_length = int(environ.get('CONTENT_LENGTH', 0))

        # 读取请求体
        wsgi_input = environ.get('wsgi.input')
        body = b''
        if content_length > 0 and wsgi_input:
            body = wsgi_input.read(content_length)

        # 构造 headers
        headers = []
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers.append((header_name.encode('utf-8'), value.encode('utf-8')))
        if content_type:
            headers.append((b'content-type', content_type.encode('utf-8')))
        if content_length:
            headers.append((b'content-length', str(content_length).encode('utf-8')))

        # 构造 ASGI scope
        scope = {
            'type': 'http',
            'asgi': {'version': '3.0'},
            'http_version': '1.1',
            'method': method,
            'scheme': environ.get('wsgi.url_scheme', 'https'),
            'path': path,
            'query_string': query_string,
            'root_path': '',
            'headers': headers,
            'server': ('0.0.0.0', 8080),
            'client': (environ.get('REMOTE_ADDR', '0.0.0.0'), 0),
            'extensions': {},
        }

        response_started = False
        response_status = 200
        response_headers = []
        response_body = bytearray()

        async def receive():
            return {'type': 'http.request', 'body': body, 'more_body': False}

        async def send(message):
            nonlocal response_started, response_status, response_headers
            if message['type'] == 'http.response.start':
                response_started = True
                response_status = message.get('status', 200)
                response_headers = message.get('headers', [])
            elif message['type'] == 'http.response.body':
                response_body.extend(message.get('body', b''))

        # 执行请求
        asyncio.run(app(scope, receive, send))

        # 转换 headers 格式
        fc_headers = [
            (key.decode('utf-8'), value.decode('utf-8'))
            for key, value in response_headers
        ]
        # 添加 CORS headers
        fc_headers.append(('Access-Control-Allow-Origin', '*'))
        fc_headers.append(('Access-Control-Allow-Methods', '*'))
        fc_headers.append(('Access-Control-Allow-Headers', '*'))

        # WSGI 响应
        status_text = f'{response_status} {"OK" if response_status < 400 else "Error"}'
        start_response(status_text, fc_headers)
        return bytes(response_body)

    except Exception as e:
        logger.exception('Error handling request')
        error_body = json.dumps({
            'error': {'code': 'internal_error', 'message': str(e)}
        })
        start_response('500 Error', [('Content-Type', 'application/json')])
        return error_body.encode('utf-8')
