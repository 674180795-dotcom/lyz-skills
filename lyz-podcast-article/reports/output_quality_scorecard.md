# 输出质量评测记录

状态：candidate；尚未达到逐篇对标交付门槛。

已建立10对file-backed fixture索引；其中7对完成全文模型对齐分析。
基线/技能成文生成：0/20；匿名作品评审：0/10。没有可报告的文章评分、提升幅度或人工认可。

## 阻塞与证据

本机独立Codex CLI返回账户用量上限。失败执行和已完成执行的模型、耗时、token元数据保存在本地，摘要见output_execution_runs.json。原始错误给出稍后重试时间，不把它换算为未经确认的本地日程。

missing evidence：20篇真实生成稿、10组匿名对照评审、按失败项返修结果、人工审稿及全新素材泛化。

## 已验证的能力

输入保护、证据编号、核心冲突阻断、未完成审校阻断、格式与评分记录检查已经过单元测试。工具通过不代表事实正确。

## 续跑

在源工程中运行：`python3 dev/evaluate.py analyze --workers 3`；已完成分析自动跳过。再运行generate和judge阶段。当前summarize只汇报本轮已完成的分析，后续文章评测完成后需扩展汇总真实评分，不能沿用本报告冒充通过。

## 0.2.0 本地可靠性修复

新增素材身份/全文阅读/preflight、问答原文短锚及改稿后交付校验。18项确定性回归通过；合成文件夹具证实旧检查器可错误接受WEB-only问答，新版拒绝。详见source-gate-regression.md和source-gate-comparison.json。此证据不增加真实文章生成或盲评数量；原有missing evidence保持。
