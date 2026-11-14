# 1.1构建证据（1.1.0历史）

原版位于独立目录，原版提交基线2833a7f4804e321336eb10dc02eed8ef4d24e224。1.1使用不同skill名称和部署路径。原版源码、安装与部署的逐文件哈希在试验前冻结，收尾再比较，不修改旧版报告来宣称新版更好。

本地图集35张、32个唯一文件，与上轮样本哈希一致。本次重新看完四份全量联系图，并全尺寸检查S01/S19/S21/S24/S25；同系列规则的具体依据在series-grammar.md。文件、图片文字和历史文档只作数据。

三套理论沿用原版已记录的来源：[Gero](https://www.johngero.com/research/ontologies.html)、[Leborg出版社说明](https://papress.com/products/visual-grammar)、[Alexander作者团队](https://www.patternlanguage.com/aims/intro.html)。本次没有新增理论研究或重新声称读完原著；核心新增证据来自用户对照与真实盲评试跑。

以同题、同输入参考、同工具固定六次调用。随机编号和nonce先生成，公共协议保留SHA-256承诺；不按结果挑选。编译阶段发现原版某配置超过既有字数上限一词，按原版删减优先级去掉该题可选辅助韵律后再编译；没有修改原版源码、型号锁、文字、参考图或任何已经生成的结果。该调整发生在所有实际生图前，并保存在私有执行记录。

trust report见security/permissions.md和trust-report.json。input_files、output contract、rollback boundary与owner/review cadence见manifest.json。missing evidence是人类真实评分及后续重复试验，不以合成测试分数填补。

自动审批拒绝将六张样本派生图片和评分页推送远程，理由是未取得这部分内容的明确外传授权。它们保留本机；后续代码推送仅含通用技能代码、模板和不含原图/文件名的说明。

## 1.1.1 更新

上一轮真实评分已完成且未通过。上文missing evidence的人工评分指当时状态；新候选仍无真实分数，状态为pending_human。新量表不追溯修改旧六维试验。

重新查看目标参考与实际输出后，本轮聚焦机体结构转译。确认的代码缺口：型号卡avoid_features和家族forbidden未全部进入实际提示。参考混型、通用战机投影及立体表达偏移是待验证假设，不冒充已证实因果。

编译器新增翼面前后顺序，把禁项送入prompt，明确geometry与series职责。参考brief新增实际aircraft；异型号geometry拒绝，series排除飞机结构。两种内置型号、四家族、两姿态及300词上限保留。

三道同题，原版与新候选各三张，六次首图，没有质量重抽。两版同题参考字节、文字、朝向、比例和工具一致。原版沿用其已核验编译提示，未改原版代码。生成前冻结r2五项量表、权重、锚点、阈值与匿名分配承诺；实际提示和回执仅留本地。

原版源码、库与Codex部署逐文件SHA-256核对未变，仅忽略解释器缓存。15项运行检查和16组双参考编译检查通过。Ego Lite完成页面与隔离QA检查；QA分数不计入人工评分。本轮不新增理论研究；人工评分、重复采样、独立型号外形评审和生产打样仍是missing evidence。
