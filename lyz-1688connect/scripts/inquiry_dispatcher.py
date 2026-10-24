#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 工厂自主对接调度器 (Inquiry Dispatcher)
串联真机驱动 (PhoneDriver, SegmentedSender, NavigationGuardian, ChatOCR)
与状态机 (InquiryStateMachine)，实现自动化询盘派发、差量追问与现场 OCR 评估。
"""

import sys
import os
import time
import argparse
import json

# 动态定位环境与依赖
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
WORKSPACE_DIR = os.path.abspath("/Users/ling99/Documents/antigravity/focused-lovelace")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from state_machine_runner import InquiryStateMachine, SourcingInquiry

# 尝试导入硬件层模块
try:
    from mobile_automation_engine.core.phone_driver import PhoneDriver
    from mobile_automation_engine.core.navigation_guardian import NavigationGuardian
    from mobile_automation_engine.core.popup_guardian import PopupGuardian
    from mobile_automation_engine.core.chat_ocr import ChatOCR
    from mobile_automation_engine.core.media_picker import MediaPicker
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False


class InquiryDispatcher:
    def __init__(
        self,
        factory_name: str,
        product_category: str,
        dimensions: str,
        material_and_craft: str,
        order_qty: int,
        artwork_path: str = "",
        ship_deadline_date: str = "",
        max_rounds: int = 3,
        dry_run: bool = False
    ):
        self.factory_name = factory_name
        self.artwork_path = artwork_path
        self.dry_run = dry_run
        
        self.sm = InquiryStateMachine(
            factory_name=factory_name,
            product_category=product_category,
            dimensions=dimensions,
            material_and_craft=material_and_craft,
            order_qty=order_qty,
            ship_deadline_date=ship_deadline_date,
            max_rounds=max_rounds
        )
        
        self.driver = None
        self.guardian = None
        self.ocr = None
        self.media_picker = None

        if HAS_HARDWARE and not self.dry_run:
            try:
                self.driver = PhoneDriver()
                self.guardian = NavigationGuardian(self.driver)
                self.ocr = ChatOCR()
                self.media_picker = MediaPicker(self.driver)
            except Exception as e:
                print(f"[Dispatcher] Warning: Hardware initialization failed: {e}. Falling back to dry-run.")
                self.dry_run = True

    def dispatch_initial_inquiry(self) -> dict:
        """
        下发首发契约：
        1. 注入效果图至相册首格（若提供 artwork_path）
        2. 发送首张效果图
        3. 拟真发送 4-part 分段话术
        """
        bubbles = self.sm.generate_initial_inquiry(mode="segmented")
        print(f"\n[Dispatcher] === Dispatching Initial Inquiry to {self.factory_name} ===")

        if self.dry_run or not self.driver:
            print("[Dispatcher] (DRY-RUN) Generated Initial Bubbles:")
            for idx, b in enumerate(bubbles, 1):
                print(f"  [{idx}] {b}")
            return {
                "success": True,
                "mode": "dry_run",
                "bubbles": bubbles
            }

        # 真实硬件执行
        # 1. 如果有效果图，推送到相册第 1 格
        if self.artwork_path and os.path.exists(self.artwork_path):
            print(f"[Dispatcher] Pinning artwork to camera roll: {self.artwork_path}...")
            self.driver._run_adb(["push", self.artwork_path, "/sdcard/DCIM/Camera/000_target_render.jpg"])
            self.driver._run_adb([
                "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", "file:///sdcard/DCIM/Camera/000_target_render.jpg"
            ])
            time.sleep(0.5)

            # 点击 '+' 调起面板并发送相册第 1 张图
            print("[Dispatcher] Sending artwork via MediaPicker...")
            self.driver.tap(1148, 2589)  # '+' 按钮
            time.sleep(0.8)
            self.driver.tap(468, 2159)   # '相册'
            time.sleep(1.2)
            self.driver.tap(257, 342)    # 勾选第 1 张
            time.sleep(0.5)
            self.driver.tap(1070, 2568)  # 发送(1)
            time.sleep(1.2)

        # 2. 逐条拟真下发 4 条气泡
        print("[Dispatcher] Sending 4 contractual bubbles...")
        for idx, text in enumerate(bubbles, 1):
            self.driver.set_clipboard(text)
            time.sleep(0.1)
            # 点击输入框激活聚焦
            self.driver.tap(500, 1500)
            time.sleep(0.2)
            self.driver.paste()
            time.sleep(0.25)
            # 点击发送按钮
            self.driver.tap(1112, 1534)
            print(f"  -> Bubble {idx} sent: {text}")
            time.sleep(0.65)

        time.sleep(1.0)
        return {
            "success": True,
            "mode": "live",
            "bubbles_sent": len(bubbles)
        }

    def inspect_and_evaluate_chat(self) -> dict:
        """
        截屏并解析当前聊天详情页，填充槽位并返回状态机判定
        """
        print(f"\n[Dispatcher] === Inspecting Chat with {self.factory_name} ===")

        if self.dry_run or not self.driver or not self.ocr:
            print("[Dispatcher] (DRY-RUN) Chat inspection skipped.")
            return {"status": self.sm.record.status, "completion_rate": self.sm.record.slots_completion_rate}

        # 1. 安全抓取截图 (统一使用 /sdcard/ 转存，防 macOS 管道换行符污染)
        local_png = "/tmp/1688_current_chat.png"
        self.driver._run_adb(["screencap", "-p", "/sdcard/1688_current_chat.png"])
        self.driver._run_adb(["pull", "/sdcard/1688_current_chat.png", local_png])
        
        # 2. 本地 OCR 解析
        ocr_text = self.ocr.recognize_image(local_png)
        print(f"[Dispatcher] OCR extracted {len(ocr_text)} characters.")

        # 3. 槽位状态机填充
        record = self.sm.evaluate_response(ocr_text)

        print(f"[Dispatcher] Current Status: {record.status}")
        print(f"[Dispatcher] Completion Rate: {record.slots_completion_rate * 100:.1f}%")
        print(f"[Dispatcher] Filled: {list(self.sm.filled_slots)}")
        print(f"[Dispatcher] Missing: {record.missing_slots}")

        # 4. 生成下一步建议
        next_actions = []
        if record.status == "rejected_by_factory":
            next_actions.append(f"熔断: {record.rejection_reason}，建议立即安全退出。")
        elif record.status == "completed":
            next_actions.append("核心槽位已齐备，已达成比价基准，可直接结案。")
        elif record.spec_drift_detected:
            next_actions.append(f"检测到规格漂移建议 ({record.suggested_process})，建议下发变更重算。")
        else:
            followups = self.sm.generate_delta_followup()
            next_actions.append(f"建议差量催问: {followups}")

        return {
            "record": record.to_dict(),
            "next_actions": next_actions,
            "raw_ocr": ocr_text[:300] + ("..." if len(ocr_text) > 300 else "")
        }

    def dispatch_delta_followup(self) -> dict:
        """
        自动派发差量催问短句
        """
        followups = self.sm.generate_delta_followup()
        if not followups:
            print("[Dispatcher] No follow-up needed.")
            return {"success": False, "reason": "no_followup_needed"}

        print(f"[Dispatcher] === Dispatching Delta Follow-up to {self.factory_name} ===")
        for idx, text in enumerate(followups, 1):
            if self.dry_run or not self.driver:
                print(f"  [DRY-RUN] -> Follow-up {idx}: {text}")
            else:
                self.driver.set_clipboard(text)
                time.sleep(0.1)
                self.driver.tap(500, 1500)
                time.sleep(0.2)
                self.driver.paste()
                time.sleep(0.25)
                self.driver.tap(1112, 1534)
                print(f"  [LIVE] -> Follow-up {idx} sent: {text}")
                time.sleep(0.65)

        return {"success": True, "followups": followups}

    def safe_exit(self):
        """调用 NavigationGuardian 安全退出当前聊天"""
        if self.guardian:
            print("[Dispatcher] Safely exiting chat...")
            self.guardian.safe_exit_chat()


def main():
    parser = argparse.ArgumentParser(description="lyz-1688connect Inquiry Dispatcher")
    parser.add_argument("--factory", type=str, default="测试供应商", help="Factory name")
    parser.add_argument("--product", type=str, default="文创徽章魔术贴", help="Product category")
    parser.add_argument("--dimensions", type=str, default="8cm×8cm", help="Dimensions")
    parser.add_argument("--material", type=str, default="高密平织+锁边+魔术贴公毛面", help="Material and craft")
    parser.add_argument("--qty", type=int, default=1000, help="Order quantity")
    parser.add_argument("--artwork", type=str, default="", help="Artwork image path")
    parser.add_argument("--deadline", type=str, default="", help="Ship deadline")
    parser.add_argument("--mode", type=str, choices=["init", "inspect", "followup", "eval-text"], default="init")
    parser.add_argument("--text", type=str, default="", help="Raw text for eval-text mode")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Run without physical device")

    args = parser.parse_args()

    dispatcher = InquiryDispatcher(
        factory_name=args.factory,
        product_category=args.product,
        dimensions=args.dimensions,
        material_and_craft=args.material,
        order_qty=args.qty,
        artwork_path=args.artwork,
        ship_deadline_date=args.deadline,
        dry_run=args.dry_run
    )

    if args.mode == "init":
        res = dispatcher.dispatch_initial_inquiry()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.mode == "inspect":
        res = dispatcher.inspect_and_evaluate_chat()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.mode == "followup":
        res = dispatcher.dispatch_delta_followup()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.mode == "eval-text":
        rec = dispatcher.sm.evaluate_response(args.text)
        print(json.dumps(rec.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
