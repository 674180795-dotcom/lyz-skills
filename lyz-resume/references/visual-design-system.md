# 视觉原型与选择

视觉系统把页面拓扑、配色语言和信息密度分开。版式决定阅读动线，配色只负责识别与层级，二者可以自由组合。

```text
layout   页面拓扑与阅读动线
skin     字体、颜色、线条与强调方式
density  sparse / balanced / dense / auto
```

机器可读定义位于 `assets/design-archetypes.json`。其中的布局是基于用户模板研究提炼的原创结构；配色从参考 DOCX 的实际色值归纳而来，但不复制原始模板的文字、图形、图片、图标或字体资产。

## 六种保留布局

只允许使用以下六种布局。`classic-single-column` 与 `tabular-structured` 已退出可选列表；旧数据仅在渲染兼容层中迁移到最接近的保留布局。

| 布局 | 主要用途 | 限制 |
|---|---|---|
| `sidebar-left-hero` | 强定位、中等信息量、人工阅读 | 不作为 ATS-first 默认选择 |
| `asymmetric-left-sidebar` | 联系方式与技能快览 | 双栏文本顺序必须验证 |
| `asymmetric-right-sidebar` | 成果、技能和教育辅助面板 | 核心长文必须留在主栏 |
| `hero-header-linear` | 中高级候选人、一至两页线性深读 | Hero 占用纵向空间；高密内容需控制摘要 |
| `hero-header-blocks` | 稀疏或模块化内容 | 高密内容容易拥挤 |
| `banner-accent-flow` | 应届、实习、内容较少 | 装饰不能代替事实 |

六种布局都支持用户提供的本地证件照。照片只是排版资产，不用于推断个人信息。

## 配色库

所有配色都可以与六种布局组合。`brand` 是主色，`accent` 是小面积强调色；不得为了“更丰富”同时加入第三种高饱和强调色。

| skin | 中文名 | 主色 / 强调色 | 来源 |
|---|---|---|---|
| `classic-navy` | 经典海军蓝 | `#203E5A` / `#B28B4B` | 原有稳健商务色 |
| `editorial-ink` | 编辑式墨色 | `#253B59` / `#9A7650` | 原有纸感编辑色 |
| `temple-blue` | 天宫蓝金 | `#1C487C` / `#C19F67` | 天宫蓝色版参考 |
| `dusty-rose` | 雾粉玫瑰 | `#953735` / `#D99694` | 粉色版参考 |
| `navy-gold` | 深蓝金 | `#17375E` / `#CE9B00` | 蓝金色版参考 |
| `powder-blue` | 淡雅浅蓝 | `#1F497D` / `#7EA0C3` | 淡蓝色系列参考 |
| `azure-blue` | 明快亮蓝 | `#0070C0` / `#32AEFE` | 简约蓝与极简蓝参考 |
| `fresh-lime` | 清新青柠 | `#5E8F2E` / `#92D050` | 清新简约系列参考 |
| `sage-mint` | 鼠尾草薄荷 | `#4F8871` / `#94C9AF` | 淡雅绿色系列参考 |
| `charcoal` | 现代炭灰 | `#404040` / `#A6A6A6` | 现代黑系列参考 |
| `modern-red` | 现代赤红 | `#CB4546` / `#C00000` | 红色系列参考 |
| `campus-green` | 校园青绿 | `#176A58` / `#BFA666` | 原有校园色与参考金色 |

## 自动选择与自由组合

新文件推荐使用：

```json
"design": {
  "layout": "hero-header-linear",
  "skin": "auto",
  "density": "auto",
  "render_profile": "balanced"
}
```

`skin: auto` 会读取布局的 `recommended_skins`，使用首选色。六布局对比模式会为不同布局自动选择不同的首选配色，不再把同一颜色机械套到全部页面。用户明确指定 `--skin` 时，则按要求让所有候选版式使用同一配色，便于只比较结构。

默认首选组合：

- `sidebar-left-hero` → `temple-blue`
- `asymmetric-left-sidebar` → `powder-blue`
- `asymmetric-right-sidebar` → `sage-mint`
- `hero-header-linear` → `navy-gold`
- `hero-header-blocks` → `dusty-rose`
- `banner-accent-flow` → `modern-red`

选择 `render_profile` 时：

- `ats-first`：只推荐阅读顺序最直接的 `hero-header-linear`，并实际验证 PDF 文本提取；
- `balanced`：可使用线性 Hero、轻条幅或左右辅助栏；
- `human-first`：可使用全部六种布局，但仍须满足 A4、可读字号和文本可提取。

选择密度时：

- `sparse`：扩大留白和字号，优先条幅、色块或辅助栏；
- `balanced`：大多数单页简历；
- `dense`：使用 `hero-header-linear`，必要时改为两页；
- `auto`：由渲染器按可见字符、条目数、bullet 数和章节数决定。

用户未指定风格时只输出一个推荐版本。用户明确要求比较时，最多选择三种拓扑差异明显的布局；`--all-layouts` 只用于内部验收或用户明确要求查看全部六种版式。

## 兼容层

旧版 `theme` 继续可用，但映射到六种保留布局。旧的 `classic-single-column` 数据迁移到 `hero-header-linear`，旧的 `tabular-structured` 数据迁移到 `asymmetric-right-sidebar`；它们不再出现在新文件的选项中。

## 视觉验收

每次生成后检查：

1. 页面是否 A4、1–2 页；
2. 正文是否不低于 9.1pt；
3. 姓名、联系方式、章节、日期和 bullet 是否有清楚层级；
4. 是否存在裁切、重叠、孤行、异常断页或大片无意义空白；
5. 双栏 PDF 的文本提取顺序是否仍可理解；
6. 主色、强调色和正文对比度是否清楚，黑白打印是否仍可辨认；
7. HTML 是否无远程字体、远程图片和绝对本地路径。

“好看”必须建立在内容主次、阅读动线和可投递性之上。不要承诺 ATS 分数，也不要把任意双栏结构描述为绝对 ATS 友好。
