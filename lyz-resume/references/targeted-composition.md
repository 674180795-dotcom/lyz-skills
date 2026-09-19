# 岗位化内容编排

目标不是把候选人的全部历史装进一份简历，而是用真实证据回答目标岗位最关心的问题。事实账本保留全量经历；单个岗位版本必须有主次、取舍和可解释的篇幅分配。

## 四层产物

```text
candidate-ledger.json  全量私有事实
role-analysis.json     岗位要求与证据覆盖
resume-plan.json       本岗位版本的选择、排序与篇幅
resume-data.json       允许公开和渲染的成稿
```

禁止跳过 `resume-plan.json` 直接把全部事实改写进简历。只换版式路径例外，但仍要把 `content_mode` 设为 `layout-only` 并保留原有内容边界。

计划只允许引用 `status: confirmed` 的证据。任何仍在 `uncertainties` 中、材料冲突或用户以“大概/可能”表达的信息都不得进入 `evidence_decisions`；先向用户确认，无法确认则设为 `omit`。最终 `confirmation.status` 未变为 `confirmed` 时，`validate_alignment.py` 必须阻止成稿。

## 岗位定位

先写一句 `role_thesis`：招聘者读完第一页后应形成的一个判断。它必须同时包含目标岗位、候选人的核心证据方向和可信边界，不能是“认真负责、学习能力强”等人格形容词。

从 JD 中选择 1–5 个 `priority_requirement_ids`。优先级顺序是：

1. 有强证据支持的 `must`；
2. 岗位核心职责；
3. 能形成差异化的真实证据；
4. 有证据的加分项。

没有证据的要求仍是 `gap`，不得进入定位、摘要、技能栏或标题。

## 证据分层

每条事实都要进入以下一个层级：

- `core`：直接证明核心要求，优先出现在第一页和对应经历第一条；
- `supporting`：补充方法、范围或相邻能力；
- `brief`：真实但弱相关，仅保留一条或一行；
- `omit`：不进入当前岗位版本，但仍保留在事实账本。

每个决定必须记录 `reason`、`placement` 和 `bullet_budget`。`omit` 的预算必须为 0；`brief` 不得超过 1；`core` 不应比弱相关证据更晚、更短，除非计划中说明版面或时间线原因。

## 第一页叙事

`first_page_story` 最多五项，按阅读顺序回答：

1. 候选人要做什么岗位；
2. 最强的岗位证据是什么；
3. 使用了什么方法或能力；
4. 结果如何被验收或观察；
5. 与同类候选人的真实差异是什么。

第一项核心经历的第一条 bullet 应承担“标题句”作用。远期、新近和职位名称只是辅助因素；岗位相关度和证据强度优先。

## 篇幅纪律

- `section_budget` 表示条目或 bullet 的上限，不是必须填满的配额。
- 同一经历最多 5 条 bullet；多数情况下 `core` 2–4 条、`supporting` 1–2 条、`brief` 1 条。
- 弱相关经历不得为了时间线完整而与核心经历等量展开。
- 内容过长时先删 `brief` 和重复证据，再压缩 `supporting`，最后才调整版式密度。
- 内容较少时扩大留白、字号和行距，不制造经历或堆装饰填满页面。

## 多岗位版本

多个岗位始终共用 `candidate-ledger.json`，分别建立 `role-analysis`、`resume-plan` 和 `resume-data`。如果两个版本只有岗位名称变化，而证据选择、排序、摘要和篇幅完全相同，应视为没有真正完成岗位定制。

## 完成检查

运行：

```bash
python3 "$SKILL_DIR/scripts/validate_alignment.py" \
  role-analysis.json resume-plan.json resume-data.json \
  --output alignment-validation.json
```

验证通过只能证明契约、一致性和可追溯性；最终措辞的真实性仍需用户确认。
