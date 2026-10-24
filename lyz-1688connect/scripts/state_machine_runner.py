#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 工厂自主对接与状态机追问引擎 (lyz-1688connect)
Core State Machine Runner: 槽位提取、完成率评估、差量催问生成、规格漂移判定与熔断控制
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import re
import json

# ==========================================
# 10 大标准通用参数槽位常量
# ==========================================
SLOT_FEASIBILITY = "SLOT_FEASIBILITY"       # 工艺可行性 (Core)
SLOT_PROCESS_SUGG = "SLOT_PROCESS_SUGG"     # 工艺建议 (Secondary)
SLOT_UNIT_PRICE = "SLOT_UNIT_PRICE"         # 大货裸单价 (Core)
SLOT_PACKAGING = "SLOT_PACKAGING"           # 包材装配 (Secondary)
SLOT_SHIPPING = "SLOT_SHIPPING"             # 物流运费 (Secondary)
SLOT_SAMPLE_FEE = "SLOT_SAMPLE_FEE"         # 打样/开版费 (Core)
SLOT_REFUND_RULE = "SLOT_REFUND_RULE"       # 退打样费 (Secondary)
SLOT_TAX_POINT = "SLOT_TAX_POINT"           # 增值税点 (Secondary)
SLOT_LEAD_TIME = "SLOT_LEAD_TIME"           # 大货交期 (Core)
SLOT_CONTACT_INFO = "SLOT_CONTACT_INFO"     # 脱媒联系方式 (Secondary)

CORE_SLOTS = [
    SLOT_FEASIBILITY,
    SLOT_UNIT_PRICE,
    SLOT_SAMPLE_FEE,
    SLOT_LEAD_TIME
]

SECONDARY_SLOTS = [
    SLOT_PROCESS_SUGG,
    SLOT_PACKAGING,
    SLOT_SHIPPING,
    SLOT_REFUND_RULE,
    SLOT_TAX_POINT,
    SLOT_CONTACT_INFO
]


