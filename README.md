# lyz-skills

我的 Codex Skill 集合。

这个仓库不是一个单一助手，也不是一组散落的提示词，而是一个持续增长的个人 Skill 库：把可重复的工作流整理成可以安装、检查、复用和继续演化的独立能力包。

每个 Skill 都有自己的入口、适用范围、输出契约和验证材料。你可以只安装一个，也可以把整个仓库作为自己的 Skill 工具箱。

## Skill 索引

| Skill | 状态 | 用途 | 入口 |
| --- | --- | --- | --- |
| **lyz-resume**（简历工坊） | 可用 | 将旧简历、JD、零散经历或口述整理为可信、针对岗位的 HTML/PDF 简历 | [README](lyz-resume/README.md) · [SKILL.md](lyz-resume/SKILL.md) |

后续新增 Skill 会先在这里登记，再在各自目录中维护完整说明。首页只负责“我有什么、怎么开始、去哪里深入”，不会替代某个 Skill 的详细文档。

## 安装

### 安装单个 Skill

如果你已经安装了 [skills CLI](https://github.com/vercel-labs/skills)，把 `<skill-name>` 换成上面的名称即可：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill <skill-name> -y
```

当前可直接安装：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

### 安装全部 Skill

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill '*' -y
```

### 查看可用 Skill

```bash
bunx skills add 674180795-dotcom/lyz-skills -l
```

### 不使用 CLI：手动复制

```bash
git clone --depth 1 https://github.com/674180795-dotcom/lyz-skills.git "$HOME/code/lyz-skills"
mkdir -p "$HOME/.agents/skills"
rsync -a "$HOME/code/lyz-skills/<skill-name>/" "$HOME/.agents/skills/<skill-name>/"
```

项目级安装时，把目标目录换成当前项目的 `.agents/skills/<skill-name>/` 即可。

## 安装后怎么用

Skill 安装完成后，用自然语言描述目标即可，不需要记住内部脚本或参数：

```text
用 <skill-name> 帮我完成这件事：……
```

更具体的使用方式、首轮输入格式、交付文件和边界，以对应目录中的 `README.md` 与 `SKILL.md` 为准。建议先看 Skill 的 README，再开始使用；如果信息不完整，直接说“不知道”“跳过”或“先按现有信息出草稿”，不要为了配合格式而编造内容。

## 当前 Skill：lyz-resume

简历工坊是本仓库的第一个可用 Skill。它面向从零做简历、优化旧简历、按 JD 定制、多岗位版本、只换版式，以及生成并验收 HTML/PDF 的场景。

它特别处理一个常见难点：用户没有整理好的材料，也很难一次讲完整。它会把对话设计成低启动成本的单问题访谈：先展示已经捕获的事实或草稿，再只追问一个最有价值的缺口；达到 `workable` 就先交付诚实版本，不替用户虚构数字、职位或成果。

详细说明请看：

- [简历工坊 README](lyz-resume/README.md)：怎么安装、怎么开口、会得到什么；
- [SKILL.md](lyz-resume/SKILL.md)：路由、工作流、对话规则和交付契约；
- [访谈与持续动力](lyz-resume/references/intake-and-momentum.md)：低信息用户的引导方法；
- [岗位分析与写作](lyz-resume/references/role-analysis-and-writing.md)：JD、证据与表达边界；
- [渲染与验收](lyz-resume/references/rendering-and-validation.md)：HTML/PDF 的检查方式；
- [评审工作台](lyz-resume/reports/review-studio.html)：当前版本的审查记录；
- [可分发压缩包](lyz-resume/dist/lyz-resume.zip)：离线分发文件。

## 共同约定

每个成熟 Skill 尽量保持相同的可读结构：

```text
<skill-name>/
├── SKILL.md       # 模型如何路由和执行
├── README.md      # 人类如何安装和使用
├── references/    # 需要时才加入的深度规则
├── scripts/       # 确定性操作与工具
├── assets/        # Schema、模板和样例
├── evals/         # 触发与输出回归
└── reports/       # 验证、评审和发布证据
```

不是每个 Skill 都必须有全部目录；只保留真正支撑它的资源。每个 Skill 都应明确：

- 它解决什么问题，以及什么情况不该使用它；
- 需要哪些输入，如何处理缺失或不确定信息；
- 会交付什么文件或结果；
- 哪些内容必须由用户确认，哪些内容不能推断；
- 如何验证这套工作流没有悄悄退化。

## 新增 Skill 的最短路径

1. 在根目录创建独立的 `<skill-name>/`；
2. 先写清 `SKILL.md` 的触发条件、边界和输出契约；
3. 再按需要加入 references、scripts、assets 和 evals；
4. 在本页的“Skill 索引”中补一行；
5. 完成安装、触发、输出和边界检查后再标记为“可用”。

这样新增 Skill 不会把首页重新变成某一个项目的说明书，也不会让使用者必须读完整个仓库才能找到入口。

## 仓库结构

```text
lyz-skills/
├── README.md
├── lyz-resume/
└── <future-skill>/
```

首页的结构参考了 [ljg-skills](https://github.com/lijigang/ljg-skills) 的“安装 + 索引 + 深入阅读”思路；这里的项目定位、Skill 说明和使用边界均按 `lyz-skills` 自己的工作流重新整理。
