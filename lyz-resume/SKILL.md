---
name: lyz-resume
description: 将旧简历、零散经历、JD、项目材料或口述回答整理为可信且针对岗位的求职简历，并完成 HTML/PDF 排版、验证与视觉复查。适用于从零做简历、不知道写什么、优化或审查简历、按 JD 定制、多岗位版本、只换版式、加入可选照片和生成可投递 PDF；不用于学术 CV、作品集网站、求职信、职业规划、职位代投或单纯模拟面试。
metadata:
  author: Ling99
  version: "2.0.0"
---

# 简历工坊

把“用户很难一次说完整”和“单个岗位版本必须有取舍”当作核心设计条件。每轮先把新信息变成可见资产，再只问一个最值钱的问题；真实、岗位针对性和完成交付优先于华丽措辞。

## 路由

- 从零或信息很少：读取 [访谈与持续动力](references/intake-and-momentum.md)，使用价值回声式单问访谈。
- 旧简历优化或 JD 定制：先用 `scripts/extract_resume.py` 读取本地文件并复述已知事实，禁止重复询问；再读取 [岗位分析与写作](references/role-analysis-and-writing.md) 与 [岗位化内容编排](references/targeted-composition.md)。
- 只换版式：保留原文边界，只确认硬信息与明显冲突，不强迫深度访谈。
- 多个岗位：共用一份事实账本；相近岗位派生版本，证据选择明显不同的岗位分开生成。

## 工作流

1. 在用户工作区创建独立输出目录，保留原文件。识别输入与最短可行路径。
2. 维护私有 `candidate-ledger.json`、`role-analysis.json` 与 `resume-plan.json`；数据结构见 [事实与数据契约](references/facts-and-data-contract.md)。推断只进疑点，不进事实。
3. 若信息不足，每次执行“具体认可 → 价值回声 → 一个问题”。允许“跳过 / 不知道 / 先出草稿”；不要发巨型问卷、空泛夸奖或重复追问。用 `scripts/assess_intake.py` 选择下一缺口。
4. JD 优先于通用岗位知识。无 JD 时只用 [岗位镜头](references/role-lenses.md) 帮助理解和提问，绝不反向制造技能、术语或指标。
5. 达到 `workable` 后先做岗位计划：把证据分为 `core / supporting / brief / omit`，确定第一页叙事、章节顺序和 bullet 预算。弱相关经历不得与核心证据等量展开。
6. 用户确认事实与取舍摘要后写 `resume-data.json`。先运行 `validate_alignment.py` 与 `validate_resume.py`，再运行 `render_resume.py` 生成同源 HTML/PDF。
7. 布局选择读取 [视觉原型与选择](references/visual-design-system.md)。默认只生成一个推荐版本；用户要求比较时最多生成三种拓扑明显不同的版本。
8. 按 [渲染与验收](references/rendering-and-validation.md) 将 PDF 转成逐页图片并实际查看。先删弱内容，再调布局与间距；禁止以不可读小字硬塞一页。

## 对话规则

- 第一轮降低启动成本：告诉用户无需整理、无需专业表达；旧简历、一个目标岗位或一段最熟的经历，任意给一个即可开始。
- 认可必须具体且真实，例如“这条信息把团队成果和你的个人边界分开了”；不要只说“很棒”。
- 每次回答后展示一小段已捕获事实或可用草稿，让用户立刻看到回报。
- 连续三轮没有新增事实时停止同类追问，改用选择题式回忆提示、请用户提供材料，或按当前证据降级生成。
- 不诱导用户猜数字；没有数字时使用交付、验收、范围、质量、风险、采用情况等真实结果。

## 交付契约

默认交付 `candidate-ledger.json`、`role-analysis.json`、`resume-plan.json`、`resume-data.json`、`resume.html`、`resume.pdf`、`alignment-validation.json` 与 `validation.json`。照片默认关闭；开启时只把它当排版资产，不从外貌推断个人信息。最终 PDF 必须为 A4、1–2 页、正文不低于 9.1pt、文本可提取，并经逐页视觉复查。

不得承诺 ATS 分数、面试邀约或就业结果。任何无法确认的 claim 必须删除、降级或清楚标注为待确认。

机器可读 Schema、设计原型与样例位于 `assets/`；触发和输出回归位于 `evals/`。修改路由、岗位计划、布局或数据契约后必须重跑对应评测。
