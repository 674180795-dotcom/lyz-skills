#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lyz-1688connect 核心测试套件
覆盖: 10 槽位提取、差量催问、分段字符长度、防风控联系方式清洗、规格漂移与熔断
"""

import unittest
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from state_machine_runner import (
    InquiryStateMachine,
    SLOT_FEASIBILITY,
    SLOT_PROCESS_SUGG,
    SLOT_UNIT_PRICE,
    SLOT_SAMPLE_FEE,
    SLOT_LEAD_TIME,
    SLOT_CONTACT_INFO
)


class TestInquiryStateMachine(unittest.TestCase):

    def setUp(self):
        self.sm = InquiryStateMachine(
            factory_name="广州益鼎明辅料厂",
            product_category="空工大徽章魔术贴",
            dimensions="8cm×8cm",
            material_and_craft="高密平织+锁边+魔术贴公毛面",
            order_qty=1000
        )

    def test_01_initial_bubbles_length_constraint(self):
        """测试首发气泡严格在 40 汉字以内"""
        bubbles = self.sm.generate_initial_inquiry(mode="segmented")
        self.assertEqual(len(bubbles), 4)
        for idx, b in enumerate(bubbles, 1):
            self.assertLessEqual(
                len(b), 40,
                f"Bubble {idx} exceeded 40 chars limit: '{b}' (len: {len(b)})"
            )

    def test_02_circuit_breaker(self):
        """测试负向熔断词立即终止对接"""
        sm = InquiryStateMachine(
            factory_name="某淘汰厂",
            product_category="金属徽章",
            dimensions="3cm",
            material_and_craft="锌合金烤漆",
            order_qty=500
        )
        rec = sm.evaluate_response("抱歉老板，我们近期排期排满了，这个量做不了")
        self.assertEqual(rec.status, "rejected_by_factory")
        self.assertEqual(rec.feasibility, "无法承接")
        self.assertIn("做不了", rec.rejection_reason)
        self.assertTrue(sm.is_finished())

    def test_03_specification_drift_vs_rejection(self):
        """测试工艺建议被正确识别为规格漂移而非误判熔断"""
        sm = InquiryStateMachine(
            factory_name="工艺创新厂",
            product_category="刺绣徽章",
            dimensions="8cm",
            material_and_craft="刺绣",
            order_qty=1000
        )
        rec = sm.evaluate_response("图案颜色有渐变，刺绣做不了渐变色，建议数码印+绣边，单价大概1.8元")
        self.assertNotEqual(rec.status, "rejected_by_factory")
        self.assertTrue(rec.spec_drift_detected)
        self.assertEqual(rec.suggested_process, "数码印+绣边")
        self.assertEqual(rec.unit_price, 1.8)

        # 检查漂移追问生成
        drift_inquiry = sm.generate_spec_drift_inquiry()
        self.assertEqual(len(drift_inquiry), 2)
        self.assertIn("数码印+绣边", drift_inquiry[0])

    def test_04_split_phone_contact_extraction(self):
        """测试跨行/拆分手机号识别与 OCR 常见错码修复"""
        ocr_text = (
            "能做的老板，单价1.5左右，打样150元。\n"
            "具体细节加我电话沟通：\n"
            "1992410\n"
            "0604"  # 模拟 OCR 将 6604 识别为 0604
        )
        rec = self.sm.evaluate_response(ocr_text)
        self.assertIn("19924106604", rec.contact_info)

    def test_05_delta_followup_does_not_repeat_quoted_slots(self):
        """测试差量催问绝不重复询问已报项目"""
        # 第一轮：报了单价 1.5，但没报打样、包装、交期
        self.sm.evaluate_response("可以做，1000个单价1.5元")
        self.assertEqual(self.sm.record.unit_price, 1.5)

        followups = self.sm.generate_delta_followup()
        self.assertTrue(len(followups) > 0)
        # 验证追问中绝对不出现“单价多少”或重复问单价
        for f in followups:
            self.assertNotIn("单价多少", f)
            self.assertNotIn("裸价多少", f)
        # 验证首条追问确认了已收到的单价
        self.assertTrue(any("¥1.5" in f for f in followups))

    def test_06_completion_metric_formula(self):
        """测试槽位完成率计算公式与收敛结案判定"""
        # 填充所有 4 个核心槽位 (4/4 * 0.7 = 0.70)
        # 填充 2 个次要槽位 (2/6 * 0.3 = 0.10) => Total = 0.80
        text1 = "能做的，单价1.5元，打样150，大货交期一周。做满1000退样费。"
        rec = self.sm.evaluate_response(text1)
        self.assertGreaterEqual(rec.slots_completion_rate, 0.75)
        self.assertIn(SLOT_FEASIBILITY, self.sm.filled_slots)
        self.assertIn(SLOT_UNIT_PRICE, self.sm.filled_slots)
        self.assertIn(SLOT_SAMPLE_FEE, self.sm.filled_slots)
        self.assertIn(SLOT_LEAD_TIME, self.sm.filled_slots)


if __name__ == "__main__":
    unittest.main()
