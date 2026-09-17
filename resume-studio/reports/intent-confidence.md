# Intent Confidence

- Confidence score: `100/100`
- Confidence band: `high`
- Gate passed: `True`
- Recommended action: Intent is clear enough to package the first routeable version.

## Current Reading

Evidence-grounded resume authoring and PDF validation：接收某位求职者不完整的旧简历、零散经历或口述材料，以低负担单问访谈补齐可验证事实，再针对一个明确岗位生成并验收可直接投递的简历。 Primary output: 一个独立输出目录，其中 candidate-ledger.json 可追溯每条事实，role-analysis.json 将岗位要求映射到证据，resume-data.json 是内容单一事实源，resume.html 可编辑，resume.pdf 为 A4、1–2 页且文本可提取，validation.json 记录机器与逐页视觉验收结果；多岗位版本共享同一事实账本。. Exclusions: 学术 CV、资深高管品牌叙事、作品集网站、求职信、面试训练、职业规划、职位代投。.

## Strong Signals

- The recurring job is concrete enough to anchor the package.
- Real input shape is explicit.
- The hand-back output is concrete.
- Boundary exclusions are already explicit.
- Operational constraints are visible.

## Gaps To Close

- No major intent gaps detected.

## Follow-Up Questions

- No extra follow-up questions required before the first package.
