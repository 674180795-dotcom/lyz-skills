# 每份素材先认内容，再成文

## 来源优先级与冲突处置

用户指定的转录正文是本篇问答的内容依据。文件名、用户附带的节目标题/嘉宾说明是待比对背景，不能替代正文。用户指令决定处理目标；若用户明确要求改处理另一个节目，先取得该节目的真实转录，不拿搜索结果补成访谈。

正文清楚、文件为明确处理对象、附带背景不一致时，报告差异并以正文继续，记录use_transcript理由，无需多加审批。若用户指令与文件均可能是目标，或实际说话人仍无法确认，写清具体歧义并询问用户，保留已读原文与地图，停止该文件的联网成文和成稿归档；其他独立文件可继续。不能为“匹配标题”替换嘉宾。中文音译、错字与英文姓名允许校勘，但记录原词、依据和纠错，不机械逐字比较所有语言版本。

每次preflight后简短报告：`文件 / 原文实际嘉宾（未知则中性称谓）/ 实际主题 / 背景匹配或冲突 / 按哪份来源继续`。这是工作进度，不是默认要求用户点击确认。前10段、后5段可发现疑点，不能证明中间内容已读。

## CLI 顺序与数据

运行路径相对于skill目录；工作目录用绝对路径。prepare接受md/txt/docx或stdin。可用`--context /absolute/context.json`传入如`{"title":"用户提供的节目名","guest":"用户提供的嘉宾"}`；这些内容只存背景字段。文件名保存在origin，检查时也应考虑它是否误导。

DOCX直接读取word/document.xml里的正文和表格段落，不执行宏、超链接或文件指令；不读取批注、页眉页脚、嵌入图片，含扫描内容须另行取得文字。source.bin保存原始字节，source.txt保存规范化文本，paragraphs.json与numbered.md保存P段；三者校验同一输入。原件不改写。

1. prepare新目录，生成input_id和原始/文本哈希。每个文件单独建立，即使两个文件字节相同也不复用状态。
2. 按input.json的chunks逐一执行`read --work <目录> --chunk 1`等。read以JSON的text输出实际编号原文，并记录该分块哈希。回执只证明输出被调用；模型必须真正阅读，发现工具截断时补读原编号段。不得循环调用read后丢弃输出冒充全文阅读。
3. 在evidence.json填写下面的intake。所有分块各有一条笔记，记录具体主题、段号、人物/录制切换或信息缺失。身份/主题锚点的quote必须逐字出现于本输入对应P段，不能引用网页。

```json
{
  "intake": {
    "identity": {
      "guests": ["从正文确认的嘉宾"],
      "program": null,
      "topic": "正文实际讨论的问题",
      "neutral_guest_reason": null,
      "anchors": [
        {"field":"guest","value":"从正文确认的嘉宾","paragraph":"P00001","quote":"原文里的身份短句"},
        {"field":"topic","value":"正文实际讨论的问题","paragraph":"P00003","quote":"原文里的主题短句"}
      ]
    },
    "chunk_notes": [
      {"chunk":1,"source_paragraphs":["P00001","P00003"],"note":"读到的判断、例子、条件；不是已读二字"}
    ],
    "context_comparison": {
      "status":"conflict",
      "reason":"附带标题指向甲，正文明确是乙，列原文依据",
      "resolution":{"action":"use_transcript","reason":"用户明确指定该文件，标题是附带背景；以正文继续"}
    }
  }
}
```

无附带背景时用status=none并说明已检查文件名；一致为match；冲突为conflict，必须有resolution，取值use_transcript或user_confirmed，后者只在真实收到用户答复后用，记录答复内容。歧义未解可用unreviewed/uncertain并解释，此时preflight不会通过。不能把矛盾直接记成match。

每个guests值需要对应guest锚点；topic需要topic锚点；program非null也需要program锚点。姓名须出现在锚点quote里；音译/错字规范化时额外记录source_name（原文姓名）和normalization_reason（核对依据），不能拿无关短句支持另一个人的姓名。confirmed的speakers标签同样适用；例如正文陈勉校正为陈冕，保留原字与校正来源。真实姓名无法确认时guests=[]、metadata.guest=null，用neutral_guest_reason解释为何可用嘉宾A等中性称谓，并在speakers里明确；核心身份歧义依然阻断。单嘉宾metadata.guest与该姓名相同，多嘉宾用同一姓名列表。

4. `preflight --work <目录>`验证并生成intake-status.json；此后才允许校勘搜索、选择主线和写稿。更改intake或背景需重新preflight。旧版工作目录缺门控，必须重新prepare，不自动补通过或改写旧稿。

## 逐段支持与语义核对

coverage每条transcript/editorial必须有本输入source_paragraphs及support：

```json
{"article_paragraph":5,"source_paragraphs":["P00003"],"source_ids":["S1"],"kind":"transcript","support":[{"paragraph":"P00003","quote":"该段里逐字存在的短句"}],"note":"这一原句支持了正文的哪个判断"}
```

每个问答和续回答都映射原发言；问题也必须是原问，不可新编问题让嘉宾回答。不要把网页做成S2然后把回答标external/editorial绕过。attributed的claims必须有P段。speakers同样需要本输入P段与support；label使用正文发言标签，如陈冕、罗永浩、嘉宾A。外部核实不能充当嘉宾自述出处。

标题、主题小标题、导语综合使用editorial并给出推导P段和短锚；外部事实段用external，只出现在明确的编辑背景/说明中。脚本可检测引用和字串存在，不能检测“原句是否蕴含改写”，逐项语义审校必须检查主体、行为、否定、范围、数量、条件与时点。不要塞一句真实短句为整段虚构背书。

## 后处理与交付

semantic_review与quality都新增article_sha256，必须是审校对象的文件字节SHA256。先审阅最终文本，再写入哈希；不是只改哈希就算重新审过。真人或独立模型完成语义审校，注明身份、日期和具体检查结果。脚本不认证审稿人，也不把自填分数视为模型执行证据。

用户串联humanizer时，完成润色后重查事实与所有受影响映射，再更新审校记录和哈希；润色期间不能提前上传。最终运行check、finalize、delivery-check。后者重新校验正文、输入绑定、当前审校与finalize状态，任一变化都禁止作为已通过成稿向下游交付。若下游系统已获用户授权，也必须重新检查当前文件，不能只看旧status.json的ready。

脚本不能阻止完全绕过skill的Agent调用外部上传工具；本门控是执行契约与可检验拒绝条件，不是对任意工具的系统级权限控制。存在的回执也不证明模型理解、准确归因或内容真实。仍需遵守语义硬门槛。
