# 播客成稿

把提供的md、txt或docx访谈转录整理成可直接阅读的Markdown长文。默认只交付一份文章，保留原话语气，不执行上传发布。

## 0.3.0：首轮质量与轻量交付

- 全文阅读、身份比对、真实问题选择前移到写作之前。
- 默认按原问答推进，只清理影响理解的噪声；不摘要后扩写，不把口语全部改成评论腔。
- 问题写“好奇”，每次回答开头写一次“回答”，续段直接写正文。
- 内部只有系统临时session.json与草稿，不再为普通任务生成十余份原文副本、台账和评分文件。成功后自动清理，目标目录只留一个md。
- 语义自查与最终哈希仍保留；脚本不证明理解、语义蕴含或事实客观真实。没有人工审稿就不声称人工审稿。

## 运行

Python3.9+标准库，无需安装依赖。命令相对于本Skill目录：

```bash
python3 scripts/compact_article.py start --input /absolute/转录.md --out /absolute/output/文章.md
python3 scripts/compact_article.py read --work /absolute/临时目录 --chunk 1
```

逐块完整读取，按references/source-gate.md填写同一session.json里的intake、plan和review：

```text
start → read全部分块 → preflight → plan-check → 写草稿 → 自查 → check → finish
```

具体格式见[素材门控](references/source-gate.md)，口语与结构要求见[编辑方法](references/editorial.md)，正文样式见[模板](references/template.md)。用户明确要求保留内部过程时才加--keep-work；普通任务不交付校勘报告或分数。

旧article_tools.py保留兼容0.2审计任务，不是默认路径。既有工作目录不会自动迁移，也不把旧检查回执套在新的文章上。

## 验证范围

轻量路径有确定性回归测试，覆盖读全、来源与计划、过期审查、重复标签、同字节交付、不覆盖输出与临时清理。它们证明运行约束，不证明文章品质提升。此次用户提供了明确的排版与编辑偏好验收标准；没有新版多篇盲评或人工成稿验收，不作此类主张。

旧reports中的工坊、盲评和打包记录属于此前版本的历史证据，不作为0.3.0的重新发布认证。此次仅报告实际运行的结构、资源、触发与回归检查，不提升既有candidate状态。
