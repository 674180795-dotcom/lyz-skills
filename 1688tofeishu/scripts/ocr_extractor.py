"""
OCR Extractor and Quote Analyzer for 1688 Factory Inquiries.
Runs local Tesseract OCR and parses structured quotes from chat lines.
"""

import os
import re
import subprocess
from typing import List, Dict, Any

IGNORE_PHRASES = [
    "打电话", "发订单", "发商品", "AI查企", "工厂信息", "输入想咨询的内容",
    "发送", "清除未读", "搜款比价", "采购车", "消息", "首页", "我的"
]

class OCRExtractor:
    def __init__(self, tessdata_lang: str = "chi_sim"):
        self.lang = tessdata_lang

    def run_ocr(self, image_path: str) -> List[str]:
        cmd = f"tesseract '{image_path}' stdout -l {self.lang} 2>/dev/null"
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = []
        for line in p.stdout.split("\n"):
            line = line.strip()
            if line and not any(ign in line for ign in IGNORE_PHRASES):
                lines.append(line)
        return lines

    def extract_factory_record(self, factory_name: str, keyword: str, image_paths: List[str]) -> Dict[str, Any]:
        all_lines = []
        for p in image_paths:
            if os.path.exists(p):
                lines = self.run_ocr(p)
                for l in lines:
                    if l not in all_lines:
                        all_lines.append(l)

        full_text = "\n".join(all_lines)

        # Baseline record structure
        record = {
            "工厂全称": factory_name,
            "对接状态": "已出详细报价",
            "工艺方案建议": "待分析",
            "打样/版费": "待出样确认",
            "大货单价(1000套)": "待报价",
            "背卡与包装费": "待报价",
            "普票税点": "未明示",
            "11.15能否发货": "待确认",
            "综合推荐评级": "⭐⭐⭐ 报价偏高/能力受限",
            "核心沟通记录与商务建议": full_text[:300] if full_text else "无有效回复"
        }

        # Check timeout / inactive
        if "商家长时间没有回复" in full_text or len(all_lines) <= 2:
            record["对接状态"] = "超时未回复"
            record["综合推荐评级"] = "❌ 暂不考虑/无实质回复"
            record["核心沟通记录与商务建议"] = "商家长时间无应答或仅发自动广告，无实质商业沟通价值。"
            return record

        # Check refusal / unable to produce
        if any(kw in full_text for kw in ["做不了", "发不了货", "无法生产", "平织的"]):
            if "发不了货" in full_text:
                record["11.15能否发货"] = "无法满足/直接拒绝"
            if "做不了" in full_text or "平织" in full_text:
                record["工艺方案建议"] = "明确表示机台工艺不匹配/做不了"
            record["综合推荐评级"] = "❌ 暂不考虑/无实质回复"

        # Check sample fee
        sample_match = re.search(r'(打样|版费|开版)\s*[:：]?\s*(\d+(\.\d+)?)\s*元?', full_text)
        if sample_match:
            record["打样/版费"] = f"¥{sample_match.group(2)}元"

        # Check unit price
        price_match = re.search(r'(单价|大货|每个|一套)\s*[:：]?\s*(\d+(\.\d+)?)\s*元?', full_text)
        if price_match:
            record["大货单价(1000套)"] = f"¥{price_match.group(2)}/个"

        # Check tax
        tax_match = re.search(r'(普票|税点|专票|发票)\s*[:：]?\s*(\d+(\.\d+)?)\s*(个点|点|%)', full_text)
        if tax_match:
            record["普票税点"] = f"{tax_match.group(2)}个点"

        # Check lead time
        if any(kw in full_text for kw in ["可以发货", "没问题", "能发货", "可以满足"]):
            record["11.15能否发货"] = "可以满足"

        return record
