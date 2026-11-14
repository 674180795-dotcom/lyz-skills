# 1.1.2 开源借鉴记录

2026-11-14通过agent-reach的GitHub CLI搜索并阅读公开项目一手README及示例，未安装、执行或复制这些项目的模型代码。以下是工作流借鉴，不能说内置image_gen已运行Adapter、ControlNet、mask或特征解耦。

| 一手项目 | 本次核对版本/材料 | 可借鉴的关系 | 本包实际落地 |
|---|---|---|---|
| [IP-Adapter](https://github.com/tencent-ailab/IP-Adapter) | 62e4af9，README的图像提示和结构控制示例 | 图像条件与文字条件分工；结构控制单独存在 | 让主参考先作为视觉内容锚，文字只规定改动及型号锁 |
| [ComfyUI IPAdapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus/blob/a0f451a5113cf9becb0847b92884cb10cbdec0ef/examples/ipadapter_style_composition.json) | a0f451a，实际StyleComposition示例的image_style/image_composition输入 | 风格和构图分别进入工作流 | geometry保主体与空间；series只借指定颜色/背景区域，并列出不能借的异型号内容 |
| [InstantStyle-Plus](https://github.com/instantX-research/InstantStyle-Plus/tree/11b2d96e0af6290b5ee503f8b85da3eeefe52732) | 11b2d96，README | 风格注入、空间保留、语义内容保留分开处理 | 提示分成内容/空间锚、风格借用、区域针线三层，保参考中的平面飞机而非重新建模 |
| [Ink/Stitch](https://github.com/inkstitch/inkstitch/tree/42e771e9d4338ce32a80f4d8c0df186a8c8210e7) | 42e771e，README和lib/elements中的fill_stitch、satin_column、stroke模块分类 | SVG图形组织与针线元素有明确区分 | 飞机面用方向填针，底纹用更安静的填针，字形/窄边才用缎面针；不交付针版或承诺生产可行性 |

本轮主要问题仍是系列转译。上一轮完整人工评分未通过，结构均分有所改善但系列转译未改善；不外传原始分数及版本映射。新的假设是：先保主参考的平面图形，再把风格借用限制在明确区域，会比通用的“画一架某型号刺绣飞机”更接近系列。该假设需要新首图及人工评分验证。

不借用项目的默认权重、seed或采样参数，不把真实架构能力伪装成提示词能力。本轮仍只用当前内置image_gen；若单靠视觉参考无法稳定保形，记录能力缺口，不偷偷切换外部模型或付费API。

## 1.1.3 适用性修正

用户明确否定复刻方向。上文的内容/空间锚属于1.1.2历史，不再执行。图像内容保持方法不能替代产品扩款目标。新查阅的google/style-aligned在同一风格下生成不同主体，其实际notebook示例及版本记录见design-expansion.md；本版借鉴主体与系列语言分开设计的思路，未执行共享注意力或外部模型。

## 1.1.4：结构与系列分工

2026-11-14再次通过agent-reach GitHub CLI搜索并核对一手README：

- [InstantStyle，6b40588](https://github.com/instantX-research/InstantStyle/tree/6b40588e263c958653353ec24eb7eb990cfa3da7)明确区分内容与风格，并讨论减少内容泄漏。本技能借鉴为“系列参考只提供色块、材质与文字重量，不能借飞机或整幅布局”。
- [ControlNet，ed85cd1](https://github.com/lllyasviel/ControlNet/tree/ed85cd1e25a5ed592f7d8178495b4483de0331bf)以额外条件控制生成，展示边缘/线段等结构输入。本技能借鉴为独立结构辅助图与数量/前后顺序约束，不能称为已运行ControlNet或拥有硬结构控制。

本轮两版收到完全相同的粗布局示意与两张系列参考，示意来自已记录的外形卡，标明不按比例，只核对数量与顺序。新版显式枚举水平翼面对数、垂尾与尾喷口数，连续横排型号字以减少拆字；构图、背景、配色关系与留白仍独立设计。只用当前内置image_gen，未安装、执行或复制这些项目的模型实现。是否改善须由十图人工盲测判断；结构示意可能带入颜色或形态，是待观察的输入偏差，不是几何认证。

## 1.1.5：全库与刺绣简化

2026-11-15使用agent-reach GitHub CLI重新搜索Ink/Stitch，并读取42e771e9d4338ce32a80f4d8c0df186a8c8210e7的一手README（SVG基础的机绣设计平台）。实际借鉴限于将图形组织与针线处理分开：保机体原样、归并细节为宽色区、字形与背景共享几何关系；没有运行软件、生成针版或认证参数。用户要求的图文呼应主要来自对其全库作品的重新分析，不假装开源架构能替代审美设计。全库与关系规则见design-expansion.md。
