# Prompt Quality Profile

Skill: `lyz-resume`
Relevance: `prompt-heavy`
Overall quality score: `92.0/100`

## Primary Task Family

**Dialogue interaction**
- Matched keywords: dialogue, 对话, 访谈

## Complexity

- Band: `expert`
- Score: `11`
- Reason: multiple task families plus governance, evaluation, or expert-level constraints

## Need Model

- Explicit Need: 把杂乱候选人资料变成可信、岗位相关、排版完成、可直接投递的简历，并让低信息用户愿意轻松把真实经历说出来。
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: 旧简历 PDF/DOCX/图片、零散文字、目标岗位或 JD、项目链接、口述回答、可选照片
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: 低负担访谈、事实可追溯、JD 关键词有证据、HTML/PDF 同源、页数与视觉验收通过。

## RTF To Skill Mapping

- Role: Use a conversational role that asks only high-leverage questions and remembers the user's goal.
- Task: Clarify intent, resolve uncertainty, and converge toward a recommendation instead of a long option list.
- Format: Return concise prompts, decision points, and reviewer-visible assumptions.

## Quality Matrix

### Completeness — 100/100
- Matched signals: input, output, constraint, example
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 95/100
- Matched signals: clear, specific, 具体
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 85/100
- Matched signals: boundary
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 95/100
- Matched signals: execute, use, workflow
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 85/100
- Matched signals: 用户
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Dialogue interaction
- Score: `3`
- Keywords: dialogue, 对话, 访谈
- Role: Use a conversational role that asks only high-leverage questions and remembers the user's goal.
- Task: Clarify intent, resolve uncertainty, and converge toward a recommendation instead of a long option list.
- Format: Return concise prompts, decision points, and reviewer-visible assumptions.

### Prompt engineering
- Score: `3`
- Keywords: prompt, role, format
- Role: Use a prompt engineer role only when role design materially improves execution.
- Task: Map Role, Task, and Format into skill behavior rather than copying a large prompt template.
- Format: Return a compact prompt contract plus tests, quality matrix, and usage notes.

### Creative generation
- Score: `2`
- Keywords: copy, content
- Role: Use a taste-aware creator role with clear audience, tone, and originality boundaries.
- Task: Generate variants, explain selection logic, and preserve the user's distinctive constraints.
- Format: Return options with rationale, selection criteria, and refinement paths.

### Execution operation
- Score: `2`
- Keywords: workflow, execute
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
