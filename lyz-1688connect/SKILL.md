---
name: lyz-1688connect
description: MUST USE when the user wants to autonomously reach out to 1688 manufacturers, execute contractual inquiries (合发建约), perform slot-based delta follow-ups (差量催问/状态机追问), handle specification drift and re-quoting (规格变更重算), or conduct multi-turn commercial negotiation for industrial/custom products (魔术贴/徽章/书签/服饰辅料/五金塑胶等). Implements 10 universal parameter slots, anti-violation contact capture, and hardware safety state machines.
metadata:
  author: Yao Team
  version: 1.0.0
  archetype: production
---

# 1688 工厂自主对接与状态机追问技能 (lyz-1688connect)

本技能为面向通用工业品类（纺织辅料、魔术贴、金属徽章、文创书签、注塑包装等）的 **1688 工厂全自动化商业谈判与状态机追问引擎**。
通过“合发建约 ➔ 差量催问 ➔ 变更重算”三大哲学，解决传统自动化在与厂家沟通时“东一句西一句”、“漏答无法收敛”、“规格漂移后报价失真”、“触发平台风控”等工业级难题。

---

## 🏗️ 核心哲学与状态机架构

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  1. 首发全量合发  │ ────> │  2. 差量精准催问  │ ────> │  3. 规格漂移重算  │
│ Contractual     │       │ Slot-Filling &  │       │ Spec Drift &    │
│ Initial Inquiry │       │ Delta Follow-up │       │ Re-Quoting      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **首发全量合发（Contractual Inquiry）**：
   - 严禁分散闲聊。将产品、材质、工艺、包装、数量、打样、税票、物流、交期 **8~10 大核心参数一次性打包合发**；
   - 建立高价值严谨买家画像，过滤无开模/打样能力的低质作坊，确立核价基准系。
2. **状态机差量追问（Slot-Filling & Delta Follow-up）**：
   - 将厂家回复映射入 10 大标准参数槽位（Universal Slots）；
   - **未填满槽位触发定点差量催问**：严禁重复提问已答项，仅针对“漏答项”高频精准催答（上限 3 轮），直至 100% 闭环。
3. **规格漂移重新报价（Specification Drift & Re-Quoting）**：
   - 当厂家提出工艺限制（如“做不了渐变色建议改数码印”、“平织做不了刺绣”）引发材质或结构变更时，自动提取新方案，重置基准并对该厂家重新核价。

---

## 📊 10 大标准参数槽位 (Universal Slots)

| 槽位标识 (Slot ID) | 槽位名称 | 业务定义与要求 | 缺失默认动作 |
| :--- | :--- | :--- | :--- |
| `SLOT_FEASIBILITY` | **工艺可行性** | 现有机台能否完全复刻设计图，有何改动 | 强制催问（第一前置关卡） |
| `SLOT_PROCESS_SUGG`| **工艺建议** | 厂家建议的最佳制造路线（如：织唛 vs 刺绣） | 记录并评估是否触发漂移 |
| `SLOT_UNIT_PRICE`  | **大货单价** | 目标梯队数量（如 1000 套）裸品出厂价 | 强制催问（核心决策项） |
| `SLOT_PACKAGING`   | **包材装配** | 背卡印刷、独立 OPP 袋及人工装配费 | 强制拆解问（严防隐形成本） |
| `SLOT_SHIPPING`    | **物流运费** | 批量货重下的运费归属（包邮 / 到付 / 金额） | 强制催问 |
| `SLOT_SAMPLE_FEE`  | **打样版费** | 产前样品费用（包含周期天数） | 强制催问 |
| `SLOT_REFUND_RULE` | **退打样费** | 大货订单达到多少数量/金额全额抵扣 | 强制追问（商务谈判项） |
| `SLOT_TAX_POINT`   | **税票点数** | 增值税普票（1~3 点）或专票（13 点）点数 | 强制催问（合规报销项） |
| `SLOT_LEAD_TIME`   | **大货交期** | 从定稿到大货出厂发货的绝对天数/承诺日 | 强制催问（排期红线项） |
| `SLOT_CONTACT_INFO`| **脱媒联系** | 高意向工厂电话/微信/厂长对接方式 | 择机触发（按防风控规约） |

