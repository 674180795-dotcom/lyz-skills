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
