# 航空刺绣 1.1.5 交接 · 2026-11-15

## 当前目标与状态

用户明确将未来测试固定为其上传多视图中的同一J20。机型一致性属于输入前提和执行检查；设计评分关注保原样的刺绣化简化，以及飞机、背景、字体的逻辑呼应。不能再换型号测试，也不能用翼尾/发动机计数代替设计判断。

整35张是设计资料库，去重为32份视觉来源，含不同子系列。归纳共用的简化、色块、字形重量和绣面语言，不强行声称全库是一种配色，也不每款绑定某两张风格供体。不恢复单图复刻或整幅内容/空间锚。主体相同也要原创。

1.1.0至1.1.4均已收齐真实评分且未通过各自门槛。上一轮r4的完整原始回复、规范化分数和按冻结承诺的复算已本地保存；不能再把1.1.4标待评，也不能用新r5回算旧图。当前1.1.5为pending_human。

## 本轮执行与设计变化

冻结1.1.4作旧版，新候选1.1.5；五个共同J20设计任务，旧新各五，共十次内置image_gen首图。技术重试0、质量重抽/修图0，全保首图。两版每题同brief、同四份参考字节、同工具与预算。

实际输入为用户J20多视图和覆盖全部样本的三张总览。J20副本在本地evaluations/aircraft-20261115-01/references/J20-user-multiview.png；同目录corpus-sheet-1/2/3.png为全库总览。全部仅本地保留，图集来源及哈希另有私有记录；不要上传，也不要改成每题挑两张。用户图作为视觉身份来源，不认证其工程准确性。

设计先定一个场景或行动，再联动飞机姿态、背景开口/轨迹/遮挡与字形切角/基线/配色。design_plan的composition/motif/lettering仍保留兼容，但含义是共同意图的三项记录，不是独立随机抽签。飞机保比例与识别点，归并为4–6个宽色区和少量标记，合并迷彩、蒙皮、铆钉细节，不用全机细线描缝。效果图不等于生产针版认证。

再次通过agent-reach GitHub CLI查阅Ink/Stitch一手README；借鉴SVG图形组织与针线处理的分工，未运行软件、生成针版或认证机器参数。来源与范围见design-expansion.md和open-source-transfer.md。assets/rules.json中的fbs_lexicon为历史解释资料，不能覆盖本版priority或r5标准。

## 盲测顺序与评分续接

用户只要求打散盲测呈现，不要求改生成调用顺序。两种顺序分开记录：生成沿原五题旧新配对流程；展示预先用系统随机源打散十项，同题位置差至少3，中间至少两张其他图。位置映射、nonce、生成和呈现顺序纳入私有匿名承诺。不能按结果排序、临时挑图或刷新重新洗牌。

新会话aircraft-20261115-01 / r5。本地评分页为evaluations/aircraft-20261115-01/index.html，已在Ego任务空间1保留并交回用户。公开界面十项匿名case，case/variant仅A–J，共用标题、任务与参考，不显示T1等配对标识、版本或作者倾向；复制文本仅A–J。配对关系保留私有key中，收齐后才能揭盲比较。

r5顺序为刺绣化简化、图文呼应、同系列感、整体审美、原创设计，权重3/3/3/2/3，总权重14；除整体审美外均为核心。绝对门槛加权均分≥4、每题每核心≥3；相对提升另需提高≥0.3、各核心均分不下降、至少赢3/5题。50项完整真实整数后才比较，N/缺项维持pending_human，关键否决不能被均分掩盖。

保留用户原始回复，按r5顺序规范化到simplification/integration/series/aesthetic/originality。不要让用户重写JSON、理由或身份；也不要索取已提交的旧分。score_blind.py已支持r1及r4/r5各自契约，r2/r3按各自旧协议复算。下一轮仍固定用户J20、旧新各五张，另开会话，不自动无限迭代。

## 验证与限制

21项运行检查通过，包括r4算术保持、r5图文呼应核心低分不能被高均分掩盖、缺项/N拒绝比较、公共页配对字段/配对标识拒绝。80组通用型号/家族/姿态基础编译通过；16组J20四参考配置最大281词，本轮候选五份实际提示最大280词、旧版295词，未超300词。十份实际提示逐字节复编译一致，输入哈希及匿名承诺一致，生成用compile_prompt.py与rules.json未在生成后修改；后续只完善文档、报告和页面呈现校验。

Ego Lite 2.2.1验证十张图片加载、A–J切换。1280×800、1024×768、800×600、390×844均左图右分、五项同屏、页面和评分列无溢出。r5长说明已移入标准弹窗，量表文本本身未改变。隔离QA验证50项选择、刷新保分、仅A–J复制、N、缺分阻止、剪贴板回退；正式页0/50，未预填，QA不能当人工评分。临时QA页在收尾删除，截图与验证回执本地留存。

技能工坊validate_skill通过且无警告；OpenAI打包及ZIP完整性/字节一致性/隐私排除检查通过。未提供registry audit，元数据与registry一致性检查跳过，已记录。未运行工坊整个ci-test，本轮未修改工坊代码，不声称其既有CI问题已解决。

missing evidence：本轮50项真实评分、重复采样、独立机绣审查与真实生产打样。结论仅覆盖五个J20设计概念，不宣称泛化、统计显著或生产可行性。

## 安装、提交与交接

Skills Manager按既有本地source_ref检查并update，refreshed=true；中心库和现有Codex已同步1.1.5，运行文件/模板/代码ZIP与源码一致。原始lyz-aircraft-embroidery源码、库、Codex逐文件SHA-256均未变，仅忽略解释器缓存。

实现提交fc1e1e288ad87a19ff10680cb2558fad1739767b，已实际推送origin/main。首次推送TLS连接中断，重试同一提交后成功，未改连接验证或重写历史。只上传通用代码、空模板、文档和代码ZIP；实际图片、用户图、总览、原始评分、协议、提示、版本映射与私有快照均Git忽略。ZIP排除HANDOFF，避免包含旧交接。

本交接在实现推送后单独提交并推送；自身SHA用`git log -1 --format=%H -- lyz-aircraft-embroidery-v1-1/HANDOFF.md`读取，避免自引用。最终SHA与实际推送结果在回复和本地closure.json核验；交接还需经Skills Manager同步到库与Codex。

常用命令在技能目录执行：

```bash
python3 scripts/compile_prompt.py assets/example-brief.json --out output/my-job
python3 -m unittest discover -s evals -p 'test_*.py' -v
python3 scripts/build_scoreboard.py review-data.json --out index.html
python3 scripts/score_blind.py ratings.json --key /absolute/local/private/key.json --out comparison.json
```

最后一条只在完整真实评分和匿名承诺核对后使用。试用安装、技术检查与代码推送都不等于用户接受。