> 详细槽位定义与正则规则详见：[通用参数槽位规范](references/universal-slots.md)

---

## 🛡️ 执行守护与防死锁规范 (Guardians)

在真机（如 Redmi K60 Ultra）执行时，必须遵守以下三大约束守卫：

1. **停止追问阈值（Stop Guardian）**：
   - 单家工厂连续追问不得超过 3 轮；超过 3 轮仍缺失核心单价或交期的，自动标记为 `对接超时/意愿低`，转入低优先级。
2. **负向信号快速熔断（Rejection Circuit Breaker）**：
   - 一旦厂家文本出现 `“发不了货”`、`“做不了”`、`“交期赶不上”`，立即标记为 `淘汰/无法承接`，停止追问。
3. **平台文字风控过滤（Anti-Violation Guard）**：
   - 严禁在 1688 聊天框直接发送 11 位连续手机号；
   - 统一采用 **“反向引导法（方案 B）”**（话术：`“老板方便留个绿泡泡吗？我加您发AI矢量原文件，咱拉个产品技术群”`）或名片图直发。
4. **硬件状态机防死锁（Navigation Guardian）**：
   - 退出聊天前必先执行软键盘收起探测（`mInputShown=true`）；
   - 偏离主航道时调用 `am start -n .../LauncherActivity` 1.2 秒一键无损切回根节点；
   - 绝对禁止盲按底部居中区域 `(500~720, 2500~2660)`，规避拍立淘相机死锁。

> 详细真机底层规范详见：[硬件安全与防死锁规范](references/hardware-guardians.md)

---

## 📋 标准执行流水线 (Workflow)

### Step 01 · 需求参数化与首发物料装配
1. 提取用户商品需求，结构化装配基本参数（品类、尺寸、材质工艺、首批数量、交期截止日）；
2. 注入设计效果图至手机相册第 1 格（DCIM 强占位 + 媒体库强刷广播）；
3. 组装**首发契约全量合发母版**（符合 <40 汉字分段发送或单段全量发送规约）。

### Step 02 · 筛选源头工厂与下发询盘
1. 1688 搜索目标品类并切入「找工厂」列表；
2. 筛选具有超级工厂、实力工厂或金牌制造标识的专业源头厂；
3. 进入会话，调用 `MediaPicker` 秒发首图，紧接着下发全量合发询盘。

### Step 03 · 聊天巡检与槽位填充
1. 监控客服回复，通过本地 Tesseract OCR（466 DPI）快速提取文字，规避 1688 聊天气泡无障碍致盲；
2. 运行 `InquiryStateMachine.evaluate_response()`，填充 10 大标准参数槽位并计算完成率。

### Step 04 · 动态分支处理（催问 / 重算 / 结案）
- **分支 A（存在漏答项）**：运行 `generate_delta_followup()`，仅针对缺失槽位动态拼装追问话术（循环 <= 3 轮）；
- **分支 B（检测到规格漂移）**：识别厂家工艺/尺寸限制建议，调用漂移处理模板重新核价；
- **分支 C（触发熔断）**：厂家明确表示无法制作或交期不足，标记淘汰，快速回退。

### Step 05 · 数据结构化结案与交接
1. 达成 100% 槽位填充或达到上限后，生成标准化 `SourcingInquiry` JSON 数据对象；
2. 若涉及脱媒联系方式，自动提取对方微信/电话；
3. 将收敛数据交由下游 `1688-inquiry-harvester` 或输出垂直卡片流汇报。

---

## 🛠️ 脚本工具集

- **状态机核心逻辑**：[`scripts/state_machine_runner.py`](scripts/state_machine_runner.py)
  - 槽位填充器、差量追问生成器、规格漂移判定器、熔断控制器。
- **真机执行调度器**：[`scripts/inquiry_dispatcher.py`](scripts/inquiry_dispatcher.py)
  - 对接 `PhoneDriver`、`SegmentedSender`、`NavigationGuardian` 与 `ChatOCR`，驱动真机闭环运作。
- **参考规范库**：
  - [10 大通用参数槽位定义](references/universal-slots.md)
  - [状态机流转与算法协议](references/state-machine-protocol.md)
  - [标准话术与追问模板库](references/inquiry-templates.md)
  - [真机防死锁与风控规范](references/hardware-guardians.md)
