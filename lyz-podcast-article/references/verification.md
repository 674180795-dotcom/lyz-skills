# 校勘与证据契约

## 事实、发言和转录分别确认

“嘉宾说X”与“X已被证实”不同。字幕可证明文本含有这一说法，不能单独证明数字和商业判断客观正确，也不能完全证明原音就是这些字。区分文本支持、上下文候选、一手资料核实、来源冲突、无法确认。没有听原音不得声称听音校验。

重点检查人名、机构、产品、缩写、数量级、百分比、币种、分母、年化与累计、收入与利润、参数总量与激活量、市场份额的口径、相对日期、否定和概率。名字可能多次错成不同字，不建立跨所有节目的无条件替换表。

“榆树/语数→宇树”“越战面→月之暗面”“MA→MLA”一类样本仅提示需查证，不能成为运行时字典。人名用节目名单与本人/机构资料交叉判断；技术缩写用原始论文对应版本定位；数字冲突先查原音或原节目，缺失则写成归属明确的说法、删去非必要精确值，或标待核。

外部证据与发言冲突时，不篡改嘉宾回答为外部正确答案。保留必要的原说法并归因，加简短编者说明，或删除非关键误述。涉及主线且无法解开时阻止合格成稿状态。

## 主动联网流程

必须先通过[素材门控](source-gate.md)的preflight。只从当前输入已经读到的内容形成待核清单；文件名、附带标题、搜索摘要或上一文件不得替代本篇转录。不能因背景称Nikita Bier就绕过正文，搜索TBH/Gas并编成他的回答。

1. 从待核清单提取精确疑点，优先找原节目介绍/音频或官方转录、公司官网公告/监管披露、论文和官方技术文档；读取对应正文。
2. 搜索摘要、聚合页和转载只作为发现入口。保存标题、URL、访问日期、发布/修订日期、精确位置、支持的具体断言；有日期的事实注明适用时点。
3. 需要浏览器交互时先运行 `ego-browser skill`，只用当前安装的 Ego Lite 内置能力。不得通过其他浏览器或 Computer Use 兜底。普通公开搜索/读取可用宿主的搜索工具。
4. 找不到一手资料时，可采用原创权威媒体作为次级依据并标“secondary”。循环转载不能算多个独立来源。访问失败、没有原音、付费墙、联网不可用都记录为证据缺失，不能填“已证实”。
5. 录制日期、发布日期、转录日期、剪藏日期分别记录。字幕文件头导出时间默认只是未经确认的文本元数据。不能据当前日期推算“去年”，不能据媒体发布时间确定实际录制日。

外部补充放在导语或编者说明，相关句尾用简洁 Markdown 链接。不能塞入嘉宾的第一人称回答。只下载明确需要的公开资料，不发送素材全文给额外服务，不登录/发布/修改平台。

## evidence.json 的最小结构

`prepare` 会创建骨架，必须按真实审校填写。`status` 使用 `draft / needs_review / ready`；只有人工或独立模型完成语义审校才能设 `semantic_review.complete=true`。

- `metadata`：guest、program_url、recorded_at、published_at、transcribed_at、clipped_at。未知为null。
- `input_binding`、`intake`：prepare生成输入绑定；全文分块笔记、身份/主题原文锚点及背景冲突选择按source-gate.md填写。没有通过本输入preflight不能成文。
- `sources`：id、kind（transcript/primary/secondary/audio）、locator（本地文件或URL）、title、accessed_at、published_at、note。外部链接必须实际读过，搜索片段不列为primary。
- `claims`：id、article_paragraph（从标题开始按空行分块，1起算）、text、core（布尔）、status（verified/attributed/unresolved/conflict/omitted）、source_ids、source_paragraphs（如P00001）、original、decision、rationale。纠错放在original与decision中，解释为何允许修改。
- `coverage`：article_paragraph、source_paragraphs、source_ids、kind（transcript/editorial/external）、support、note。transcript/editorial的support为本输入P段逐字短句；每段问答只能用transcript，不能改标external/editorial。editorial明确推导依据。
- `speakers`：label、identity、source_paragraphs、source_ids、support、status。同样给出原文短锚，无法确认身份用中性标识。
- `open_issues`：id、core、description、article_paragraphs。
- `semantic_review`：complete、reviewer、reviewed_at、fact_gate（pass/blocked/unverified）、notes、article_sha256。模型姓名不写成人工审稿人。
- `quality`：五维scores、reviewer、reviewed_at、notes、article_sha256。按quality.md评分；不以自填数字代替证据。

缺失来源的verified不能通过；attributed只表示明确归因，仍需文本出处。核心冲突、核心未决、核心疑问未关闭时不能ready。范围不明的数字不因加了“据说”就自动合格。

## 修复与交付

初稿后两轮返修，每轮记录问题、修改与回查结果。必要的身份、核心数字、主线引语仍未确认时保留 `【待核：具体问题】`，交付待核稿；不在文件末尾藏一条笼统免责声明。

最终校勘记录保留已解决纠错和仍存在问题，正文只保留阅读必需的来源说明。工作目录永不覆盖输入文件；恢复与回滚以原文快照和input SHA256为准。

humanizer或其他后处理改变文章后，重新审校受影响事实和问答映射，再绑定新article_sha256并finalize。向已授权的飞书/本地归档等下游交接前必须delivery-check；待核稿只能明确按待核交付，不能以完成稿归档。该检查不授予上传权限，本skill仍不负责上传。
