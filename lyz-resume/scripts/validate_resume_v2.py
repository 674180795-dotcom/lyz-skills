#!/usr/bin/env python3
"""Validate v2 resume content, design contract, HTML, and optional PDF."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DESIGN_SYSTEM = json.loads((ROOT / "assets" / "design-archetypes.json").read_text(encoding="utf-8"))
ALLOWED_EVIDENCE = {"source_resume", "user_confirmed", "repository_verified", "document_verified", "conservative_estimate"}
ALLOWED_SECTIONS = ("education", "experience", "projects", "skills", "awards")
DATE_RE = re.compile(r"^(\d{4})[.\-/](\d{1,2})$")
PLACEHOLDER_RE = re.compile(r"(?:待补充|待确认|待填写|示例文本|你的名字|XXX|TBD|TODO|\bN/?A\b|lorem ipsum)", re.IGNORECASE)
WEAK_OPENING_RE = re.compile(r"^(?:主要)?(?:负责|参与|协助|熟悉|了解|学习|帮助)|^(?:responsible for|helped|assisted with|familiar with)\b", re.IGNORECASE)
RESULT_SIGNAL_RE = re.compile(r"(?:\d|%|上线|交付|验收|部署|发布|完成|实现|覆盖|测试|验证|采用|解决|降低|减少|提升|提高|缩短|节省|获奖|deployed|launched|delivered|shipped|tested|validated|reduced|increased|improved|completed|implemented|resolved)", re.IGNORECASE)
SUMMARY_CLICHE_RE = re.compile(r"(?:学习能力强|责任心强|沟通能力强|团队合作精神|热爱技术|积极主动|hard[- ]working|team player|fast learner)", re.IGNORECASE)
ESTIMATE_MARKER_RE = re.compile(r"(?:约|大约|近|超过|不少于|~|≈|\d+\s*[-–—]\s*\d+)")


def nonempty(value: Any) -> bool:
    return bool(str(value or "").strip())


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def date_value(raw: Any) -> tuple[int, int] | None:
    match = DATE_RE.match(str(raw or "").strip())
    if not match:
        return None
    year, month = int(match.group(1)), int(match.group(2))
    return (year, month) if 1 <= month <= 12 else None


def collect_texts(data: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key not in {"source_note", "targeting"}:
                texts.extend(collect_texts(value))
    elif isinstance(data, list):
        for value in data:
            texts.extend(collect_texts(value))
    elif isinstance(data, str):
        texts.append(data)
    return texts


def validate_data(data: dict[str, Any]) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"education": 0, "experience": 0, "projects": 0, "skills": 0, "bullets": 0, "result_bullets": 0, "weak_openings": 0}
    if data.get("version") != 2:
        errors.append("v2 验证器要求 version=2")
    if data.get("language") not in {"zh-CN", "en"}:
        errors.append("language 必须为 zh-CN 或 en")
    design = data.get("design") if isinstance(data.get("design"), dict) else {}
    layout, skin = str(design.get("layout", "")), str(design.get("skin", ""))
    density, profile = str(design.get("density", "")), str(design.get("render_profile", ""))
    if layout not in DESIGN_SYSTEM["layouts"]:
        errors.append("design.layout 无效")
    if skin != "auto" and skin not in DESIGN_SYSTEM["skins"]:
        errors.append("design.skin 无效")
    if density not in {"auto", "sparse", "balanced", "dense"}:
        errors.append("design.density 无效")
    if layout in DESIGN_SYSTEM["layouts"]:
        meta = DESIGN_SYSTEM["layouts"][layout]
        if profile not in meta["render_profiles"]:
            errors.append(f"{layout} 不支持 render_profile={profile}")
        if density != "auto" and density not in meta["capacity"]:
            errors.append(f"{layout} 不适合 density={density}")
    filename = str(data.get("filename", ""))
    if not filename or re.search(r"[\\/:*?\"<>|]", filename):
        errors.append("filename 不能为空且不能包含非法字符")
    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    for label, value in (("目标岗位", target.get("role")), ("姓名", basics.get("name")), ("邮箱", basics.get("email"))):
        if not nonempty(value):
            errors.append(f"缺少{label}")
    email = str(basics.get("email", ""))
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("邮箱格式无效")
    for index, link in enumerate(basics.get("links", []) or [], 1):
        if not isinstance(link, dict) or not valid_url(str(link.get("url", ""))):
            errors.append(f"basics.links[{index}] URL 无效")
    photo = basics.get("photo") if isinstance(basics.get("photo"), dict) else {}
    decision = str(photo.get("decision", ""))
    if decision not in {"provided", "declined"}:
        errors.append("必须记录证件照决定：provided 或 declined")
    if photo.get("enabled") is True:
        if decision != "provided":
            errors.append("启用照片时 decision 必须为 provided")
        if layout in DESIGN_SYSTEM["layouts"] and not DESIGN_SYSTEM["layouts"][layout]["supports_photo"]:
            errors.append(f"{layout} 不支持照片")
        source = str(photo.get("source", "")).strip()
        if not source or source.startswith(("http://", "https://", "data:")):
            errors.append("照片必须是本地文件")
    elif decision == "provided":
        errors.append("decision=provided 时必须启用照片")
    elif decision == "declined" and photo.get("enabled") is not False:
        errors.append("明确不使用照片时 enabled 必须为 false")
    section_order = data.get("section_order")
    if section_order is not None:
        if not isinstance(section_order, list) or len(section_order) != len(set(section_order)):
            errors.append("section_order 必须是无重复数组")
        elif any(value not in ALLOWED_SECTIONS for value in section_order):
            errors.append("section_order 包含未知章节")
    for section in ("education", "experience", "projects", "skills"):
        value = data.get(section, [])
        if not isinstance(value, list):
            errors.append(f"{section} 必须是数组")
        else:
            counts[section] = len(value)
    if counts["experience"] + counts["projects"] == 0:
        errors.append("至少需要一条实践经历或项目经历")
    targeting = data.get("targeting") if isinstance(data.get("targeting"), dict) else {}
    if not nonempty(targeting.get("role_thesis")):
        errors.append("targeting.role_thesis 不能为空")
    if not targeting.get("priority_requirement_ids"):
        errors.append("targeting 至少需要一个 priority_requirement_id")
    included_declared = {str(value) for value in targeting.get("included_evidence_ids", []) or []}
    omitted_declared = {str(value) for value in targeting.get("omitted_evidence_ids", []) or []}
    if included_declared & omitted_declared:
        errors.append("included_evidence_ids 与 omitted_evidence_ids 不得重叠")
    observed_ids: set[str] = set()
    for section in ("experience", "projects"):
        for item_index, item in enumerate(data.get(section, []) or [], 1):
            if not isinstance(item, dict):
                errors.append(f"{section}[{item_index}] 必须是对象")
                continue
            item_ids = {str(value) for value in item.get("evidence_ids", []) or [] if str(value).strip()}
            observed_ids.update(item_ids)
            if not item_ids:
                errors.append(f"{section}[{item_index}] 缺少 evidence_ids")
            if item.get("priority") not in {"core", "supporting", "brief"}:
                errors.append(f"{section}[{item_index}] priority 无效")
            start, raw_end = date_value(item.get("start")), str(item.get("end", "")).strip()
            end = date_value(raw_end)
            if item.get("start") and not start:
                errors.append(f"{section}[{item_index}] 开始时间格式无效")
            if raw_end and raw_end.lower() not in {"至今", "present", "now"} and not end:
                errors.append(f"{section}[{item_index}] 结束时间格式无效")
            if start and end and start > end:
                errors.append(f"{section}[{item_index}] 时间线倒置")
            bullets = item.get("bullets", [])
            if not isinstance(bullets, list) or not 1 <= len(bullets) <= 5:
                errors.append(f"{section}[{item_index}] 必须包含 1–5 条 bullets")
                continue
            if item.get("priority") == "brief" and len(bullets) > 1:
                errors.append(f"{section}[{item_index}] 为 brief，不得超过一条 bullet")
            for bullet_index, bullet in enumerate(bullets, 1):
                counts["bullets"] += 1
                path = f"{section}[{item_index}].bullets[{bullet_index}]"
                if not isinstance(bullet, dict):
                    errors.append(f"{path} 必须是对象")
                    continue
                text = str(bullet.get("text", "")).strip()
                evidence = str(bullet.get("evidence_type", ""))
                if len(text) < 12:
                    errors.append(f"{path}.text 过短")
                if WEAK_OPENING_RE.search(text):
                    counts["weak_openings"] += 1; warnings.append(f"{path} 以弱职责词开头")
                if RESULT_SIGNAL_RE.search(text):
                    counts["result_bullets"] += 1
                if evidence not in ALLOWED_EVIDENCE:
                    errors.append(f"{path}.evidence_type 无效")
                if not nonempty(bullet.get("source_note")):
                    warnings.append(f"{path} 缺少私下复核备注")
                if evidence == "conservative_estimate" and not ESTIMATE_MARKER_RE.search(text):
                    errors.append(f"{path} 的保守估算缺少约数标记")
    if observed_ids != included_declared:
        errors.append("targeting.included_evidence_ids 与成稿条目不一致")
    if observed_ids & omitted_declared:
        errors.append("omitted_evidence_ids 仍出现在成稿")
    if SUMMARY_CLICHE_RE.search(str(basics.get("summary", ""))):
        warnings.append("summary 包含空泛自我评价")
    if any(PLACEHOLDER_RE.search(text) for text in collect_texts(data)):
        errors.append("公开内容中发现占位符或未确认字段")
    if counts["bullets"] and counts["result_bullets"] * 2 < counts["bullets"]:
        warnings.append("超过一半的 bullet 缺少结果、验证、范围或交付信号")
    return errors, warnings, counts


def inspect_html(path: Path, expected_design: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {"file": path.name, "bytes": path.stat().st_size if path.is_file() else 0}
    if not path.is_file():
        return ["HTML 文件不存在"], warnings, facts
    text = path.read_text(encoding="utf-8", errors="replace")
    layout = str(expected_design.get("layout", "")); skin = str(expected_design.get("skin", ""))
    if skin == "auto" and layout in DESIGN_SYSTEM["layouts"]:
        skin = DESIGN_SYSTEM["layouts"][layout]["recommended_skins"][0]
    for marker, value in (("data-layout", layout), ("data-skin", skin)):
        if f'{marker}="{value}"' not in text:
            errors.append(f"HTML {marker} 与预期不符")
    if '<meta name="resume-layout-system" content="archetype-skin-density-3.0">' not in text:
        errors.append("HTML 缺少 3.0 布局系统标记")
    expected_dom = {"asymmetric-left-sidebar": "resume-left-sidebar", "sidebar-left-hero": "resume-sidebar-hero", "hero-header-blocks": "resume-hero-blocks", "hero-header-linear": "resume-hero-linear", "asymmetric-right-sidebar": "resume-right-sidebar", "banner-accent-flow": "resume-banner"}.get(layout)
    if expected_dom and expected_dom not in text:
        errors.append(f"HTML 缺少 {layout} 的独立 DOM 标记")
    if re.search(r"@font-face\s*\{[^}]*https?://", text, re.IGNORECASE | re.DOTALL):
        errors.append("HTML 不得依赖远程字体")
    if re.search(r'<img[^>]+src=["\']https?://', text, re.IGNORECASE):
        errors.append("HTML 不得依赖远程图片")
    if re.search(r"(?:file://|/Users/|[A-Za-z]:\\\\)", text):
        errors.append("HTML 暴露绝对本地路径")
    if re.search(r"\d+(?:\.\d+)?px\b", text, re.IGNORECASE):
        errors.append("打印 CSS 不得使用 px 尺寸")
    if re.search(r"border-radius\s*:", text, re.IGNORECASE):
        errors.append("HTML 使用了未获设计系统支持的圆角")
    if layout != "banner-accent-flow" and re.search(r"border-left\s*:", text, re.IGNORECASE):
        errors.append(f"{layout} 不应使用左侧装饰边框")
    facts.update({"layout": layout, "skin": skin, "density": re.search(r'data-density="([^"]+)"', text).group(1) if re.search(r'data-density="([^"]+)"', text) else "unknown", "distinct_dom": bool(expected_dom and expected_dom in text)})
    return errors, warnings, facts


def find_pdf_tool(name: str) -> str | None:
    direct = shutil.which(name)
    if direct:
        return direct
    anchor = shutil.which("pdfinfo") or shutil.which("pdftoppm")
    if anchor:
        for relative in ("../../native/poppler/bin", "../../native/poppler/poppler/bin"):
            candidate = (Path(anchor).resolve().parent / relative / name).resolve()
            if candidate.is_file():
                return str(candidate)
    return None


def inspect_pdf(path: Path, expected: list[str]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {"file": path.name, "bytes": path.stat().st_size if path.is_file() else 0}
    if not path.is_file() or path.read_bytes()[:5] != b"%PDF-":
        return ["PDF 文件不存在或无效"], warnings, facts
    pdfinfo = find_pdf_tool("pdfinfo")
    if pdfinfo:
        completed = subprocess.run([pdfinfo, str(path)], capture_output=True, text=True, check=False)
        pages = re.search(r"^Pages:\s+(\d+)", completed.stdout, re.MULTILINE)
        size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", completed.stdout, re.MULTILINE)
        if pages:
            facts["pages"] = int(pages.group(1))
            if not 1 <= facts["pages"] <= 2:
                errors.append("PDF 必须为 1–2 页")
        if size:
            width, height = float(size.group(1)), float(size.group(2)); facts["page_size_points"] = [width, height]
            if abs(width - 595.28) > 15 or abs(height - 841.89) > 15:
                errors.append("PDF 页面不是 A4")
    else:
        warnings.append("pdfinfo 不可用；页数和 A4 为 missing evidence")
    pdftotext = find_pdf_tool("pdftotext")
    if pdftotext:
        completed = subprocess.run([pdftotext, "-layout", str(path), "-"], capture_output=True, text=True, check=False)
        extracted = completed.stdout.strip(); facts["extracted_characters"] = len(extracted)
        if len(extracted) < 100:
            errors.append("PDF 文本提取失败或文本过少")
        normalized = re.sub(r"\s+", "", extracted)
        for value in expected:
            if value and re.sub(r"\s+", "", value) not in normalized:
                errors.append(f"PDF 文本中缺少关键字段：{value}")
    else:
        warnings.append("pdftotext 不可用；文本提取为 missing evidence")
    return errors, warnings, facts


def main() -> None:
    parser = argparse.ArgumentParser(description="检查 v2 简历数据与可选 HTML/PDF 产物。")
    parser.add_argument("input"); parser.add_argument("--html"); parser.add_argument("--pdf"); parser.add_argument("--output", "-o")
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON 根节点必须是对象")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    errors, warnings, counts = validate_data(data)
    html_facts = pdf_facts = None
    if args.html:
        item_errors, item_warnings, html_facts = inspect_html(Path(args.html).expanduser().resolve(), data.get("design") or {})
        errors.extend(item_errors); warnings.extend(item_warnings)
    if args.pdf:
        basics = data.get("basics") or {}; target = data.get("target") or {}
        item_errors, item_warnings, pdf_facts = inspect_pdf(Path(args.pdf).expanduser().resolve(), [str(basics.get("name", "")), str(basics.get("email", "")), str(target.get("role", ""))])
        errors.extend(item_errors); warnings.extend(item_warnings)
    report = {"ok": not errors, "input": input_path.name, "counts": counts, "html": html_facts, "pdf": pdf_facts, "errors": errors, "warnings": warnings, "evidence_boundary": "deterministic structure/runtime checks only; page images still require visual inspection"}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser().resolve(); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
