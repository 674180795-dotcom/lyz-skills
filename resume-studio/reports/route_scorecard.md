# 触发路由评测

- 27/27 通过：应触发 12，不应触发 10，近邻边界 5。
- Precision 1.0，Recall 1.0，误触发 0，漏触发 0。
- 使用 `evals/semantic_config.json` 与阈值 0.18；默认的“技能创建”语义表不适用于简历领域，未被用作发布证据。

命令证据来自 `yao-meta-skill/scripts/trigger_eval.py`，评测日期为 2026-09-17。
