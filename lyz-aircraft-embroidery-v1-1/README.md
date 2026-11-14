# 航空刺绣设计 1.1.3

独立标识lyz-aircraft-embroidery-v1-1，原版lyz-aircraft-embroidery不变。

本技能设计同系列的原创扩款：选择其他型号，从多款样本提炼平面省略、色块、字形层级与针线语言，为新飞机重新设计构图、背景关系和文字。1.1.2把整幅参考当内容/空间锚，偏向复刻，已被用户否定并撤回。

先读[扩款规则](references/design-expansion.md)和[执行规则](references/workflow.md)。默认J-10C；内置J-20、J-35A、J-10C、J-15、通用J-7粗外形卡，不认证精确比例或具体批次。用户未指定型号时，优先选择本批series参考中没有的型号。

brief的design_plan需有composition、motif、lettering三个独立选择。最多一张目标geometry和三张series，series可跨型号多张；没有同型号成品章也可根据外形卡设计，不必找一张来复刻。参考字段均为path/role/aircraft，不能将重复文件充当多个来源。

```bash
python3 scripts/compile_prompt.py assets/example-brief.json --out output/my-job
python3 -m unittest discover -s evals -p 'test_*.py' -v
python3 scripts/build_scoreboard.py review-data.json --out index.html
```

编译器只做离线计划，实际由宿主调用内置image_gen。没有工具则说明未生图，不暗换外部模型或付费API。

1.1.0、1.1.1、1.1.2均已收到真实评分且未通过。本轮重新开r3，三款新型号单版验收，五项为型号结构、同系列感、新款原创度、整体审美、文字设计；前三项核心。不是旧新盲评，不宣称相对提升，旧分不回算。当前人工状态pending_human。

评分页限尺寸左图、右侧评分、原位切换，同屏看图打分。实际图、参考、分数、协议与执行材料只留本机，不进入Git或代码ZIP。安装候选和技术检查均不代表用户已接受。

维护者ling99；最长一季度及收到反馈/新增型号/工具接口变更时复核。只交产品效果图，不交生产针版，不认证工艺可行性，不做军事性能分析。
