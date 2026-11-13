# 技能工坊人工评分流程 r1 · 2026-11-14

## 当前结果

用户要求从刺绣技能的实际迭代体验抽象通用流程：每次技能迭代都要人工评分，按任务选好标准，点选后直接复制分数回聊天；可允许旧新版并存，但本轮技能工坊直接原位更新。已完成候选并更新实际部署，人工评分状态 `pending_human`；尚不能宣称本轮验收通过或优于旧版。

实现及边界见 [README.md](README.md)，具体规则见 [references/human-evaluation.md](references/human-evaluation.md)，技术证据与历史阻塞见 [VALIDATION.md](VALIDATION.md)。不重复旧框架的生成报告，它们不是本次完整发布证据。

## 源码与部署

本目录是增量更新包，不能单独安装。完整本地来源 `~/.codex/skills/yao-meta-skill` 已原位应用 8 个文件：SKILL.md、agents/interface.yaml、4 个人工/输出评测相关 references、assets/human-scorecard.html、tests/human-evaluation-cases.md。

通过 `manage-skills` 的实际 CLI 先 check 再 update 现有“技能工坊”条目；结果 refreshed=true。保留原名称、Default 分组及 Codex、Antigravity、Kiro 既有部署关系。源码、中心库和 Codex 入口的这 8 个文件 SHA-256 一致。不另安装原版/新版技能工坊。此安装仅供试用，不等于人工验收。

## 继续执行

优先接收用户从本轮评分页复制的纯文本。核对会话与 r1 顺序，有效、稳健为核心；权重依次 3/3/1/1/2。单候选验收要求加权均分 ≥ 4，核心项各 ≥ 3；缺分或 N 待补评。评分前冻结的协议与实际页面保留本地，已在仓库忽略。QA 分数不可计入人工证据。

下一步先根据真实分数判断本轮流程是否好用，再只改最弱的一项；不要把本轮扩张为框架全面升级。没有用户要求时不自动无限迭代。若后续做完整框架发布，先处理原有 manifest/frontmatter/Skill IR 命名不一致与安装证据失败，再重建发布证据并跑完整 CI。

实际图片、历史用户评分与匿名映射不属于本次通用更新包，不得随 Git 操作上传。

## Git 状态

实现提交 `8be2655c4906d6009371933e0228b3c3012adec5` 已实际推送 origin/main。交接文件在实现推送后单独提交并推送；其最终 SHA 用 `git log -1 -- skill-updates/yao-meta-skill/HANDOFF.md` 查询，避免自引用。若后续推送失败，应改写实际状态，不能沿用成功表述。

## Suggested skills

- 技能工坊：按本轮新流程读取分数和继续迭代。
- manage-skills：保持原技能来源、库和部署一致。
- ego-browser：需要操作本地评分页时，先运行当前 `ego-browser skill`；仅用 Ego Lite。
- git-pushing、handoff：后续代码工作收尾。
