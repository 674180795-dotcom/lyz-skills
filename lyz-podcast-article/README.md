# 播客成稿 · lyz-podcast-article

将播客字幕、访谈转录或对谈逐字稿编辑为公众号访谈长文，交付 Markdown 成稿和独立校勘记录。支持 `.md`、`.txt`、`.docx` 与粘贴文本。当前版本为 **0.2.0 候选版**。

每份素材单独建立工作目录，完整读取转录，先核对原文中的嘉宾和主题，再与用户提供的标题或背景比对。问答须有原文段落与短句支持；润色后重新审校，归档前执行交付检查。详细流程和使用边界见 [SKILL.md](SKILL.md) 与 [素材门控](references/source-gate.md)。

脚本仅需 Python 3.9+ 标准库。它检查来源记录和文件一致性，无法证明模型真正理解了原文，也不能替代语义审稿。[回归记录](reports/source-gate-regression.md)列出了测试与尚缺证据。原事件三篇真实素材的端到端回归和人工验收尚未完成。

在 Agent 中使用：

```text
使用 $lyz-podcast-article，把这份播客转录编辑成公众号文章。
```

离线包可从仓库的 [dist](dist/lyz-podcast-article.zip) 下载；解压后整个 `lyz-podcast-article/` 目录即为 skill。
