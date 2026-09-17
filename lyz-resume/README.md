# 简历工坊（lyz-resume）

这是一个完整的求职简历生产 Skill：从旧简历、零散经历或低信息对话开始，维护可追溯事实，按 JD 或岗位方向选择证据，完成写作、逻辑审查、HTML/PDF 渲染和逐页视觉验收。

它的关键不是“连续盘问”，而是价值回声式访谈：每次回答都会先被转换成一条可见事实或简历草稿，并说明它补上了哪个证据缺口，然后只问下一件最值得问的事。

## 安装

有 Node.js 时，推荐使用官方 `skills` CLI：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

已安装 Bun 时也可以使用：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

如果包管理器被沙箱拦截、GitHub 网络不稳定，或要接入豆包、WorkBuddy 等未被 CLI 原生列出的平台，请使用仓库内的 `lyz-resume/dist/lyz-resume.zip` 手动复制。完整的 Windows/macOS/Linux 操作、代理 407 处理、Bun registry 配置和安装验证见 [安装与兼容性](references/installation-and-portability.md)。

豆包与 WorkBuddy 当前属于“手动复制兼容”，不是经过其官方安装器验证的原生集成；具体目录以产品界面显示的用户 Skill 目录为准。

典型触发：

- “我什么资料都没有，采访我做一份产品经理简历。”
- “这是旧简历和 JD，帮我针对性改写并生成 PDF。”
- “内容不要改，只重排得更专业。”
- “用同一份经历分别做 AI 产品和增长运营两个版本。”

默认交付：

```text
candidate-ledger.json   私有事实账本
role-analysis.json      岗位要求—证据—缺口映射
resume-data.json        允许公开和渲染的内容
resume.html             可编辑源文件
resume.pdf              文本型投递文件
validation.json         内容与文件验证结果
```

入口是 [SKILL.md](SKILL.md)。访谈、数据契约、岗位镜头、写作审查、渲染命令和安装排障分别放在 `references/`；确定性操作放在 `scripts/`；可运行样例和 Schema 放在 `assets/`。

本 Skill 的 HTML/PDF 渲染与部分验证代码改编自 MIT 许可的 `joeseesun/qiaomu-campus-resume`，详情见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
