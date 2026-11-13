# 视觉语法与FBS

Gero的FBS区分功能F、预期行为Be、结构导出的行为Bs、结构S。这里把B操作化为可观察的视觉效应，用实际生图近似分析Bs；这是领域改写，原理论并不只讨论视觉，也不支持从F跳过行为直接拼风格词。[原论文](https://johngero.com/publications/1990/90GeroDesignPrototypes.pdf)；[作者索引](https://www.johngero.com/research/ontologies.html)。本次PDF直取超时，定义经作者原文搜索索引摘录核对，未声称逐页阅读全文。

Leborg以抽象/具象对象与结构、活动、关系组织视觉概念。以下四轴是对其形式、表面、重复、方向与图地关系的应用重组，不是书的原始四章。[出版社](https://papress.com/products/visual-grammar)。Alexander的模式语言是互相调用的模式网络；本库采用情境—问题—张力—解决—结果—关联，额外加入编译约束，并不声称书中已有刺绣定律。[作者团队](https://www.patternlanguage.com/aims/intro.html)。

| 轴 | Leborg概念锚点 | 独立参数 | 保留 | 剥离 |
|---|---|---|---|---|
| 形态M | form/size/direction | 章形、主体投影、占比、层数 | 封闭容器、清晰负空间 | 具体机型/舰形/人物、品牌排布 |
| 肌理T | concrete structure/surface | 填针方向、轮廓针、绣边、光泽 | 可见线股、分区方向反射 | 印刷渐变、PVC/珐琅/金属联想 |
| 韵律R | repetition/movement/variation | none/parallel/arc/grid单选 | 疏密与曲直对比 | 火焰、雷电、豹、山、地图等原题材 |
| 边界E | enclosure/contact/relations | 闭合、边宽、安全内缩 | 连续包边、不切主体 | 原标识外轮廓、发光描边 |

色彩C单独选线色；不把蓝色与网格、红色与战斗绑定。正交指参数责任单一，不声称知觉统计独立。文字区与主体占比等关联必须显式检查。针法名是视觉近似，效果图无法证明实物工艺。

设计初值：主体约内宽65–78%，绣边约章宽3%，完整章距画面边缘≥8%，背景线不穿识别点。这些不是逐像素实测，也不是生产针距/毫米公差。

## FBS双向词表

受众痛点来自军迷定位、产品用途和图集的设计推断，未经访谈或销量验证。完整机器版在`assets/rules.json`。

| F需求 | Be预期视觉行为 | S正向词/参数 | 反向词 | 权重 | Bs观察 |
|---|---|---|---|---|---|
| 型号认同 | 不看字也辨机型 | 3–6个型号识别点 | hybrid aircraft, wrong wing/tail layout | 5 | 对照翼形、翼面位置、尾翼与发动机布局 |
| 刺绣真实 | 像线绣成 | directional thread fill, satin-stitched contours, raised stitched edge | printed fabric, enamel, molded plastic | 5 | 线股、针向、绣边可见 |
| 缩小可读 | 主体先被看到 | one dominant aircraft, clear figure-ground separation | competing motifs, busy scenery | 4 | 约200px剪影连续 |
| 系列收藏 | 同系列底盘统一 | closed badge, limited thread palette | unrelated borders, random colors | 4 | 线色/绣边/摄影一致 |
| 速度感 | 方向明确 | sparse directional bands | trails crossing identification features | 3 | 背景不遮机体 |
| 小字可靠 | 必要且清楚 | single short model label（可选） | gibberish, extra slogans | 3 | 逐字核对 |
| 原创性 | 不复刻专有组合 | new arrangement from abstract atoms | copied logo, copied mascot | 4 | 无原品牌/口号/意象组合 |
| 展示清楚 | 全章可见 | complete isolated product, soft side light | cropped rim, prop scene | 2 | 全轮廓/阴影可读 |

1=可删点缀，2=展示辅助，3=可选表达，4=关键行为，5=硬锁。型号在所有5分项中仍最优先。不是审美测量分数，不允许加权平均后用漂亮抵消错机型。

## 观察与反例

六边形、封闭绣边、分区针向反复出现。S06/S09有圆章，S04/S11–15有三角/异形和套装，所以六边只是默认。S17/S22为双机、S05有编队、S08是人物；单机是本技能为稳定性主动缩窄，不能谎称样本全为单机。S01/S02是场景营销图，白底来自S17–31单品，不能把海报背景当针线。