@dataclass
class SourcingInquiry:
    factory_name: str
    product_category: str
    dimensions: str
    material_and_craft: str
    order_qty: int
    ship_deadline_date: str = ""
    status: str = "init"  # init, in_progress, completed, partially_quoted, rejected_by_factory, timed_out
    
    # 提取的槽位值
    feasibility: Optional[str] = None
    suggested_process: Optional[str] = None
    unit_price: Optional[float] = None
    pack_price: Optional[float] = None
    total_unit_price: Optional[float] = None
    is_free_shipping: Optional[bool] = None
    shipping_fee: Optional[float] = None
    sample_fee: Optional[float] = None
    is_sample_refundable: Optional[bool] = None
    tax_point: Optional[float] = None
    tax_included_unit_price: Optional[float] = None
    lead_time: Optional[str] = None
    lead_time_ok: Optional[bool] = None
    contact_info: List[str] = field(default_factory=list)
    
    # 状态机度量
    slots_completion_rate: float = 0.0
    rounds_conducted: int = 0
    max_rounds: int = 3
    missing_slots: List[str] = field(default_factory=list)
    rejection_reason: Optional[str] = None
    spec_drift_detected: bool = False
    raw_texts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class InquiryStateMachine:
    """
    通用工业品类 1688 工厂状态机调度器
    执行：首发契约 ➔ OCR语义槽位填充 ➔ 差量催问生成 ➔ 规格漂移重算 ➔ 熔断与结案
    """
    def __init__(
        self,
        factory_name: str,
        product_category: str,
        dimensions: str,
        material_and_craft: str,
        order_qty: int,
        ship_deadline_date: str = "",
        max_rounds: int = 3
    ):
        self.record = SourcingInquiry(
            factory_name=factory_name,
            product_category=product_category,
            dimensions=dimensions,
            material_and_craft=material_and_craft,
            order_qty=order_qty,
            ship_deadline_date=ship_deadline_date,
            max_rounds=max_rounds
        )
        self.filled_slots: set = set()
        self._update_metrics()

    def generate_initial_inquiry(self, mode: str = "segmented") -> List[str]:
        """
        生成首发契约全量合发物料。
        mode="segmented": 返回 3~4 条拟真短气泡（每条严格 <40 汉字，间隙下发）。
        mode="single": 返回单条完整长文契约。
        """
        if mode == "single":
            text = (
                f"老板好，图片中的产品我们近期下单制作，以下为完整采购需求，麻烦一次性核对并逐条回复报价：\n\n"
                f"【基本参数】\n"
                f"1. 产品品类：{self.record.product_category}\n"
                f"2. 规格尺寸：{self.record.dimensions}\n"
                f"3. 材质工艺：{self.record.material_and_craft}\n"
                f"4. 首批数量：{self.record.order_qty} 个\n\n"
                f"【请逐项报出以下 5 点明细，以便直接定单】：\n"
                f"1. 制作可行性：贵厂现有工艺能否完全复刻？有需调整之处请直言。\n"
                f"2. 拆解单价：产品裸价多少？背卡+独立OPP袋+人工装配费多少？\n"
                f"3. 运费与发票：{self.record.order_qty}个是否包邮？开具普票加几个税点？\n"
                f"4. 打样与减免：打样费用多少？做大货能否全额退还打样费？\n"
                f"5. 交期红线：能否确保在预期时间内大货发出？"
            )
            return [text]

        # 分段模式（严格 <40 汉字，规避一次性大段刷屏）
        bubble1 = "老板好，这款产品图片刚发您，贵厂机台能完全复刻吗？"
        bubble2 = f"尺寸按{self.record.dimensions}，材质做{self.record.material_and_craft}，首批做{self.record.order_qty}个。"
        bubble3 = f"麻烦报下{self.record.order_qty}个出厂裸价？另外独立OPP袋+背卡装配人工费多少？"
        bubble4 = "打样费多少？大货能退样费吗？加普票几个点？大货几天能发出？"
        return [bubble1, bubble2, bubble3, bubble4]

    def evaluate_response(self, text: str) -> SourcingInquiry:
        """
        核心状态机状态跃迁函数：解析 OCR 对话文本，填充槽位并更新状态
        """
        if not text:
            return self.record

        self.record.raw_texts.append(text)

        # 1. 规格漂移优先检测 (Specification Drift Check)
        # 若厂家提出工艺瓶颈并给出修改方案（如“做不了渐变色，建议做数码印”），属于规格漂移而非彻底拒绝
        drift_signals = [
            ("做不了渐变色", "数码印+绣边"),
            ("不能刺绣", "织唛工艺"),
            ("建议数码印", "数码印工艺"),
            ("建议织唛", "高密织唛工艺"),
            ("做平织", "平织工艺"),
            ("尺寸要改", "调整尺寸"),
            ("排版浪费", "优化排模尺寸"),
            ("改数码印", "数码印工艺"),
            ("做热转印", "热转印工艺")
        ]
        is_spec_drift = False
        for signal, sugg in drift_signals:
            if signal in text:
                self.record.spec_drift_detected = True
                is_spec_drift = True
                if not self.record.suggested_process:
                    self.record.suggested_process = sugg
                self.filled_slots.add(SLOT_PROCESS_SUGG)
                break

        # 2. 负向信号快速熔断检查 (Rejection Circuit Breaker)
        # 仅在未提出替代工艺建议时触发熔断
        if not is_spec_drift:
            rejection_words = [
                "做不了", "做不到", "发不了", "来不及", "赶不上", "排满了", 
                "不接小单", "做不起", "交期赶不上", "打不了样", "不支持定制",
                "没有这个工艺", "设备做不了"
            ]
            for rw in rejection_words:
                if rw in text:
                    self.record.status = "rejected_by_factory"
                    self.record.rejection_reason = f"触发负向熔断词: {rw}"
                    self.record.feasibility = "无法承接"
                    self._update_metrics()
                    return self.record

        # 3. 工艺可行性槽位 (SLOT_FEASIBILITY)
        if any(kw in text for kw in ["能做", "可以做", "没问题", "做得了", "可以", "能搞", "发来核对"]):
            self.record.feasibility = "可以复刻"
            self.filled_slots.add(SLOT_FEASIBILITY)

        # 4. 工艺建议槽位 (SLOT_PROCESS_SUGG)
        if any(kw in text for kw in ["织唛", "织标", "布贴"]):
            if not self.record.suggested_process:
                self.record.suggested_process = "织唛工艺"
            self.filled_slots.add(SLOT_PROCESS_SUGG)
        elif any(kw in text for kw in ["刺绣", "绣花"]):
            if not self.record.suggested_process:
                self.record.suggested_process = "刺绣工艺"
            self.filled_slots.add(SLOT_PROCESS_SUGG)
        elif any(kw in text for kw in ["数码印", "数码热转印", "热升华"]):
            if not self.record.suggested_process:
                self.record.suggested_process = "数码印工艺"
            self.filled_slots.add(SLOT_PROCESS_SUGG)

        # 5. 大货裸单价槽位 (SLOT_UNIT_PRICE)
        # 支持: 单价1.5, 单价 1.58元, 单价大概1.8元, 1.5左右, ¥1.5, 1.5元一个
        price_patterns = [
            r'单价\s*[:：]?\s*(?:大概|约)?\s*([0-9.]+)\s*(?:左右|元|块)?',
            r'([0-9.]+)\s*单价',
            r'([0-9.]+)\s*(?:元|块)?\s*(?:一个|每件|套|只|条|/件|/个)',
            r'¥\s*([0-9.]+)',
            r'价格\s*[:：]?\s*(?:大概|约)?\s*([0-9.]+)'
        ]
        for pat in price_patterns:
            m = re.search(pat, text)
            if m:
                val_str = m.group(1)
                try:
                    price_val = float(val_str)
                    # 合理性过滤 (0.1 ~ 500元)
                    if 0.1 <= price_val <= 500.0:
                        self.record.unit_price = price_val
                        self.filled_slots.add(SLOT_UNIT_PRICE)
                        break
                except ValueError:
                    pass

        # 6. 包材装配费用槽位 (SLOT_PACKAGING)
        # 支持: 背卡0.2, 包装0.3, 加袋子0.1, 包装人工0.25
        pack_patterns = [
            r'(?:背卡|包装|套袋|装配|人工)\s*([0-9.]+)\s*(?:元|块)?',
            r'加\s*([0-9.]+)\s*(?:元|块)?(?:包装|背卡)'
        ]
        for pat in pack_patterns:
            m = re.search(pat, text)
            if m:
                try:
                    p_val = float(m.group(1))
                    if 0.05 <= p_val <= 20.0:
                        self.record.pack_price = p_val
                        self.filled_slots.add(SLOT_PACKAGING)
                        break
                except ValueError:
                    pass

        # 7. 物流运费槽位 (SLOT_SHIPPING)
        if any(kw in text for kw in ["包邮", "含运费", "包快递", "免运费"]):
            self.record.is_free_shipping = True
            self.record.shipping_fee = 0.0
            self.filled_slots.add(SLOT_SHIPPING)
        elif any(kw in text for kw in ["不包邮", "到付", "运费自理", "发顺丰到付"]):
            self.record.is_free_shipping = False
            self.filled_slots.add(SLOT_SHIPPING)
            ship_fee_m = re.search(r'运费\s*([0-9.]+)\s*(?:元|块)?', text)
            if ship_fee_m:
                try:
                    self.record.shipping_fee = float(ship_fee_m.group(1))
                except ValueError:
                    pass

        # 8. 打样费槽位 (SLOT_SAMPLE_FEE)
        sample_patterns = [
            r'打样(?:费)?\s*[:：]?\s*([0-9.]+)\s*(?:每款|元|块)?',
            r'版费\s*[:：]?\s*([0-9.]+)\s*(?:元|块)?',
            r'打版\s*([0-9.]+)\s*(?:元|块)?',
            r'([0-9.]+)\s*打样'
        ]
        for pat in sample_patterns:
            m = re.search(pat, text)
            if m:
                try:
                    s_val = float(m.group(1))
                    if 10.0 <= s_val <= 5000.0:
                        self.record.sample_fee = s_val
                        self.filled_slots.add(SLOT_SAMPLE_FEE)
                        break
                except ValueError:
                    pass

        # 9. 退打样费规则槽位 (SLOT_REFUND_RULE)
        if any(kw in text for kw in ["退样费", "退打样费", "做大货退", "大货可退", "冲抵货款", "免版费", "抵扣"]):
            self.record.is_sample_refundable = True
            self.filled_slots.add(SLOT_REFUND_RULE)
        elif any(kw in text for kw in ["不退样费", "样费不退", "版费不退"]):
            self.record.is_sample_refundable = False
            self.filled_slots.add(SLOT_REFUND_RULE)

        # 10. 税票点数槽位 (SLOT_TAX_POINT)
        tax_patterns = [
            r'(?:普票|发票|税点|加点)\s*([0-9.]+)\s*(?:个点|点|%)',
            r'加\s*([0-9.]+)\s*(?:个点|点|%)'
        ]
        for pat in tax_patterns:
            m = re.search(pat, text)
            if m:
                try:
                    t_val = float(m.group(1))
                    if 1.0 <= t_val <= 17.0:
                        self.record.tax_point = t_val
                        self.filled_slots.add(SLOT_TAX_POINT)
                        break
                except ValueError:
                    pass

        # 11. 大货交期槽位 (SLOT_LEAD_TIME)
        lead_patterns = [
            r'(?:交货期|交期|大货交期|大货制作周期|工期)\s*[:：]?\s*([一二三四五六七八九十0-9]+[天周月]+|一周)',
            r'([0-9]+)\s*天(?:左右|发出|出货)?',
            r'(一周|半个月|两周)'
        ]
        for pat in lead_patterns:
            m = re.search(pat, text)
            if m:
                self.record.lead_time = m.group(1)
                self.record.lead_time_ok = True
                self.filled_slots.add(SLOT_LEAD_TIME)
                break

        # 12. 脱媒联系方式 (SLOT_CONTACT_INFO)
        # 连续 11 位数字
        for p in re.findall(r'1[3-9]\d{9}', text):
            if p not in self.record.contact_info:
                self.record.contact_info.append(p)
                self.filled_slots.add(SLOT_CONTACT_INFO)

        # 分段气泡拆分手机号识别 (如 1992410 \n 6604)
        split_matches = re.findall(r'(1[3-9]\d{5})[\r\n\s]+(\d{4})', text)
        for s1, s2 in split_matches:
            # 常见 OCR 混淆修复 (0604 -> 6604)
            s2_clean = "6" + s2[1:] if s2.startswith("0") else s2
            combined = f"{s1}{s2_clean}"
            if combined not in self.record.contact_info:
                self.record.contact_info.append(combined)
                self.filled_slots.add(SLOT_CONTACT_INFO)

        # 计算并更新全包总单价与含税单价
        if self.record.unit_price is not None:
            pack = self.record.pack_price or 0.0
            self.record.total_unit_price = round(self.record.unit_price + pack, 4)
            if self.record.tax_point:
                self.record.tax_included_unit_price = round(
                    self.record.total_unit_price * (1 + self.record.tax_point / 100.0), 4
                )

        self._update_metrics()
        return self.record

    def _update_metrics(self):
        """计算槽位完成率与流转状态"""
        core_count = sum(1 for s in CORE_SLOTS if s in self.filled_slots)
        secondary_count = sum(1 for s in SECONDARY_SLOTS if s in self.filled_slots)

        # 权重公式: Core 70% + Secondary 30%
        core_score = (core_count / len(CORE_SLOTS)) * 0.70
        sec_score = (secondary_count / len(SECONDARY_SLOTS)) * 0.30
        self.record.slots_completion_rate = round(core_score + sec_score, 2)

        # 梳理未填核心与重要槽位
        missing = []
        for s in CORE_SLOTS:
            if s not in self.filled_slots:
                missing.append(s)
        for s in [SLOT_PACKAGING, SLOT_SHIPPING, SLOT_REFUND_RULE, SLOT_TAX_POINT]:
            if s not in self.filled_slots:
                missing.append(s)
        self.record.missing_slots = missing

        # 状态判定
        if self.record.status == "rejected_by_factory":
            return

        if self.record.slots_completion_rate >= 0.85 or (core_count == len(CORE_SLOTS) and len(missing) <= 1):
            self.record.status = "completed"
        elif self.record.rounds_conducted >= self.record.max_rounds:
            self.record.status = "timed_out" if self.record.unit_price is None else "partially_quoted"
        else:
            self.record.status = "in_progress"

    def generate_delta_followup(self) -> List[str]:
        """
        差量精准催问生成器：
        仅针对 missing_slots 拼装 1~2 句轻量口语化短句，严禁重复提问已答项。
        """
        if self.record.status in ["completed", "rejected_by_factory"]:
            return []

        self.record.rounds_conducted += 1
        missing = self.record.missing_slots

        # 如果核心单价没报
        if SLOT_UNIT_PRICE in missing:
            msg = f"老板，{self.record.order_qty}个大货裸价和打样费分别多少？我们今天综合核价定单。"
            return [msg]

        # 单价已报，催配套与商务明细
        prompts = []
        # 前缀确认，立起严谨感
        prefix = f"老板，单价¥{self.record.unit_price}收到！"

        sub_queries = []
        if SLOT_PACKAGING in missing:
            sub_queries.append("独立OPP袋+背卡装配每套加多少")
        if SLOT_SHIPPING in missing:
            sub_queries.append(f"{self.record.order_qty}个包邮吗")
        if SLOT_SAMPLE_FEE in missing:
            sub_queries.append("打样费多少")
        if SLOT_REFUND_RULE in missing:
            sub_queries.append(f"大货定{self.record.order_qty}个能全额退样费吗")
        if SLOT_TAX_POINT in missing:
            sub_queries.append("普票税点几个点")
        if SLOT_LEAD_TIME in missing:
            sub_queries.append("大货几天能发出")

        if not sub_queries:
            # 已经很全，只差细节或催单
            return [f"{prefix}麻烦确认下排期今天能否下样哈，谢谢！"]

        # 取前 2~3 个最关键缺失项组合，避免单条消息过长
        joined = "？另外".join(sub_queries[:2]) + "？麻烦核算下哈"
        full_msg = f"{prefix}{joined}"

        # 严格遵守单条 <40 汉字规范，若超长则拆为两条短气泡
        if len(full_msg) > 38:
            b1 = prefix + sub_queries[0] + "？"
            b2 = ("另外" + sub_queries[1] + "？麻烦确认下哈") if len(sub_queries) > 1 else "麻烦确认下哈！"
            return [b1, b2]
        
        return [full_msg]

    def generate_spec_drift_inquiry(self, new_process: str = "") -> List[str]:
        """
        当检测到厂家提出工艺/规格漂移建议时，生成重置基准二次核价话术
        """
        process_name = new_process or self.record.suggested_process or "推荐新工艺"
        b1 = f"收到，那我们采纳贵厂建议，统一按【{process_name}】核算。"
        b2 = f"请问按这个新方案：{self.record.order_qty}套大货全包单价和打样费分别是多少？交期是否有变动？"
        return [b1, b2]

    def generate_contact_lead_prompt(self) -> List[str]:
        """
        生成反向脱媒留号话术（规避 1688 封禁风险）
        """
        b = "老板方便留个绿泡泡吗？我加您发AI矢量原文件，咱拉个产品技术群细聊打样。"
        return [b]

    def is_finished(self) -> bool:
        """检查状态机是否已达终态"""
        return self.record.status in ["completed", "rejected_by_factory", "timed_out", "partially_quoted"]


