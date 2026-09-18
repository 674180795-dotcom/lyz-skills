# 视觉原型与选择

视觉系统把“页面结构”“视觉语言”“信息密度”分开，避免把换色误认为新模板。

```text
layout   页面拓扑与阅读动线
skin     字体、颜色、线条与强调方式
density  sparse / balanced / dense / auto
```

机器可读定义位于 `assets/design-archetypes.json`。该文件是从用户提供的 172 份模板研究中提炼出的原创结构规范，不包含原始 DOCX、图片、图标或字体资产。

## 八种布局

| 布局 | 主要用途 | 限制 |
|---|---|---|
| `classic-single-column` | 稳定阅读顺序、正式投递、内容较多 | 视觉表现克制 |
| `asymmetric-left-sidebar` | 联系方式与技能快览 | 双栏阅读顺序需验证 |
| `sidebar-left-hero` | 强定位、人工阅读 | 不用于 ATS-first 默认选择 |
| `hero-header-blocks` | 稀疏或模块化内容 | 高密内容容易拥挤 |
| `hero-header-linear` | 中高级、一至两页深读 | Hero 会占用纵向空间 |
| `asymmetric-right-sidebar` | 成果和技能辅助面板 | 辅助栏不得放核心长文 |
| `tabular-structured` | 传统字段对齐 | 不声称通用 ATS 友好，必须测文本顺序 |
| `banner-accent-flow` | 应届、实习、内容较少 | 装饰不能代替事实 |

## 自动选择

先判断 `render_profile`：

- `ats-first`：默认 `classic-single-column`；只有实际文本提取测试通过时才允许其他布局。
- `balanced`：根据内容密度选择单栏、线性 Hero、轻条幅或左右辅助栏。
- `human-first`：可以选择双栏和模块化布局，但仍需满足 A4、可读字号和文本可提取。

再判断密度：

- `sparse`：扩大留白和字号，优先条幅、色块或辅助栏；
- `balanced`：大多数单页简历；
- `dense`：优先单栏或线性流，必要时使用两页；
- `auto`：由渲染器按可见字符、条目数、bullet 数和章节数决定。

用户未指定风格时只输出一个推荐版本。用户明确要求比较时，最多选择三种拓扑差异明显的布局，不生成八套近似换色稿。

## 兼容层

旧版 `theme` 继续可用，但只作为兼容预设：

- `ats-classic / kami / swiss / tech` → 单栏布局与对应皮肤；
- `campus` → 轻条幅布局与清新皮肤；
- `compact` → 单栏布局与 `dense` 密度。

新文件使用：

```json
"design": {
  "layout": "classic-single-column",
  "skin": "classic-navy",
  "density": "auto",
  "render_profile": "balanced"
}
```

## 视觉验收

每次生成后检查：

1. 页面是否 A4、1–2 页；
2. 正文是否不低于 9.1pt；
3. 姓名、联系方式、章节、日期和 bullet 是否有清楚层级；
4. 是否存在裁切、重叠、孤行、异常断页或大片无意义空白；
5. 双栏和表格的 PDF 文本提取顺序是否仍可理解；
6. 色块打印是否保留，黑白打印是否仍可辨认；
7. HTML 是否无远程字体、远程图片和绝对本地路径。

“好看”必须建立在内容主次、阅读动线和可投递性之上。不要承诺 ATS 分数，也不要把任意表格或双栏结构描述为绝对 ATS 友好。
