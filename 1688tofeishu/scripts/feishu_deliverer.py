"""
Feishu Deliverer for 1688 Inquiry Harvester.
Manages Bitable schema, record insertion, and mobile-friendly Docx report publishing.
"""

import os
import json
import subprocess
import requests
from typing import List, Dict, Any

class FeishuDeliverer:
    def __init__(self, config_path: str = "/Users/ling99/.feishu_config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.token = self._get_tenant_token()

    def _get_tenant_token(self) -> str:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self.cfg["app_id"], "app_secret": self.cfg["app_secret"]}
        )
        return resp.json().get("tenant_access_token", "")

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def push_bitable_records(self, app_token: str, table_id: str, records: List[Dict[str, Any]]) -> int:
        headers = self.get_headers()
        success = 0
        for r in records:
            payload = {"fields": r}
            resp = requests.post(
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records",
                headers=headers,
                json=payload
            )
            if resp.json().get("code") == 0:
                success += 1
            else:
                print(f"[Feishu Deliverer] Record push fail: {resp.json().get('msg')}")
        return success

    def publish_docx_report(self, markdown_path: str, title: str) -> str:
        cmd = f"python3 /Users/ling99/.gemini/config/skills/feishu-doc/scripts/feishu_doc.py -f '{markdown_path}' -t '{title}' -c"
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = p.stdout.strip()
        for line in out.split("\n"):
            if "https://my.feishu.cn/docx/" in line:
                return line.strip()
        return out
