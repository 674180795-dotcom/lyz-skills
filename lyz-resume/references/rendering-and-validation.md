# 渲染与验收

以下命令中的 `SKILL_DIR` 是本 Skill 目录，先在当前 shell 设置为包含 `SKILL.md` 的绝对路径。输出写进用户的独立工作目录，不覆盖源文件。

## 1. 提取旧简历

```bash
python3 "$SKILL_DIR/scripts/extract_resume.py" old-resume.pdf --output source-extract.txt
```

支持 PDF、DOCX、TXT、Markdown。扫描 PDF 或图片先征得用户同意，再使用本地 OCR/视觉能力；姓名、电话、邮箱、公司、职位、日期和数字必须复述确认。

## 2. 采集门禁

```bash
python3 "$SKILL_DIR/scripts/assess_intake.py" candidate-ledger.json --output intake-status.json
```

`blocked` 继续补一个阻断项；`workable` 可生成诚实版本；`strong` 表示证据覆盖充分。脚本只能检查完整性，不能证明用户陈述为真。

## 3. 岗位一致性与内容验证

```bash
python3 "$SKILL_DIR/scripts/validate_alignment.py" \
  role-analysis.json resume-plan.json resume-data.json \
  --output alignment-validation.json
python3 "$SKILL_DIR/scripts/validate_resume.py" resume-data.json --output validation-data.json
```

一致性验证必须先通过：计划纳入的证据都进入成稿，`omit` 证据不泄漏，核心证据在前，`brief` 与其他条目不超出 bullet 预算。

## 4. 渲染

```bash
python3 "$SKILL_DIR/scripts/render_resume.py" resume-data.json \
  --layout hero-header-linear \
  --skin auto \
  --density auto \
  --output-dir output
```

布局与选择规则见 [视觉原型与选择](visual-design-system.md)。旧版 `--theme` 仍可用于 v1 文件；新版优先使用 `--layout / --skin / --density / --render-profile`。内部验收六种保留布局时可运行 `--all-layouts`，此时未指定 `--skin` 会使用各布局的推荐色；普通用户默认只生成一个推荐版本。

最终渲染前必须先提醒用户上传证件照或明确选择不使用。提供照片时，在 `basics.photo` 中设置 `decision: provided`、`enabled: true` 与本地 `source`；拒绝时设置 `decision: declined`、`enabled: false`。渲染器把图片嵌入 HTML，最终文件不依赖绝对本地路径。

## 5. 文件验证

```bash
python3 "$SKILL_DIR/scripts/validate_resume.py" resume-data.json \
  --html output/resume.html \
  --pdf output/resume.pdf \
  --output output/validation.json
```

必须核对：

- A4、1–2 页、未加密；
- 姓名、邮箱和标准章节可从 PDF 提取；
- HTML 与 PDF 来自同一 JSON；
- 无占位符、远程字体、远程图片或渲染出的私人 `source_note`；
- 时间线、链接、证据类型和章节顺序有效。

## 6. 视觉闭环

```bash
python3 "$SKILL_DIR/scripts/pdf_to_images.py" output/resume.pdf --output-dir output/pages
```

必须逐页实际查看 PNG，检查：裁切、重叠、孤行、异常换行、层级不清、段落过密、大片空白、头像变形和页尾断裂。机器检查不能代替这一步。

## Page-fit 修复顺序

1. 删除弱相关、重复或无证据内容；
2. 合并重复 bullet，缩短长句；
3. 调整章节顺序和适度间距；
4. 将 `density` 切换为 `dense`，但正文不得低于 9.1pt；
5. 切换兼容高密内容的布局或使用两页。

正文不得低于 9.1pt。不要为“一页”牺牲可读性，也不要把两页本身当成失败。
