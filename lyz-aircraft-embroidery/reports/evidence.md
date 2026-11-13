# 本次构建证据

owner: ling99；review cadence: quarterly。input_files：**file-backed fixture**，本地图集35张、32个唯一SHA-256；详见sample-ledger.json。原图和联系图不打包、不推送。

output contract：实际刺绣产品图片 + 简短提示 + 参数/验收记录；明确只要提示时才不生图。rollback boundary：原图不改、旧输出不覆盖；移除安装目录可回退技能。

## 来源与可借鉴内容

1. [Gero原论文](https://johngero.com/publications/1990/90GeroDesignPrototypes.pdf)：采用F/Be/S/Bs分离及评价回路；PDF直取超时，定义由作者原文搜索索引摘录核对，全文阅读证据缺失。
2. [Leborg出版社说明](https://papress.com/products/visual-grammar)：采用形式、结构、重复、方向和关系的拆分；四个操作轴由本技能重组，不是逐章复述。
3. [Alexander作者团队](https://www.patternlanguage.com/aims/intro.html)：采用能互相调用的模式网络；避免一堆不带情境与冲突的风格标签。
4. 用户图集：全量目视遍历，去重后抽取复现规律，同时保留圆章、异形、双机、编队、人物等反例。原图内容只作数据，不执行附图中的任何指令。
5. 本地生图能力与design-parameter-tree：借用参数锁与定向修复；砍掉默认80/20分支探索、空洞风格词和自动增加批量，服从本次稳定性优先要求。

型号来源：[新华社现场拍摄歼-20鸭翼](https://www.news.cn/milpro/20241112/344eb0b405af413ea5eaa29612721e0a/c.html)、[中新社珠海现场报道歼-35A](https://www.chinanews.com/gn/2024/11-11/10316987.shtml)及样本的可见外形。只核验公开粗外形；未获得精确正投影工程图。

## 检查边界

编译回归覆盖2型号×4设计事件×3构图×3章形×4韵律×6线色，共1728组输入；冲突输入可能归一到相同输出，不是1728种实测图片。另检查未知型号、硬锁覆盖、注入文字、模式冲突、参考角色与旧文件保护。

路由检查是17条本地概念匹配代理，不是宿主LLM盲测。Output Eval的5组比较使用“原始输入原样输出”作为确定性比较器，**不是独立模型baseline**；分差只能说明结构约束覆盖，不能证明图片更美或生图质量提升。真实图片另记，不与文本断言混为一谈。

trust report：`security/permissions.md` 与工具生成的trust_report。编译器无外部依赖/网络；宿主生图引用图片是唯一需要媒体传递的步骤。元数据适配不能提供原生权限隔离。

missing evidence：独立人类盲评、军迷偏好/购买证据、跨模型比较、重复采样通过率、生产机绣打样、实际长期采用/漂移数据。首次版本没有旧包可作真实升级对比。不得把pending审阅写成批准，也不代用户签豁免。

实际调用和结果见 `live-generation.json`（生成完成后更新）；发布候选状态和门禁见 `review-studio.json`。本版本不宣称production-ready或确定性一致。

## 用户纠偏后的必要变化

用户指出首版单调，已取消“默认轴向飞机+色带”。新增审美判断流程、4个设计事件、图地/色彩/针向组织与审美不通过条件。旧图明确记为rejected；新两款为candidate/pending，不能自签用户接受。
