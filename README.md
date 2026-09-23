# lyz-skills

我的可安装 AI Skill 集合。

这里不是一个单一助手，也不是一堆散落的提示词。每个目录都是一项独立能力：有明确的触发范围、执行流程、交付契约和验证材料。你可以只安装需要的一项，也可以把整个仓库作为持续增长的个人 Skill 工具箱。

## Skill 索引

| Skill | 状态 | 用途 | 文档 | 离线包 |
| --- | --- | --- | --- | --- |
| **lyz-resume**（简历工坊） | 可用 · v1.1.0 | 从旧简历、JD、零散经历或口述开始，生成可信、针对岗位的 HTML/PDF 简历 | [使用说明](lyz-resume/README.md) · [执行入口](lyz-resume/SKILL.md) | [下载 ZIP](lyz-resume/dist/lyz-resume.zip) |
| **lyz-explanation**（解释编译器） | 试用 · v0.1.0 | 从先验预测出发，把复杂概念编译为离线 HTML 交互实验，并以闭卷建模题检验理解 | [使用说明](lyz-explanation/README.md) · [执行入口](lyz-explanation/SKILL.md) · [通用 System Prompt](lyz-explanation/SYSTEM_PROMPT.md) | [下载 ZIP](lyz-explanation/dist/lyz-explanation.zip) |

以后新增的 Skill 都会先登记在这里。首页只负责索引、安装和通用约定；每项 Skill 的具体用法放在它自己的目录中。

## 安装

### 推荐：Node.js / npx

不需要先安装 Bun。把 `<skill-name>` 换成索引中的名称：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill <skill-name> -y
```

例如：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

查看仓库中的 Skill：

```bash
npx -y skills add 674180795-dotcom/lyz-skills --list
```

安装全部 Skill：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill '*' -y
```

### 可选：Bun / bunx

已经使用 Bun 时，命令等价：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill <skill-name> -y
```

### 包管理器不可用：下载 ZIP

每个已发布 Skill 在索引中提供独立 ZIP。解压后，把完整的 `<skill-name>/` 复制到目标产品的用户 Skill 目录；目录内应直接包含 `SKILL.md`，不要多套一层同名文件夹。

macOS / Linux 的通用 Agent Skills 目录示例：

```bash
unzip <skill-name>.zip
mkdir -p "$HOME/.agents/skills"
cp -R <skill-name> "$HOME/.agents/skills/<skill-name>"
```

Windows PowerShell 示例：

```powershell
Expand-Archive .\<skill-name>.zip -DestinationPath .\skill-package
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\skill-package\<skill-name>" "$env:USERPROFILE\.agents\skills\<skill-name>"
```

豆包、WorkBuddy 或其他未被 `skills` CLI 原生列出的产品，以产品界面或文档显示的“用户 Skill 目录”为准。能手动读取 Agent Skills 格式，不等于该产品拥有经过验证的原生适配。

## 安装失败时

- 没有 Bun：直接使用上面的 `npx` 命令。
- `npx`/`bunx` 的缓存写入被宿主沙箱拦截：使用独立 ZIP 手动复制。
- Bun 访问 `registry.npmmirror.com` 返回 407：按网络策略处理代理白名单，或用 `BUN_CONFIG_REGISTRY=https://registry.npmjs.org` 指定 registry。
- GitHub clone 或 tarball 下载反复中断：优先下载索引中的小型 ZIP，不要无上限重试。
- 命令被 `SIGTERM` 且没有任何输出：同时检查宿主沙箱、代理和 GitHub TLS，不能仅凭这一条认定 Skill 损坏。

每个 Skill 的依赖、平台声明和完整排障记录都在其自己的 README 或 `references/` 中。例如：[lyz-resume 安装与兼容性](lyz-resume/references/installation-and-portability.md)。

## 安装后怎么用

在目标 Agent 中用自然语言描述任务即可；明确写出 Skill 名称最稳定：

```text
使用 $<skill-name> 帮我完成：……
```

输入不完整时可以直接说“不知道”“跳过”或“先按现有信息出草稿”。具体的首轮输入、输出文件和能力边界，以对应目录中的 `README.md` 与 `SKILL.md` 为准。

## 共同结构

成熟 Skill 尽量保持相同的可读结构：

```text
<skill-name>/
├── SKILL.md       # 模型如何路由和执行
├── README.md      # 人类如何安装和使用
├── references/    # 需要时才读取的深度规则
├── scripts/       # 确定性操作与工具
├── assets/        # Schema、模板和样例
├── evals/         # 触发与输出回归
├── reports/       # 验证、评审和发布证据
└── dist/          # 可分发安装包
```

不是每项 Skill 都必须拥有全部目录，但都应说明：

- 它解决什么问题，什么情况不该使用；
- 需要哪些输入，怎样处理缺失与不确定信息；
- 会交付什么结果；
- 哪些内容必须由用户确认，哪些不能推断；
- 怎样验证工作流没有悄悄退化。

## 新增 Skill

1. 在根目录创建独立的 `<skill-name>/`；
2. 先写清 `SKILL.md` 的触发条件、边界和交付契约；
3. 按实际需要加入 references、scripts、assets 和 evals；
4. 完成安装、触发、输出和边界检查；
5. 在本页的索引中登记，不把某一项 Skill 的详细说明搬到首页。

首页的信息架构参考了 [ljg-skills](https://github.com/lijigang/ljg-skills) 的“安装 + 索引 + 深入阅读”思路；具体 Skill、验证材料和兼容性声明由本仓库独立维护。
