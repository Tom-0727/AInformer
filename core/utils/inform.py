from __future__ import annotations

import json
import os
import sys
from typing import List
from urllib import error, request

from dotenv import load_dotenv

load_dotenv()



def inform(message: str) -> None:
    """向所有 NOTIFY_WEBHOOK_URLS 发送钉钉格式的 JSON 消息。"""
    value = os.getenv("NOTIFY_WEBHOOK_URLS", "")
    urls = [u.strip() for u in value.split(",") if u.strip()]
    
    if not urls:
        print("[inform] 警告: 未找到 Webhook URL 环境变数", file=sys.stderr)
        return

    payload_dict = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    payload = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}

    for url in urls:
        req = request.Request(url, data=payload, headers=headers, method="POST")
        
        try:
            with request.urlopen(req, timeout=5) as resp:
                result = resp.read().decode("utf-8")
                print(f"[inform] Webhook 返回结果: {result}")
                
        except error.URLError as exc:
            print(f"[inform] 网络发送到 {url} 失败: {exc}", file=sys.stderr)


