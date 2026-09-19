# 简历工坊（lyz-resume）

这是一个完整的求职简历生产 Skill：从旧简历、零散经历或低信息对话开始，维护可追溯事实，按 JD 或岗位方向取舍证据、重排篇幅，再通过六种页面原型和多套可组合配色完成 HTML/PDF 渲染与逐页视觉验收。

3.0 在岗位化取舍基础上收敛为六种页面拓扑，加入从参考模板提炼的多套配色，并把证件照选择与未确认事实拦截变成成稿门禁。旧版 v1 `theme` 文件仍可渲染。

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
resume-plan.json        当前岗位版本的取舍、排序与篇幅计划
resume-data.json        允许公开和渲染的内容
resume.html             可编辑源文件
resume.pdf              文本型投递文件
alignment-validation.json 岗位计划与成稿一致性
validation.json         内容与文件验证结果
```

入口是 [SKILL.md](SKILL.md)。岗位化取舍见 [targeted-composition.md](references/targeted-composition.md)，六种页面原型与配色库见 [visual-design-system.md](references/visual-design-system.md)。确定性操作放在 `scripts/`；可运行样例、Schema 和设计注册表放在 `assets/`。

典型验证与渲染：

```bash
python3 scripts/validate_alignment.py role-analysis.json resume-plan.json resume-data.json
python3 scripts/validate_resume.py resume-data.json
python3 scripts/render_resume.py resume-data.json --layout hero-header-linear --skin auto --density auto --output-dir output
```

运行要求为 Python 3.10+。macOS 自带 Python 3.9 不能运行 2.0 脚本。

本 Skill 的 HTML/PDF 渲染与部分验证代码改编自 MIT 许可的 `joeseesun/qiaomu-campus-resume`，详情见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
