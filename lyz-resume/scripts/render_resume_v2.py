#!/usr/bin/env python3
"""Render v2 resume data through distinct layout archetypes."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DESIGN_SYSTEM = json.loads((ROOT / "assets" / "design-archetypes.json").read_text(encoding="utf-8"))
LAYOUT_ORDER = tuple(DESIGN_SYSTEM["layouts"])
SKIN_ORDER = tuple(DESIGN_SYSTEM["skins"])
SKIN_CHOICES = ("auto",) + SKIN_ORDER
LEGACY_THEMES = tuple(DESIGN_SYSTEM["legacy_mapping"])
REFERENCE_STYLES = {
    "rc-003": {"label": "RC003 高密蓝线", "theme": "compact"},
    "rc-071": {"label": "RC071 深蓝极简", "theme": "ats-classic"},
    "rc-102": {"label": "RC102 章条商务", "theme": "tech"},
    "rc-109": {"label": "RC109 双语经典", "theme": "ats-classic"},
    "rc-150": {"label": "RC150 灰白机构", "theme": "ats-classic"},
    "rc-214": {"label": "RC214 天蓝时间序", "theme": "campus"},
}
REFERENCE_STYLE_ORDER = tuple(REFERENCE_STYLES)
DEFAULT_SECTION_ORDER = ("experience", "projects", "education", "skills", "awards")
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PHOTO_BYTES = 8 * 1024 * 1024
LABELS = {
    "zh-CN": {"education": "教育经历", "experience": "工作经历", "projects": "项目经历", "skills": "专业技能", "awards": "奖项与证书"},
    "en": {"education": "EDUCATION", "experience": "EXPERIENCE", "projects": "PROJECTS", "skills": "SKILLS", "awards": "AWARDS & CERTIFICATIONS"},
}
BILINGUAL_LABELS = {
    "education": "教育经历 · EDUCATION", "experience": "工作经历 · EXPERIENCE", "projects": "项目经历 · PROJECTS", "skills": "专业技能 · SKILLS", "awards": "奖项与证书 · AWARDS"
}


def esc(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=True)


def safe_url(raw: Any) -> str:
    value = str(raw or "").strip()
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https", "mailto"} else ""


def safe_basename(raw: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", "_", raw).strip(" ._")
    return cleaned[:96] or "resume"


def hydrate_photo(data: dict[str, Any], base_dir: Path) -> None:
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    photo = basics.get("photo") if isinstance(basics.get("photo"), dict) else {}
    if photo.get("enabled") is not True:
        return
    source = str(photo.get("source", "")).strip()
    if not source or source.startswith(("http://", "https://", "data:")):
        raise ValueError("照片必须是用户提供的本地文件")
    photo_path = Path(source).expanduser()
    if not photo_path.is_absolute():
        photo_path = base_dir / photo_path
    photo_path = photo_path.resolve()
    if not photo_path.is_file() or photo_path.suffix.lower() not in PHOTO_EXTENSIONS:
        raise ValueError("照片文件不存在或格式不受支持")
    if photo_path.stat().st_size > MAX_PHOTO_BYTES:
        raise ValueError("照片超过 8 MB，请先压缩")
    mime = mimetypes.guess_type(photo_path.name)[0] or "image/jpeg"
    photo["_data_uri"] = f"data:{mime};base64,{base64.b64encode(photo_path.read_bytes()).decode('ascii')}"
    photo["_alt"] = str(photo.get("alt") or basics.get("name") or "证件照")


def resolve_section_order(data: dict[str, Any]) -> list[str]:
    raw = data.get("section_order")
    requested = [str(value).strip() for value in raw or [] if str(value).strip() in DEFAULT_SECTION_ORDER] if isinstance(raw, list) else []
    ordered = list(dict.fromkeys(requested))
    ordered.extend(section for section in DEFAULT_SECTION_ORDER if section not in ordered)
    return ordered


def content_density(data: dict[str, Any]) -> str:
    entries = sum(len(data.get(section, []) or []) for section in ("education", "experience", "projects", "awards"))
    bullets = sum(len(item.get("bullets", []) or []) for section in ("experience", "projects") for item in data.get(section, []) or [] if isinstance(item, dict))
    text = "".join(str(value) for value in collect_visible_values(data))
    score = len(text) / 95 + bullets * 1.25 + entries * 1.1
    return "sparse" if score < 24 else "balanced" if score < 36 else "dense"


def collect_visible_values(value: Any) -> list[str]:
    output: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key not in {"source_note", "targeting", "evidence_ids", "requirement_ids"}:
                output.extend(collect_visible_values(item))
    elif isinstance(value, list):
        for item in value:
            output.extend(collect_visible_values(item))
    elif isinstance(value, str):
        output.append(value)
    return output


def resolve_design(
    data: dict[str, Any],
    *,
    layout: str | None = None,
    skin: str | None = None,
    density: str | None = None,
    render_profile: str | None = None,
    theme: str | None = None,
    reference_style: str | None = None,
) -> dict[str, str]:
    if reference_style:
        if reference_style not in REFERENCE_STYLES:
            raise ValueError(f"未知参考风格：{reference_style}")
        theme = REFERENCE_STYLES[reference_style]["theme"]
    raw = data.get("design") if isinstance(data.get("design"), dict) else {}
    legacy = str(theme or data.get("theme") or "").strip()
    inherited = DESIGN_SYSTEM["legacy_mapping"].get(legacy, {})
    requested_layout = str(layout or raw.get("layout") or inherited.get("layout") or "hero-header-linear")
    requested_layout = DESIGN_SYSTEM.get("retired_layout_mapping", {}).get(requested_layout, requested_layout)
    requested_skin = str(skin or raw.get("skin") or inherited.get("skin") or "auto")
    requested_skin = DESIGN_SYSTEM.get("retired_skin_mapping", {}).get(requested_skin, requested_skin)
    chosen = {
        "layout": requested_layout,
        "skin": requested_skin,
        "density": str(density or raw.get("density") or inherited.get("density") or "auto"),
        "render_profile": str(render_profile or raw.get("render_profile") or "balanced"),
    }
    if chosen["layout"] not in LAYOUT_ORDER:
        raise ValueError(f"未知布局：{chosen['layout']}")
    if chosen["skin"] == "auto":
        chosen["skin"] = DESIGN_SYSTEM["layouts"][chosen["layout"]]["recommended_skins"][0]
    if chosen["skin"] not in SKIN_ORDER:
        raise ValueError(f"未知皮肤：{chosen['skin']}")
    if chosen["density"] not in {"auto", "sparse", "balanced", "dense"}:
        raise ValueError(f"未知密度：{chosen['density']}")
    allowed_profiles = DESIGN_SYSTEM["layouts"][chosen["layout"]]["render_profiles"]
    if chosen["render_profile"] not in allowed_profiles:
        raise ValueError(f"{chosen['layout']} 不支持 {chosen['render_profile']}；可选：{', '.join(allowed_profiles)}")
    auto_density = chosen["density"] == "auto"
    if auto_density:
        chosen["density"] = content_density(data)
    allowed_density = DESIGN_SYSTEM["layouts"][chosen["layout"]]["capacity"]
    if chosen["density"] not in allowed_density:
        if auto_density:
            chosen["density"] = "balanced" if "balanced" in allowed_density else allowed_density[0]
        else:
            raise ValueError(f"{chosen['layout']} 不适合 {chosen['density']} 内容；可选：{', '.join(allowed_density)}")
    return chosen


def date_range(item: dict[str, Any]) -> str:
    start, end = str(item.get("start", "")).strip(), str(item.get("end", "")).strip()
    return f"{start}\u202f–\u202f{end}" if start and end else start or end


def render_contact(basics: dict[str, Any]) -> str:
    items: list[str] = []
    for field in ("phone", "email", "location"):
        if str(basics.get(field, "")).strip():
            items.append(f"<span>{esc(basics[field])}</span>")
    for link in basics.get("links", []) or []:
        if isinstance(link, dict) and safe_url(link.get("url")):
            items.append(f'<a href="{esc(link["url"])}">{esc(link.get("label") or link["url"])}</a>')
    return '<div class="contact">' + '<span class="dot">·</span>'.join(items) + "</div>"


def render_bullets(raw: Any) -> str:
    values = [esc(item.get("text")) if isinstance(item, dict) else esc(item) for item in raw or []]
    values = [value for value in values if value]
    return "<ul>" + "".join(f"<li>{value}</li>" for value in values) + "</ul>" if values else ""


def render_entry(item: dict[str, Any], *, project: bool = False) -> str:
    title = esc(item.get("organization") or item.get("name"))
    right = " · ".join(part for part in (esc(date_range(item)), esc(item.get("location"))) if part)
    subtitle = [esc(item.get("role"))] if str(item.get("role", "")).strip() else []
    tech = [esc(value) for value in item.get("tech", []) or [] if str(value).strip()]
    if tech:
        subtitle.append(" / ".join(tech))
    link = safe_url(item.get("link"))
    if link:
        subtitle.append(f'<a href="{esc(link)}">{esc(item.get("link_label") or "项目链接")}</a>')
    priority = str(item.get("priority") or "supporting")
    return f'''<article class="entry {'project' if project else 'work'} priority-{esc(priority)}">
      <div class="entry-head"><h3>{title}</h3><div class="entry-date">{right}</div></div>
      {f'<div class="entry-sub">{" · ".join(subtitle)}</div>' if subtitle else ''}
      {render_bullets(item.get("bullets"))}
    </article>'''


def render_education(item: dict[str, Any]) -> str:
    credential = " · ".join(part for part in (esc(item.get("degree")), esc(item.get("major"))) if part)
    right = " · ".join(part for part in (esc(date_range(item)), esc(item.get("location"))) if part)
    details = " · ".join(esc(value) for value in item.get("details", []) or [] if str(value).strip())
    return f'''<article class="entry education-item">
      <div class="entry-head"><h3>{esc(item.get("school"))}</h3><div class="entry-date">{right}</div></div>
      {f'<div class="entry-sub">{credential}</div>' if credential else ''}
      {f'<div class="edu-details">{details}</div>' if details else ''}
    </article>'''


def section_html(section: str, labels: dict[str, str], bodies: dict[str, str], extra: str = "") -> str:
    body = bodies.get(section, "")
    return f'<section class="section section-{section} {extra}"><h2 class="section-title">{esc(labels[section])}</h2>{body}</section>' if body.strip() else ""


def build_bodies(data: dict[str, Any]) -> dict[str, str]:
    skills: list[str] = []
    for group in data.get("skills", []) or []:
        if isinstance(group, dict):
            values = [esc(value) for value in group.get("items", []) or [] if str(value).strip()]
            if values:
                skills.append(f'<div class="skill-row"><strong>{esc(group.get("category"))}</strong><span>{" · ".join(values)}</span></div>')
    awards: list[str] = []
    for award in data.get("awards", []) or []:
        if isinstance(award, dict):
            detail = f" · {esc(award.get('detail'))}" if str(award.get("detail", "")).strip() else ""
            awards.append(f'<div class="award-row"><span><strong>{esc(award.get("name"))}</strong>{detail}</span><time>{esc(award.get("date"))}</time></div>')
    return {
        "education": "".join(render_education(item) for item in data.get("education", []) or [] if isinstance(item, dict)),
        "experience": "".join(render_entry(item) for item in data.get("experience", []) or [] if isinstance(item, dict)),
        "projects": "".join(render_entry(item, project=True) for item in data.get("projects", []) or [] if isinstance(item, dict)),
        "skills": "".join(skills),
        "awards": "".join(awards),
    }


def identity_content(basics: dict[str, Any], target: dict[str, Any], portrait: str, *, contact: bool = True, summary: bool = True) -> str:
    headline = esc(basics.get("headline") or target.get("role"))
    summary_text = esc(basics.get("summary"))
    return f'''<div class="identity{' has-photo' if portrait else ''}">
      <div class="identity-copy"><h1>{esc(basics.get("name"))}</h1>{f'<div class="headline">{headline}</div>' if headline else ''}</div>
      {render_contact(basics) if contact else ''}{portrait}
    </div>{f'<p class="summary">{summary_text}</p>' if summary and summary_text else ''}'''


def layout_markup(data: dict[str, Any], design: dict[str, str], portrait: str, labels: dict[str, str], bodies: dict[str, str]) -> str:
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    order = resolve_section_order(data)
    layout = design["layout"]
    all_sections = "".join(section_html(section, labels, bodies) for section in order)
    main_sections = "".join(section_html(section, labels, bodies) for section in order if section in {"experience", "projects", "awards"})
    side_sections = "".join(section_html(section, labels, bodies, "section-compact") for section in order if section in {"skills", "education"})
    if layout == "asymmetric-left-sidebar":
        return f'''<article class="resume resume-left-sidebar"><aside>{portrait}{render_contact(basics)}{side_sections}</aside><main><header>{identity_content(basics, target, "", contact=False)}</header>{main_sections}</main></article>'''
    if layout == "sidebar-left-hero":
        return f'''<article class="resume resume-sidebar-hero"><header class="hero">{identity_content(basics, target, portrait)}</header><aside>{side_sections}</aside><main>{main_sections}</main></article>'''
    if layout == "hero-header-blocks":
        cards = "".join(section_html(section, labels, bodies, "card card-wide" if section in {"experience", "projects"} else "card") for section in order)
        return f'''<article class="resume resume-hero-blocks"><header class="hero">{identity_content(basics, target, portrait)}</header><div class="block-grid">{cards}</div></article>'''
    if layout == "hero-header-linear":
        return f'''<article class="resume resume-hero-linear"><header class="hero">{identity_content(basics, target, portrait)}</header><main>{all_sections}</main></article>'''
    if layout == "asymmetric-right-sidebar":
        right = portrait + render_contact(basics) + "".join(section_html(section, labels, bodies, "section-compact") for section in order if section in {"skills", "education", "awards"})
        left = "".join(section_html(section, labels, bodies) for section in order if section in {"experience", "projects"})
        return f'''<article class="resume resume-right-sidebar"><main><header>{identity_content(basics, target, "", contact=False)}</header>{left}</main><aside>{right}</aside></article>'''
    return f'''<article class="resume resume-banner"><header class="banner">{identity_content(basics, target, portrait)}</header><main>{all_sections}</main></article>'''


def design_css(layout: str) -> str:
    common = '''
    @page { size: A4; margin: var(--page-margin); }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--paper); }
    body { color: var(--ink); font-family: var(--body-font); font-size: var(--body-size); line-height: var(--line-height); font-weight: 400; text-rendering: optimizeLegibility; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .resume { margin: 0 auto; background: var(--paper); }
    h1, h2, h3, p, ul { margin-top: 0; }
    h1, h2, h3, .headline { font-family: var(--heading-font); }
    h1 { margin-bottom: 1.6mm; font-size: var(--name-size); line-height: 1; font-weight: 700; letter-spacing: -.25pt; }
    .identity { display: flex; align-items: center; justify-content: space-between; gap: 5mm; }
    .identity-copy { min-width: 0; }
    .headline { color: var(--brand); font-size: var(--headline-size); font-weight: 650; }
    .contact { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0 1.8mm; color: var(--muted); font-size: var(--meta-size); }
    .contact .dot { color: var(--line); }
    a { color: var(--brand); text-decoration: none; }
    .summary { margin: 2.8mm 0 0; max-width: 96%; }
    .section { margin-top: var(--section-gap); break-inside: auto; }
    .section-title { margin: 0 0 1.7mm; padding-bottom: .8mm; color: var(--brand); font-size: var(--section-size); line-height: 1.15; letter-spacing: .55pt; border-bottom: .55pt solid var(--line); break-after: avoid; }
    .entry { padding: .55mm 0; break-inside: avoid; page-break-inside: avoid; }
    .entry + .entry { margin-top: var(--entry-gap); }
    .entry-head { display: flex; align-items: baseline; justify-content: space-between; gap: 4mm; }
    h3 { margin-bottom: 0; font-size: var(--entry-size); line-height: 1.25; }
    .entry-date { flex: 0 0 auto; color: var(--muted); font-size: var(--meta-size); white-space: nowrap; }
    .entry-sub, .edu-details { margin-top: .45mm; color: var(--muted); font-size: var(--sub-size); }
    ul { margin-bottom: 0; padding-left: 4.2mm; }
    li { margin: .5mm 0; padding-left: .35mm; }
    li::marker { color: var(--brand); }
    .skill-row { display: grid; grid-template-columns: 5.5em 1fr; gap: 2.6mm; padding: .35mm 0; break-inside: avoid; }
    .skill-row strong { color: var(--brand); }
    .award-row { display: flex; justify-content: space-between; gap: 4mm; padding: .5mm 0; break-inside: avoid; }
    .award-row time { color: var(--muted); font-size: var(--meta-size); }
    .portrait { width: 20mm; height: 25mm; flex: 0 0 auto; object-fit: cover; object-position: center; }
    .section-compact .section-title { font-size: calc(var(--section-size) * .9); }
    .section-compact .entry-head { display: block; }
    .section-compact .entry-date { margin-top: .4mm; white-space: normal; }
    @media screen { .resume { box-shadow: 0 2mm 8mm rgba(0,0,0,.12); } }
    '''
    variants = {
        "asymmetric-left-sidebar": '''
          :root { --page-margin: 0; }
          .resume-left-sidebar { display: grid; grid-template-columns: 58mm 1fr; width: 210mm; min-height: 297mm; }
          .resume-left-sidebar > aside { padding: 14mm 8mm; color: white; background: var(--brand); }
          .resume-left-sidebar > aside .portrait { display: block; width: 28mm; height: 35mm; margin: 0 auto 6mm; }
          .resume-left-sidebar > aside .contact { display: block; color: white; }
          .resume-left-sidebar > aside .contact span, .resume-left-sidebar > aside .contact a { display: block; margin-bottom: 1.6mm; color: white; }
          .resume-left-sidebar > aside .contact .dot { display: none; }
          .resume-left-sidebar > aside .section-title, .resume-left-sidebar > aside .skill-row strong { color: white; border-bottom-color: rgba(255,255,255,.35); }
          .resume-left-sidebar > aside .entry-sub, .resume-left-sidebar > aside .edu-details, .resume-left-sidebar > aside .entry-date, .resume-left-sidebar > aside .skill-row span, .resume-left-sidebar > aside .award-row time { color: rgba(255,255,255,.88); }
          .resume-left-sidebar > aside li::marker { color: rgba(255,255,255,.78); }
          .resume-left-sidebar > aside .skill-row { display: block; }
          .resume-left-sidebar > aside .skill-row span { display: block; margin-top: .6mm; }
          .resume-left-sidebar > main { padding: 14mm 13mm; }
          .resume-left-sidebar > main header { padding-bottom: 3mm; border-bottom: .7pt solid var(--brand); }
        ''',
        "sidebar-left-hero": '''
          :root { --page-margin: 0; }
          .resume-sidebar-hero { display: grid; grid-template-columns: 59mm 1fr; grid-template-rows: auto 1fr; width: 210mm; min-height: 297mm; }
          .resume-sidebar-hero > .hero { grid-column: 1 / -1; padding: 14mm 16mm 11mm; color: white; background: var(--brand); }
          .resume-sidebar-hero .hero .headline, .resume-sidebar-hero .hero .contact, .resume-sidebar-hero .hero a { color: white; }
          .resume-sidebar-hero .hero .summary { max-width: 150mm; color: rgba(255,255,255,.88); }
          .resume-sidebar-hero > aside { padding: 9mm 7mm; color: white; background: color-mix(in srgb, var(--brand) 88%, black); }
          .resume-sidebar-hero > aside .contact { display: block; color: white; }
          .resume-sidebar-hero > aside .contact span, .resume-sidebar-hero > aside .contact a { display: block; margin-bottom: 1.5mm; color: white; }
          .resume-sidebar-hero > aside .contact .dot { display: none; }
          .resume-sidebar-hero > aside .section-title, .resume-sidebar-hero > aside .skill-row strong { color: white; border-bottom-color: rgba(255,255,255,.35); }
          .resume-sidebar-hero > aside .entry-sub, .resume-sidebar-hero > aside .edu-details, .resume-sidebar-hero > aside .entry-date, .resume-sidebar-hero > aside .skill-row span, .resume-sidebar-hero > aside .award-row time { color: rgba(255,255,255,.88); }
          .resume-sidebar-hero > aside li::marker { color: rgba(255,255,255,.78); }
          .resume-sidebar-hero > aside .skill-row { display: block; }
          .resume-sidebar-hero > main { padding: 10mm 13mm; }
        ''',
        "hero-header-blocks": '''
          :root { --page-margin: 0; }
          .resume-hero-blocks { width: 210mm; min-height: 297mm; }
          .resume-hero-blocks > .hero { padding: 15mm 17mm 12mm; color: white; background: var(--brand); }
          .resume-hero-blocks .hero .headline, .resume-hero-blocks .hero .contact, .resume-hero-blocks .hero a { color: white; }
          .resume-hero-blocks .hero .summary { color: rgba(255,255,255,.88); }
          .block-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; padding: 6mm 12mm 12mm; }
          .block-grid .card { margin-top: 0; padding: 4mm; background: var(--tint); break-inside: avoid; }
          .block-grid .card-wide { grid-column: 1 / -1; }
          .block-grid .section-title { border-bottom-color: var(--accent); }
        ''',
        "hero-header-linear": '''
          :root { --page-margin: 0; }
          .resume-hero-linear > .hero { padding: 13mm 17mm 10mm; color: white; background: var(--brand); }
          .resume-hero-linear .hero .headline, .resume-hero-linear .hero .contact, .resume-hero-linear .hero a { color: white; }
          .resume-hero-linear .hero .summary { color: rgba(255,255,255,.88); }
          .resume-hero-linear > main { padding: 8mm 16mm 14mm; }
          .resume-hero-linear .section-title { border-bottom-color: var(--accent); }
        ''',
        "asymmetric-right-sidebar": '''
          :root { --page-margin: 10mm 12mm; }
          .resume-right-sidebar { display: grid; grid-template-columns: 1fr 43mm; gap: 7mm; }
          .resume-right-sidebar > main header { padding-bottom: 3mm; border-bottom: .7pt solid var(--brand); }
          .resume-right-sidebar > aside { padding: 5mm 4mm; background: var(--tint); }
          .resume-right-sidebar > aside .portrait { display: block; width: 25mm; height: 31mm; margin: 0 auto 4mm; }
          .resume-right-sidebar > aside .contact { display: block; }
          .resume-right-sidebar > aside .contact span, .resume-right-sidebar > aside .contact a { display: block; margin-bottom: 1.4mm; }
          .resume-right-sidebar > aside .contact .dot { display: none; }
          .resume-right-sidebar > aside .skill-row { display: block; }
          .resume-right-sidebar > aside .skill-row span { display: block; margin-top: .5mm; }
        ''',
        "banner-accent-flow": '''
          :root { --page-margin: 0; }
          .resume-banner > .banner { padding: 8mm 15mm; color: white; background: var(--brand); }
          .resume-banner .banner .headline, .resume-banner .banner .contact, .resume-banner .banner a { color: white; }
          .resume-banner .banner .summary { color: rgba(255,255,255,.88); }
          .resume-banner > main { padding: 6mm 15mm 14mm; }
          .resume-banner .section-title { padding-left: 2.5mm; border-left: 2.2pt solid var(--accent); border-bottom-color: var(--line); }
        ''',
    }
    return common + variants[layout]


def make_html(
    data: dict[str, Any],
    *,
    layout: str | None = None,
    skin: str | None = None,
    density: str | None = None,
    render_profile: str | None = None,
    theme: str | None = None,
    reference_style: str | None = None,
) -> str:
    design = resolve_design(data, layout=layout, skin=skin, density=density, render_profile=render_profile, theme=theme, reference_style=reference_style)
    tokens = DESIGN_SYSTEM["skins"][design["skin"]]
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    photo = basics.get("photo") if isinstance(basics.get("photo"), dict) else {}
    photo_uri = str(photo.get("_data_uri", "")).strip() if photo.get("enabled") is True else ""
    if photo_uri and not DESIGN_SYSTEM["layouts"][design["layout"]]["supports_photo"]:
        raise ValueError(f"{design['layout']} 不支持照片")
    portrait = f'<img class="portrait" src="{esc(photo_uri)}" alt="{esc(photo.get("_alt") or basics.get("name") or "证件照")}">' if photo_uri else ""
    language = str(data.get("language", "zh-CN"))
    labels = BILINGUAL_LABELS if reference_style == "rc-109" and language == "zh-CN" else LABELS.get(language, LABELS["zh-CN"])
    density_tokens = {
        "sparse": {"body": "10.2pt", "line": "1.54", "name": "29pt", "headline": "11pt", "section": "11.7pt", "entry": "10.7pt", "sub": "9.3pt", "meta": "9pt", "section_gap": "6.5mm", "entry_gap": "2mm"},
        "balanced": {"body": "9.7pt", "line": "1.47", "name": "26pt", "headline": "10.4pt", "section": "11pt", "entry": "10.35pt", "sub": "8.9pt", "meta": "8.65pt", "section_gap": "5mm", "entry_gap": "1.3mm"},
        "dense": {"body": "9.1pt", "line": "1.36", "name": "23pt", "headline": "9.6pt", "section": "10.3pt", "entry": "9.9pt", "sub": "8.4pt", "meta": "8.1pt", "section_gap": "3.5mm", "entry_gap": ".8mm"},
    }[design["density"]]
    css_vars = ";".join([
        f"--paper:{tokens['paper']}", f"--ink:{tokens['ink']}", f"--muted:{tokens['muted']}", f"--line:{tokens['line']}", f"--brand:{tokens['brand']}", f"--tint:{tokens['tint']}", f"--accent:{tokens['accent']}",
        f"--body-font:{tokens['body_font']}", f"--heading-font:{tokens['heading_font']}", f"--body-size:{density_tokens['body']}", f"--line-height:{density_tokens['line']}", f"--name-size:{density_tokens['name']}", f"--headline-size:{density_tokens['headline']}", f"--section-size:{density_tokens['section']}", f"--entry-size:{density_tokens['entry']}", f"--sub-size:{density_tokens['sub']}", f"--meta-size:{density_tokens['meta']}", f"--section-gap:{density_tokens['section_gap']}", f"--entry-gap:{density_tokens['entry_gap']}"
    ])
    markup = layout_markup(data, design, portrait, labels, build_bodies(data))
    title = esc(f"{basics.get('name', '')} - {target.get('role', '')} - {DESIGN_SYSTEM['layouts'][design['layout']]['label']}")
    return f'''<!doctype html>
<html lang="{'en' if language == 'en' else 'zh-CN'}" data-layout="{design['layout']}" data-skin="{design['skin']}" data-density="{design['density']}" data-render-profile="{design['render_profile']}">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light">
  <meta name="generator" content="Resume Studio 3.0 local renderer"><meta name="resume-layout-system" content="archetype-skin-density-3.0"><meta name="resume-typography-system" content="3.0">
  <title>{title}</title><style>:root{{{css_vars};}}{design_css(design['layout'])}</style>
</head><body class="layout-{design['layout']} skin-{design['skin']} density-{design['density']}">{markup}</body></html>'''


def find_browser() -> str | None:
    candidates = [
        os.environ.get("RESUME_BROWSER", ""),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or "", shutil.which("microsoft-edge") or "",
    ]
    return next((value for value in candidates if value and Path(value).is_file()), None)


def print_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    pdf_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="lyz-resume-chrome-") as profile:
        command = [browser, "--headless=new", "--disable-gpu", "--disable-extensions", "--no-first-run", "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--user-data-dir={profile}", f"--print-to-pdf={pdf_path}", html_path.as_uri()]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        deadline, previous_size, stable_since, generated = time.monotonic() + 30, -1, None, False
        while time.monotonic() < deadline:
            if pdf_path.is_file() and pdf_path.stat().st_size > 1024:
                size = pdf_path.stat().st_size
                if size == previous_size:
                    stable_since = stable_since or time.monotonic()
                    if time.monotonic() - stable_since >= 1:
                        generated = pdf_path.read_bytes()[:5] == b"%PDF-"
                        break
                else:
                    previous_size, stable_since = size, None
            if process.poll() is not None:
                generated = pdf_path.is_file() and pdf_path.read_bytes()[:5] == b"%PDF-"
                break
            time.sleep(.2)
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        stdout, stderr = process.communicate(timeout=5)
    if not generated:
        raise RuntimeError(stderr.strip() or stdout.strip() or "浏览器未生成有效 PDF")


def render_one(data: dict[str, Any], design: dict[str, str], output_dir: Path, basename: str, browser: str | None, html_only: bool) -> dict[str, Any]:
    html_path, pdf_path = output_dir / f"{basename}.html", output_dir / f"{basename}.pdf"
    html_path.write_text(make_html(data, **design), encoding="utf-8")
    item: dict[str, Any] = {"layout": design["layout"], "skin": design["skin"], "density": design["density"], "render_profile": design["render_profile"], "html": str(html_path), "pdf": None}
    if not html_only:
        if not browser:
            raise RuntimeError("未找到 Chrome、Chromium 或 Edge；可设置 RESUME_BROWSER")
        print_pdf(browser, html_path, pdf_path)
        item["pdf"] = str(pdf_path)
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description="将 v2 结构化简历渲染为六种布局的本地 HTML/PDF。")
    parser.add_argument("input"); parser.add_argument("--output-dir", "-o", default="output"); parser.add_argument("--basename")
    parser.add_argument("--layout", choices=LAYOUT_ORDER); parser.add_argument("--skin", choices=SKIN_CHOICES); parser.add_argument("--density", choices=("auto", "sparse", "balanced", "dense")); parser.add_argument("--render-profile", choices=("ats-first", "balanced", "human-first"))
    parser.add_argument("--theme", choices=LEGACY_THEMES, help="兼容旧版主题"); parser.add_argument("--reference-style", choices=REFERENCE_STYLE_ORDER); parser.add_argument("--all-layouts", action="store_true"); parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON 根节点必须是对象")
        hydrate_photo(data, input_path.parent)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    if args.all_layouts and (args.layout or args.theme or args.reference_style):
        parser.error("--all-layouts 不能与 --layout、--theme 或 --reference-style 同时使用")
    try:
        if args.all_layouts:
            selections = []
            for layout in LAYOUT_ORDER:
                meta = DESIGN_SYSTEM["layouts"][layout]
                profile = args.render_profile or ("balanced" if "balanced" in meta["render_profiles"] else "human-first")
                requested_density = args.density or "auto"
                try:
                    selections.append(resolve_design(data, layout=layout, skin=args.skin or "auto", density=requested_density, render_profile=profile))
                except ValueError:
                    fallback_density = "balanced" if "balanced" in meta["capacity"] else meta["capacity"][0]
                    selections.append(resolve_design(data, layout=layout, skin=args.skin or "auto", density=fallback_density, render_profile=profile))
        else:
            selections = [resolve_design(data, layout=args.layout, skin=args.skin, density=args.density, render_profile=args.render_profile, theme=args.theme, reference_style=args.reference_style)]
    except ValueError as exc:
        parser.error(str(exc))
    output_dir = Path(args.output_dir).expanduser().resolve(); output_dir.mkdir(parents=True, exist_ok=True)
    base = safe_basename(args.basename or str(data.get("filename") or "resume")); browser = None if args.html_only else find_browser(); outputs = []
    try:
        for design in selections:
            suffix = DESIGN_SYSTEM["layouts"][design["layout"]]["label"]
            rendered_name = base if len(selections) == 1 else safe_basename(f"{base}_{suffix}")
            outputs.append(render_one(data, design, output_dir, rendered_name, browser, args.html_only))
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"简历渲染失败：{exc}", file=sys.stderr); raise SystemExit(4) from exc
    manifest = {"ok": True, "input": str(input_path), "renderer": None if args.html_only or not browser else Path(browser).name, "set_type": "all_layouts" if args.all_layouts else "single", "layout_count": len(outputs), "outputs": outputs}
    if len(outputs) > 1:
        manifest_path = output_dir / f"{base}_六布局清单.json"; manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); manifest["manifest"] = str(manifest_path)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