if __name__ == "__main__":
    # 模块自测运行
    print("=== Testing InquiryStateMachine ===")
    sm = InquiryStateMachine(
        factory_name="广州益鼎明辅料",
        product_category="空工大飞行徽章魔术贴",
        dimensions="8cm×8cm",
        material_and_craft="高密平织+锁边+魔术贴公毛面",
        order_qty=1000
    )

    # 1. 验证首发物料生成
    initial_bubbles = sm.generate_initial_inquiry(mode="segmented")
    print(f"Initial Bubbles ({len(initial_bubbles)} msgs):")
    for idx, b in enumerate(initial_bubbles, 1):
        print(f"  [{idx}] ({len(b)} chars): {b}")

    # 2. 模拟厂家回复 1: 工艺可行性 + 单价 + 建议
    resp1 = "能做的老板，我们推荐做织唛，单价1.5左右，打样150每款"
    record1 = sm.evaluate_response(resp1)
    print("\n--- After Response 1 ---")
    print(f"Status: {record1.status}, Completion Rate: {record1.slots_completion_rate * 100}%")
    print(f"Filled: {sm.filled_slots}")
    print(f"Missing: {record1.missing_slots}")

    # 3. 验证差量催问生成
    followup = sm.generate_delta_followup()
    print("\n--- Delta Follow-up Generated ---")
    for f in followup:
        print(f"  -> {f}")

    # 4. 模拟厂家回复 2: 补充交期 + 退样费 + 拆分手机号
    resp2 = "做满1000个退样费。大货交期一周。有疑问加我 1992410\n0604"
    record2 = sm.evaluate_response(resp2)
    print("\n--- After Response 2 ---")
    print(f"Status: {record2.status}, Completion Rate: {record2.slots_completion_rate * 100}%")
    print(f"Contacts Captured: {record2.contact_info}")
    print(f"Unit Price: {record2.unit_price}, Sample Fee: {record2.sample_fee}, Lead Time: {record2.lead_time}")

    print("\n=== All Tests Passed Successfully ===")
