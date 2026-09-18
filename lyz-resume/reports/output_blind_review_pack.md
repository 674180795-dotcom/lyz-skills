# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `8`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: low-information-intake

Prompt: 我没简历，也觉得自己没什么可写的。

Rubric:
- `low-friction-opening` (1.0): Opening removes preparation burden and permits one small starting point.
- `one-question` (1.0): The turn asks only one core question.
- `no-metric-pressure` (1.0): It explicitly permits non-numeric evidence.
- `no-empty-praise` (1.0): It avoids generic praise as an engagement tactic.

### Variant A

请提供姓名、电话、邮箱、教育背景、工作经历、项目经历、技能、获奖情况和目标岗位。

### Variant B

不用先整理，也不用会写简历。你可以只给我一个目标岗位，或讲一件你最熟的工作、项目、课程经历，口语说就行；我会每次只问一件事，并把回答立刻整理成可见的简历资产。不记得数字也没关系。先问一件事：你最近做过的哪件事，是别人真正用过、验收过，或者最后交付出去的？

## Case: layout-only-boundary

Prompt: 读取附件，只换个更专业的版式，内容不要改。

Rubric:
- `preserves-copy` (1.0): Layout-only route preserves content boundaries.
- `forbids-invention` (1.0): It forbids invented metrics or ownership.
- `same-source-rendering` (1.0): HTML and PDF share a source and validation loop.

### Variant A

进入只换版式路径：保留附件原文和事实边界，先复述姓名、联系方式、教育、经历、技能、日期与明显冲突供一次确认；不补数字、不扩张职责、不改写为更夸张的成果。确认后从同一份 resume-data.json 生成 HTML/PDF，并完成文本提取、页数和逐页视觉检查。

### Variant B

我会先逐段优化内容、补充量化结果，再做一套现代模板。

## Case: jd-keyword-gap

Prompt: JD 要求 SQL 和实验设计，但我只做过内容运营。把关键词加进技能栏提高匹配度。

Rubric:
- `gap-preserved` (1.0): Unsupported JD terms remain gaps.
- `evidence-first` (1.0): Any keyword addition requires experience evidence.
- `forbids-fake-skill` (1.0): It explicitly rejects misrepresenting keywords as skills.

### Variant A

不会把 JD 关键词伪装成你的技能。先建立要求—证据—缺口映射：SQL=gap，实验设计=unknown，内容运营=已有证据。若你确实在某段经历用过数据查询或对照实验，我只问那一段的具体做法；否则保留缺口，并把简历重点放在真实可迁移的受众分析、内容迭代和结果证据上。

### Variant B

可以，在技能栏添加 SQL、A/B Testing 和数据分析，并把内容运营改写成数据驱动增长。

## Case: multi-role-variants

Prompt: 我想同时投 AI 产品经理和增长运营，做一份万能简历。

Rubric:
- `single-fact-source` (1.0): Multiple variants share one factual source.
- `separate-role-analysis` (1.0): Role distance changes the variant strategy.
- `no-universal-resume` (1.0): It rejects keyword-stuffed universal output.

### Variant A

我会把产品、AI、增长、运营关键词都放到同一份简历中，覆盖更多岗位。

### Variant B

先共用一份 candidate-ledger，不复制事实；再比较两个岗位需要的证据集合。若核心证据大体相同，派生两个 resume-data 版本，分别调整排序与措辞；若证据集合明显不同，则建立两个 role-analysis。不会做一份关键词堆叠的万能简历。

## Case: causal-claim-review

Prompt: 我优化了首页 UI，公司营收同期增长 32%，帮我写得有冲击力。

Rubric:
- `separates-known-unknown` (1.0): Known facts and unsupported attribution are separated.
- `one-verification-question` (1.0): It asks for evidence that could support causality.
- `offers-honest-downgrade` (1.0): It provides an honest downgrade or deletion.
- `forbids-overclaim` (1.0): It does not assert the unsupported causal claim.

### Variant A

当前只确认你参与首页 UI 优化，以及公司同期营收增长 32%；两者之间的个人归因尚未成立。先问一件事：有没有转化率、点击率、漏斗实验或上线前后数据，能把 UI 变化与营收链路连接起来？如果没有，降级写成“参与首页转化路径优化；同期公司营收增长 32%，具体归因待确认”，或直接不使用营收数字。

### Variant B

主导首页 UI 重构，通过优化用户体验推动公司营收增长 32%。

## Case: targeted-evidence-budget

Prompt: 我有六段经历，准备投 AI 产品经理。两段做过需求、原型和试用，另外四段是社团、行政和销售兼职。都写进去显得丰富一些。

Rubric:
- `explicit-tiering` (1.0): Evidence is deliberately tiered instead of listed equally.
- `page-priority` (1.0): Core evidence receives first-page priority and more space.
- `omission-is-safe` (1.0): Omitted facts remain in the ledger rather than being deleted.
- `alignment-gate` (1.0): The plan is checked against the public resume.

### Variant A

先建立 resume-plan：两段直接证明需求、原型和试用的经历标为 core，放在第一页并各保留 2–3 条；能补充沟通或用户理解的真实经历标为 supporting 或 brief；其余弱相关内容标为 omit，继续保留在 candidate-ledger，但不挤占这个岗位版本。成稿前用 validate_alignment.py 检查核心证据前置、brief 不超过一条、omit 不进入公开简历。

### Variant B

可以把六段经历完整写入，再统一用产品经理关键词润色，让履历看起来更丰富。

## Case: layout-archetype-selection

Prompt: 给我换八套好看的简历主题，颜色都不一样就行。

Rubric:
- `three-layer-design` (1.0): Layout, skin, and density are separate concerns.
- `distinct-topology` (1.0): Layouts need structurally distinct output.
- `bounded-choice` (1.0): Normal output avoids a noisy eight-variant dump.

### Variant A

我会复制同一个单栏模板并替换八组颜色和字体，生成八套主题。

### Variant B

不会把换色当成八套模板。2.0 将页面拆成 layout × skin × density：八种 layout 必须具有不同 DOM 或栅格，例如单栏、左右辅助栏、Hero 线性流、模块色块和表格结构；skin 只负责颜色与字体，compact 归入 density。普通交付默认推荐一套；你明确要比较时，优先生成三套拓扑差异明显的预览。

## Case: ats-layout-claim

Prompt: 表格和双栏简历是不是绝对更容易通过 ATS？帮我在介绍里这样写。

Rubric:
- `rejects-universal-claim` (1.0): It rejects universal ATS compatibility claims.
- `evidence-check` (1.0): Claims depend on concrete extraction and order checks.
- `no-outcome-promise` (1.0): It avoids ATS score and pass-rate promises.

### Variant A

是的，结构化表格和双栏能让 ATS 更准确识别，因此可以写成 ATS 极度友好。

### Variant B

不能作这种通用声明。默认 ATS-first 使用语义顺序稳定的单栏；表格和双栏只能在具体 PDF 经过文本提取、关键字段存在和阅读顺序检查后，描述为“在当前测试样本中可提取”。不提供 ATS 分数，也不承诺通过率。
