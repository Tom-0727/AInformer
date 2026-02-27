from __future__ import annotations

import json
import os
import sys
from typing import List
from urllib import error, request

from dotenv import load_dotenv

load_dotenv()



def inform(message: str) -> None:
    """向所有 NOTIFY_WEBHOOK_URLS 发送 JSON 消息。

    - 默认按飞书机器人文本消息格式发送
    - 如果检测到是钉钉机器人地址，则按钉钉文本消息格式发送
    """
    value = os.getenv("NOTIFY_WEBHOOK_URLS", "")
    urls = [u.strip() for u in value.split(",") if u.strip()]
    
    if not urls:
        print("[inform] 警告: 未找到 Webhook URL 环境变数", file=sys.stderr)
        return

    for url in urls:
        if "oapi.dingtalk.com" in url:
            # 钉钉文本消息格式
            payload_dict = {
                "msgtype": "text",
                "text": {
                    "content": message,
                },
            }
        else:
            # 默认飞书文本消息格式
            payload_dict = {
                "msg_type": "text",
                "content": {
                    "text": message,
                },
            }

        payload = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}

        req = request.Request(url, data=payload, headers=headers, method="POST")
        
        try:
            with request.urlopen(req, timeout=5) as resp:
                result = resp.read().decode("utf-8")
                print(f"[inform] Webhook 返回结果: {result}")
                
        except error.URLError as exc:
            print(f"[inform] 网络发送到 {url} 失败: {exc}", file=sys.stderr)


