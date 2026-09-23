# lyz-explanation

一个把复杂概念编译成离线交互实验的 Agent Skill。它先让学习者预测，再交付一个完整因果单元和单文件 HTML，最后通过闭卷问题判断是否能把模型迁移到新情景。

## 安装

从此仓库安装到 Codex：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-explanation -y
```

也可下载 [独立 ZIP](dist/lyz-explanation.zip)，解压后将 `lyz-explanation/` 放入所用 Agent 的 Skill 目录。仓库目录含 [通用 System Prompt](SYSTEM_PROMPT.md)，可直接用于不支持 Skill 的大模型系统消息栏。

## 使用

```text
使用 $lyz-explanation 帮我理解傅里叶变换。
```

首次回复只请你对一个具体情景作预测。回答后，Skill 才交付解释与完整 HTML。保存 HTML 后可离线打开、调节参数并完成页面末尾的闭卷题；把答案贴回对话，由模型依据因果理由判定通关或给出更小的修复实验。

源码与进一步规则见 [SKILL.md](SKILL.md)和[编译协议](references/compiler-protocol.md)。[复合增长样例](examples/compound-growth.html)展示了页面结构。[质量记录](reports/output_quality_scorecard.md)列出已通过的静态与逻辑检查，以及尚未完成的浏览器视觉和真实学习者验证。因此当前标记为试用版。
