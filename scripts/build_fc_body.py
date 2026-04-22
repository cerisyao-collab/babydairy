#!/usr/bin/env python3
"""Build FC UpdateFunction body JSON from zip file."""
import base64
import json
import os
import sys

zip_path = sys.argv[1]
output_path = sys.argv[2]

with open(zip_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

body = {
    "Code": {"ZipFile": b64},
    "Handler": "src.api.index.handler",
    "Runtime": "python3.9",
    "MemorySize": 256,
    "Timeout": 30,
    "EnvironmentVariables": {
        "DATABASE_URL": os.environ["DATABASE_URL"],
        "WECHAT_APP_ID": os.environ.get("WECHAT_APP_ID", ""),
        "WECHAT_APP_SECRET": os.environ.get("WECHAT_APP_SECRET", ""),
        "JWT_SECRET": os.environ.get("JWT_SECRET", ""),
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRE_MINUTES": "10080",
    },
}

with open(output_path, "w") as f:
    json.dump(body, f)
