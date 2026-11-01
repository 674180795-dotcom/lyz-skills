# 0.2.0 素材错配修复回归

2026-11-02，状态：已完成局部实现与确定性回归；skill整体仍为experimental/candidate。

## 问题与实际复现

用户报告连续处理三个转录文件时，第三份正文为Farza Majeed/HeyClicky，附带背景却称Nikita Bier；执行Agent跳过正文，用网络资料写成TBH/Gas访谈并归档。此记录依据用户的bug report，不声称已检查那三个原始DOCX或回看当时工具日志。

另建立synthetic file-backed fixture，以Farza正文、Nikita文件名和WEB-only问答，复现旧检查器的结构漏洞。原始版本90f9613a6bee9163cd0c196016fa0ac3434b6059返回ready=true；新版拒绝。实际结果见source-gate-comparison.json。此比较是命令执行，不是模型生成实验；新版另有通过新preflight后仍拒绝WEB-only问答的独立测试，避免只靠旧目录格式不兼容得出结论。

## 改动和验收

- 直接读取DOCX正文和表格，保持原始字节快照及规范化文字的哈希一致。
- 每个prepare分配独立input_id；阅读回执、身份锚点、逐块笔记与preflight绑定该输入，阻断跨篇复用。
- 全部分块均需read回执与内容笔记；缺中间分块不能以首尾抽样通过。
- 身份/主题先来自正文，再比对背景；冲突需明确选择和理由。明确指定文件且背景错误时可直接按正文继续，不增加一律请示。
- 姓名要有原文短锚；音译/错字允许显式source_name与normalization_reason。元数据嘉宾与已核正文身份必须一致。
- 问答不允许external/editorial替代原文，转述claims、coverage、speakers需要本输入P段，coverage/speakers还要逐字短锚。
- 语义与编辑审校绑定最终文章哈希，humanizer改稿后失效。delivery-check重算检查并核对当前finalize结果，防止沿用旧状态归档。

18项Python单元测试通过，含8项原有约束与10项新增拒绝/兼容用例。测试内的通过审稿和评分为synthetic fixture，不能当真实编辑质量证据。触发评测为启发式，不是模型原生路由证明。

## 边界与 missing evidence

命令回执只证明原文被输出，不证明Agent阅读理解；逐字锚只证明字符串存在，不证明其支持整段改写。姓名规范化的理由也须语义审查。故仍要求真人或独立模型审校；脚本不认证审稿人，不把自填分数当真实评测。

完全绕过此skill直接调用上传工具，无法被本地CLI系统级阻止。下游必须遵守delivery-check契约。本次没有上传、覆盖或删除任何已有飞书文档/知识库文章。

missing evidence：原事件三个DOCX的完整重放、修复后的真实连续三篇模型成稿、humanizer真实端到端运行与人工验收、旧10对文章盲评。不得据本次回归宣称从此不会幻觉或达到整体正式发布标准。

## 升级与回滚

旧0.1工作目录不自动补门控通过；需以原件重新prepare，保留旧稿和原件。运行不依赖开发目录或工坊。部署保持Skills Manager既有skill id及Codex/Antigravity目标，只更新受管源内容。回滚以本次Git父提交重建运行包，再通过Skills Manager重新导入受管源；不删除部署或原稿。
