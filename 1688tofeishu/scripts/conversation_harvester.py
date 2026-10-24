"""
Conversation Harvester for 1688 Mobile App.
Automates multi-factory chat message inspection, snapshot collection, and safe navigation.
"""

import os
import re
import sys
import time
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple

class ConversationHarvester:
    def __init__(self, evidence_dir: str = "/tmp/1688_harvest"):
        self.evidence_dir = evidence_dir
        os.makedirs(self.evidence_dir, exist_ok=True)

    def _sh(self, cmd: str) -> str:
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return p.stdout.strip()

    def get_focused_activity(self) -> str:
        return self._sh("adb shell dumpsys window | grep mCurrentFocus")

    def is_in_chat(self) -> bool:
        return "CBUMessageChatActivity" in self.get_focused_activity()

    def is_in_home_tab(self) -> bool:
        return "V5HomeActivity" in self.get_focused_activity()

    def exit_chat_safely(self, max_retries: int = 4) -> bool:
        """
        Guaranteed safe exit from CBUMessageChatActivity back to V5HomeActivity.
        Uses top-left back button (67, 188) and keyevent 4 fallback.
        """
        for _ in range(max_retries):
            if not self.is_in_chat():
                return True
            self._sh("adb shell input tap 67 188")
            time.sleep(1.0)
            if not self.is_in_chat():
                return True
            self._sh("adb shell input keyevent 4")
            time.sleep(1.0)
        return not self.is_in_chat()

    def reset_list_to_top(self):
        """
        Safe gesture to reset 1688 message list to the very top.
        """
        self.exit_chat_safely()
        for _ in range(4):
            self._sh("adb shell input swipe 600 600 600 2200 150")
            time.sleep(0.2)
        time.sleep(1.0)

    def dump_hierarchy(self) -> Optional[ET.ElementTree]:
        self._sh("adb shell uiautomator dump /sdcard/harvester_dump.xml")
        self._sh("adb pull /sdcard/harvester_dump.xml /private/tmp/harvester_dump.xml")
        try:
            return ET.parse("/private/tmp/harvester_dump.xml")
        except Exception as e:
            print(f"[Harvester Error] Dump parse failed: {e}")
            return None

    def find_factory_bounds(self, keyword: str, max_scrolls: int = 6) -> Optional[Tuple[int, int]]:
        for step in range(max_scrolls):
            tree = self.dump_hierarchy()
            if tree:
                for node in tree.iter():
                    text = node.attrib.get("text", "")
                    if keyword in text:
                        bounds = node.attrib.get("bounds", "")
                        m = list(map(int, re.findall(r"\d+", bounds)))
                        if len(m) == 4 and 450 < m[1] < 2350:
                            cx = (m[0] + m[2]) // 2
                            cy = (m[1] + m[3]) // 2
                            return cx, cy
            # Scroll down to reveal next batch
            self._sh("adb shell input swipe 600 1700 600 1000 350")
            time.sleep(1.2)
        return None

    def capture_factory_chat(self, idx: int, keyword: str, full_name: str) -> Dict[str, str]:
        print(f"[{idx}] Harvester inspecting: {full_name} ({keyword})...")
        self.reset_list_to_top()
        coords = self.find_factory_bounds(keyword)
        if not coords:
            print(f"  [Error] Factory {keyword} could not be located in list!")
            return {}

        cx, cy = coords
        self._sh(f"adb shell input tap {cx} {cy}")
        time.sleep(2.0)

        if not self.is_in_chat():
            self._sh(f"adb shell input tap {cx} {cy}")
            time.sleep(2.0)

        paths = {}
        # 1. Bottom
        bot_path = os.path.join(self.evidence_dir, f"f_{idx:02d}_{keyword}_bot.png")
        self._sh(f"adb shell screencap -p /sdcard/h_bot.png && adb pull /sdcard/h_bot.png {bot_path}")
        paths["bot"] = bot_path

        # 2. Mid
        self._sh("adb shell input swipe 600 800 600 1800 350")
        time.sleep(1.0)
        mid_path = os.path.join(self.evidence_dir, f"f_{idx:02d}_{keyword}_mid.png")
        self._sh(f"adb shell screencap -p /sdcard/h_mid.png && adb pull /sdcard/h_mid.png {mid_path}")
        paths["mid"] = mid_path

        # 3. Top
        self._sh("adb shell input swipe 600 800 600 1800 350")
        time.sleep(1.0)
        top_path = os.path.join(self.evidence_dir, f"f_{idx:02d}_{keyword}_top.png")
        self._sh(f"adb shell screencap -p /sdcard/h_top.png && adb pull /sdcard/h_top.png {top_path}")
        paths["top"] = top_path

        self.exit_chat_safely()
        return paths

    def clean_remote_temp(self):
        self._sh("adb shell rm -f /sdcard/h_*.png /sdcard/harvester_dump.xml")
