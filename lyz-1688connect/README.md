# lyz-1688connect (1688 工厂自主建约与状态机追问引擎)

面向通用工业品类（纺织辅料、魔术贴、金属徽章、文创书签、注塑包装等）的 **1688 工厂自主对接与多轮状态机博弈引擎**。
通过“合发建约 ➔ 差量催问 ➔ 变更重算”三大哲学，解决传统自动化对接时“东一句西一句”、“漏答无法收敛”、“规格漂移后报价失真”、“触发平台风控”等工业级难题。

---

## 🎯 核心解决痛点

1. **首发全量合发（Contractual Inquiry）**：
   - 杜绝分散闲聊。将产品、材质、工艺、包装、数量、打样、税票、物流、交期 **8~10 大核心参数一次性打包拟真分段合发**（单条严格 `< 40` 汉字，间隙 0.5~0.7s）；
   - 建立高专业度买家画像，过滤无开模/打样能力的低质作坊，确立核价基准系。
2. **状态机差量精准追问（Slot-Filling & Delta Follow-up）**：
   - 将厂家回复映射入 **10 大标准参数槽位**（Universal Slots）；
   - **未填满槽位触发定点差量催问**：严禁重复提问已答项，仅针对“漏答项”高频精准催答（上限 3 轮），直至 100% 闭环。
3. **规格漂移重新报价（Specification Drift & Re-Quoting）**：
   - 当厂家提出工艺限制（如“做不了渐变色建议改数码印”）引发材质或结构变更时，自动提取新方案，重置基准并对该厂家重新核价。
4. **脱媒反向引导防封（Anti-Violation Protocol）**：
   - 严禁在 1688 聊天框直接发送 11 位数字；
   - 采用反向引导话术（`“老板方便留个绿泡泡吗？我发AI矢量工程图”`）或名片图直发，OCR 自动处理跨行拆分数字（`1992410` + `6604`）。
5. **硬件状态机防死锁（Hardware Guardians）**：
   - 软键盘收起探测、拍立淘相机禁区规避、`LauncherActivity` 1.2 秒无损重置。

---

## 📦 安装

### 推荐：通过 Skills 包管理器

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-1688connect -y
```

或使用 Bun：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-1688connect -y
```

### 手动安装（下载 ZIP）

下载 [独立 ZIP](dist/lyz-1688connect.zip)，解压后将 `lyz-1688connect/` 复制到你的 Agent Skills 目录：

```bash
unzip lyz-1688connect.zip
mkdir -p "$HOME/.gemini/config/skills"
cp -R lyz-1688connect "$HOME/.gemini/config/skills/lyz-1688connect"
```

---

## 🚀 使用方式

在目标 Agent 中直接说：

```text
使用 $lyz-1688connect 帮我向 1688 供应商询盘制作一批 1000 套 8cm×8cm 的魔术贴徽章
```

或自然语言触发：
- *“帮我对接 1688 厂家，按标准需求询盘并追问单价与打样费”*
- *“自动跟进刚才 1688 工厂的报价，补齐漏掉的包装和税点”*

---

## 🛠️ 目录结构与资产

```text
lyz-1688connect/
├── SKILL.md                          # 模型路由与标准执行流水线
├── README.md                         # 技能使用说明
├── agents/
│   └── interface.yaml                # 标准输入输出接口契约
├── references/
│   ├── universal-slots.md            # 10 大通用参数槽位定义与正则规则
│   ├── state-machine-protocol.md     # 离散状态流转图与守卫算法协议
│   ├── inquiry-templates.md          # 契约首发、差量催问与漂移模板库
│   └── hardware-guardians.md         # 硬件级防死锁与真机安全规范
├── scripts/
│   ├── state_machine_runner.py       # 状态机核心引擎（槽位、完成率、熔断）
│   └── inquiry_dispatcher.py         # 真机与状态机全自动化调度器
├── tests/
    └── test_state_machine.py         # 核心自动化测试套件
└── dist/
    └── lyz-1688connect.zip           # 离线发行包
```
