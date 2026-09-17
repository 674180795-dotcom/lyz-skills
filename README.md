# lyz-skills

我的 Codex Skill 集合。这里的 Skill 不只是一个提示词，而是一套可以反复调用的工作流：知道什么时候提问、如何保留事实、怎样产出文件，以及交付前如何检查。

当前首个 Skill 是 **resume-studio（简历工坊）**：把旧简历、JD、零散经历或一段口述，整理成可信、针对岗位、可以继续编辑和投递的简历文件。

## 先开始：三步用起来

### 1. 安装 Skill

如果你已经安装了 [skills CLI](https://github.com/vercel-labs/skills)，可以直接安装到 Codex：

```bash
# 安装简历工坊（全局，推荐）
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill resume-studio -y

# 查看仓库里的可用 Skill
bunx skills add 674180795-dotcom/lyz-skills -l
```

也可以用 git clone 手动安装：

```bash
git clone --depth 1 https://github.com/674180795-dotcom/lyz-skills.git "$HOME/code/lyz-skills"
mkdir -p "$HOME/.agents/skills"
rsync -a "$HOME/code/lyz-skills/resume-studio/" "$HOME/.agents/skills/resume-studio/"
```

项目级安装时，把目标目录换成当前项目的 `.agents/skills/resume-studio/` 即可。

### 2. 用自然语言叫它

安装完成后，不需要记命令。直接在 Codex 里说你想完成的事：

```text
用简历工坊帮我做一份产品经理简历。我现在只有一些零散经历。
```

或者：

```text
这是我的旧简历和目标 JD，请保留真实经历，针对这个岗位重写，并生成可投递 PDF。
```

还可以只说：

```text
我不知道简历写什么，先采访我，但一次只问一个问题。
```

### 3. 你只需要提供一点点

不需要先整理资料，也不需要使用专业表达。下面任意一项都可以作为起点：

- 一份旧简历、项目文档或 JD；
- 一个你做过的项目；
- 一次你解决过的具体问题；
- 一段想到什么说什么的语音转文字；
- 甚至只说“我想找什么工作”。

如果暂时答不上来，可以直接说 **“跳过”**、**“不知道”** 或 **“先按现有信息出草稿”**。Skill 会把不确定内容标出来，不会替你编数字、职位或成果。

## 简历工坊会怎么带你完成

它专门为“手里没有完整资料、很难持续回忆”的情况设计：

1. **先降低启动成本**：告诉你无需整理、无需一次说完，从最熟悉的一件事开始。
2. **每次只问一个最值钱的问题**：不发长问卷，不要求你凭空想 KPI。
3. **回答后立即回声**：先具体指出这条信息证明了什么，再展示已经捕获的事实或草稿。
4. **把经历变成证据**：区分你的个人贡献、团队成果、已确认事实和待确认信息。
5. **达到可用就先交付**：信息达到 `workable` 就能生成诚实版本；证据更充分时再升级到 `strong`。
6. **完成文件级验收**：生成 HTML/PDF，检查内容、页数、可提取文本和逐页视觉效果。

对话中的“鼓励”是有依据的。例如它会说：

> 这条信息已经把“团队做了什么”和“你亲自负责什么”分开了，我先记为一条可用证据。下面只补一个关键缺口：当时你具体交付了什么？

它不会用空泛夸奖、制造焦虑或诱导你猜数字来延长对话。每轮都应该让你看到已经得到的东西。

## 你会得到什么

默认交付目录包含：

| 文件 | 用途 |
| --- | --- |
| `candidate-ledger.json` | 私有事实账本：来源、置信度、个人边界和待确认项 |
| `role-analysis.json` | JD 要求、证据映射与缺口 |
| `resume-data.json` | 允许公开并用于渲染的简历数据 |
| `resume.html` | 可编辑的同源 HTML |
| `resume.pdf` | 文本可提取、适合投递的 PDF |
| `validation.json` | 内容与文件验证结果 |

照片默认关闭；如果你主动开启，只把它作为排版资产，不根据外貌推断年龄、性格或能力。

## 适用与边界

适合：

- 从零制作第一份简历；
- 旧简历重写、纠错和结构优化；
- 按不同 JD 生成多个真实版本；
- 只改版式，不改原文；
- 生成 HTML/PDF 并做可读性复查。

不负责：学术 CV、作品集网站、求职信、职业规划、职位代投和单纯模拟面试。它不会承诺 ATS 分数、面试邀约或就业结果。

## 仓库内容

```text
lyz-skills/
└── resume-studio/
    ├── SKILL.md                    # 路由、工作流与交付契约
    ├── README.md                   # Skill 级说明
    ├── references/                 # 访谈、事实契约、岗位分析、渲染验收
    ├── scripts/                    # 提取、评估、验证、渲染脚本
    ├── assets/                     # Schema、样例与模板
    ├── evals/                      # 触发和输出回归样例
    ├── reports/                    # 评测、审查和发布证据
    └── dist/resume-studio.zip      # 可分发压缩包
```

从这些入口深入：

- [简历工坊说明](resume-studio/README.md)
- [Skill 主文件](resume-studio/SKILL.md)
- [访谈与持续动力](resume-studio/references/intake-and-momentum.md)
- [岗位分析与写作](resume-studio/references/role-analysis-and-writing.md)
- [渲染与验收](resume-studio/references/rendering-and-validation.md)
- [评审工作台](resume-studio/reports/review-studio.html)
- [下载压缩包](resume-studio/dist/resume-studio.zip)

## 验证状态

当前版本已完成本地确定性验证：流水线测试、触发回归、输出契约、目标适配、安装/打包检查均已记录在 `resume-studio/reports/`。这些是可复现的工程检查，不等同于真实用户长期使用数据；后续会继续补充真人盲评和采用反馈。

## 第三方说明

HTML/PDF 渲染与部分验证代码改编自 MIT 许可项目 [`joeseesun/qiaomu-campus-resume`](https://github.com/joeseesun/qiaomu-campus-resume)，详见 [THIRD_PARTY_NOTICES.md](resume-studio/THIRD_PARTY_NOTICES.md)。

## 下一步

这个仓库会继续收纳可复用的个人 Skill。新增 Skill 时，首页会同时补上：它解决什么问题、怎么安装、第一句话怎么说、会交付什么，以及明确的边界。
