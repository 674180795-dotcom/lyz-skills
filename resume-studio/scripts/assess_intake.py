#!/usr/bin/env python3
"""Assess resume-intake readiness and rank the next highest-value gaps."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FORBIDDEN_KEYS = {
    "id_card",
    "identity_number",
    "password",
    "token",
    "secret",
    "religion",
    "marital_status",
    "ethnicity",
    "full_address",
    "health_record",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def private_key_hits(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_KEYS:
                hits.append(path)
            hits.extend(private_key_hits(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(private_key_hits(child, f"{prefix}[{index}]"))
    return hits


def add_gap(
    gaps: list[dict[str, Any]],
    *,
    field: str,
    question: str,
    why: str,
    impact: int,
    friction: int,
    blocking: bool = False,
) -> None:
    gaps.append(
        {
            "field": field,
            "question": question,
            "why": why,
            "impact": impact,
            "friction": friction,
            "blocking": blocking,
            "priority_score": impact * 3 - friction + (8 if blocking else 0),
        }
    )


def assess(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    gaps: list[dict[str, Any]] = []

    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    if not nonempty(target.get("role")):
        errors.append("缺少目标岗位或岗位族")
        add_gap(
            gaps,
            field="target.role",
            question="这份简历现在最想先投哪个岗位或岗位族？不确定的话，我也可以根据你最强的经历给 1 个推荐方向。",
            why="岗位会改变取材、排序和追问方向。",
            impact=5,
            friction=1,
            blocking=True,
        )

    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    if not nonempty(basics.get("name")):
        errors.append("缺少公开姓名")
        add_gap(
            gaps,
            field="basics.name",
            question="最终简历使用什么姓名？",
            why="这是交付文件的硬信息。",
            impact=4,
            friction=0,
            blocking=True,
        )
    email = str(basics.get("email", "")).strip()
    if not EMAIL_RE.match(email):
        errors.append("缺少可用邮箱")
        add_gap(
            gaps,
            field="basics.email",
            question="最终简历使用哪个可公开邮箱？",
            why="至少需要一种稳定的公开联系方式。",
            impact=4,
            friction=0,
            blocking=True,
        )

    evidence_items = data.get("evidence_items") if isinstance(data.get("evidence_items"), list) else []
    known_ids: set[str] = set()
    complete_items: list[dict[str, Any]] = []
    for item in evidence_items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "")).strip()
        if item_id:
            known_ids.add(item_id)
        actions = item.get("actions") if isinstance(item.get("actions"), list) else []
        complete = (
            item.get("status") == "confirmed"
            and nonempty(item_id)
            and nonempty(item.get("name"))
            and nonempty(item.get("ownership"))
            and any(nonempty(action) for action in actions)
            and nonempty(item.get("result"))
            and nonempty(item.get("proof"))
        )
        if complete:
            complete_items.append(item)
            continue

        label = str(item.get("name") or "当前经历")
        if not nonempty(item.get("ownership")):
            add_gap(
                gaps,
                field=f"evidence_items.{item_id or label}.ownership",
                question=f"在“{label}”里，哪些部分是你独立或主要负责的？团队其他人做了什么？",
                why="个人边界决定能否把团队结果写成你的贡献。",
                impact=5,
                friction=1,
            )
        elif not any(nonempty(action) for action in actions):
            add_gap(
                gaps,
                field=f"evidence_items.{item_id or label}.actions",
                question=f"在“{label}”里，你做过的最关键动作是什么？说一个最有印象的就行。",
                why="具体动作是简历 bullet 的骨架。",
                impact=4,
                friction=1,
            )
        elif not nonempty(item.get("result")):
            add_gap(
                gaps,
                field=f"evidence_items.{item_id or label}.result",
                question=f"“{label}”最后怎样算完成或变好了？没有数字也可以，验收、上线、复用、少返工或按期交付都算。",
                why="结果让动作有落点，但不要求编造数字。",
                impact=4,
                friction=1,
            )
        elif not nonempty(item.get("proof")):
            add_gap(
                gaps,
                field=f"evidence_items.{item_id or label}.proof",
                question=f"“{label}”的结果来自哪里：你的明确确认、原简历、仓库、证书、验收记录，还是其他材料？",
                why="证据来源决定 claim 的表达强度。",
                impact=3,
                friction=1,
            )

    if not complete_items:
        errors.append("没有形成闭环的经历证据")
        if not evidence_items:
            add_gap(
                gaps,
                field="evidence_items",
                question="先说一件你最熟的工作、项目、课程或校园经历：当时要完成什么？口语讲就行。",
                why="只需要一项经历就能开始形成第一条可用资产。",
                impact=5,
                friction=1,
                blocking=True,
            )

    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    linked_skills = [
        skill
        for skill in skills
        if isinstance(skill, dict)
        and skill.get("status") == "confirmed"
        and nonempty(skill.get("name"))
        and isinstance(skill.get("evidence_ids"), list)
        and any(str(ref).strip() in known_ids for ref in skill.get("evidence_ids", []))
    ]
    if not linked_skills:
        warnings.append("核心技能尚未关联到经历证据")
        add_gap(
            gaps,
            field="skills.evidence_ids",
            question="你最有把握在面试中解释的一个技能或工具是什么？它具体用在哪段经历里？",
            why="技能放进真实场景，比单独罗列更可信。",
            impact=3,
            friction=1,
        )

    requirements = data.get("job_requirements") if isinstance(data.get("job_requirements"), list) else []
    mapped_requirements = 0
    mapping_errors = 0
    if target.get("jd_available") is True and not requirements:
        warnings.append("已提供 JD，但尚未建立要求—证据—缺口映射")
        add_gap(
            gaps,
            field="job_requirements",
            question="这份 JD 里你认为最关键的一条硬要求是什么？我先把它和已有经历对上。",
            why="先解决最关键要求，避免把整份 JD 变成问卷。",
            impact=4,
            friction=1,
        )
    for requirement in requirements:
        if not isinstance(requirement, dict):
            mapping_errors += 1
            continue
        status = requirement.get("status")
        refs = requirement.get("evidence_ids") if isinstance(requirement.get("evidence_ids"), list) else []
        valid_refs = [str(ref).strip() for ref in refs if str(ref).strip() in known_ids]
        if status == "supported" and not valid_refs:
            mapping_errors += 1
        elif status in {"supported", "partial", "gap"}:
            mapped_requirements += 1
        else:
            mapping_errors += 1
    if mapping_errors:
        errors.append(f"有 {mapping_errors} 项岗位要求映射无效")

    uncertainties = data.get("uncertainties") if isinstance(data.get("uncertainties"), list) else []
    blocking_uncertainties = [
        item
        for item in uncertainties
        if isinstance(item, dict) and item.get("blocking") is True and item.get("resolved") is not True
    ]
    if blocking_uncertainties:
        errors.append(f"有 {len(blocking_uncertainties)} 项阻断性疑点未解决")
        highest = blocking_uncertainties[0]
        add_gap(
            gaps,
            field="uncertainties",
            question=str(highest.get("question") or "先确认时间线、职责归属或数字中最影响真实性的一项，可以吗？"),
            why="阻断性矛盾不能带入最终简历。",
            impact=5,
            friction=1,
            blocking=True,
        )

    confirmation = data.get("confirmation") if isinstance(data.get("confirmation"), dict) else {}
    confirmed = confirmation.get("status") == "confirmed"
    if not confirmed:
        errors.append("最终事实摘要尚未获得明确确认")
        add_gap(
            gaps,
            field="confirmation.status",
            question="我会先把目标岗位、核心经历、可用结果、技能证据和仍有疑点压缩成 5 条；这些事实可以作为最终简历依据吗？",
            why="明确确认可防止模型把推断偷偷变成事实。",
            impact=5,
            friction=1,
            blocking=True,
        )

    private_hits = private_key_hits(data)
    if private_hits:
        errors.append("事实账本包含不应收集的敏感字段：" + ", ".join(private_hits))

    hard_block = (
        not nonempty(target.get("role"))
        or not nonempty(basics.get("name"))
        or not EMAIL_RE.match(email)
        or not complete_items
        or bool(blocking_uncertainties)
        or not confirmed
        or bool(private_hits)
        or bool(mapping_errors)
    )
    mapped_enough = target.get("jd_available") is not True or (bool(requirements) and mapped_requirements == len(requirements))
    if hard_block:
        state = "blocked"
    elif len(complete_items) >= 2 and linked_skills and mapped_enough:
        state = "strong"
    else:
        state = "workable"
        warnings.append("当前素材可生成诚实版本，但证据覆盖仍偏薄")

    gaps.sort(key=lambda item: (-int(item["priority_score"]), int(item["friction"]), str(item["field"])))
    return {
        "ok": state in {"workable", "strong"},
        "state": state,
        "counts": {
            "evidence_items": len(evidence_items),
            "complete_evidence_items": len(complete_items),
            "linked_skills": len(linked_skills),
            "job_requirements": len(requirements),
            "mapped_job_requirements": mapped_requirements,
            "blocking_uncertainties": len(blocking_uncertainties),
        },
        "errors": errors,
        "warnings": warnings,
        "next_questions": gaps[:3],
        "evidence_boundary": "deterministic completeness check; it cannot prove that user-provided facts are true",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="检查简历采集状态并给出下一批高价值问题。")
    parser.add_argument("input", help="candidate-ledger.json 路径")
    parser.add_argument("--output", "-o", help="写出 JSON 报告")
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"无法读取事实账本：{exc}")
    if not isinstance(payload, dict):
        parser.error("事实账本根节点必须是对象")
    result = assess(payload)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        target = Path(args.output).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if result["state"] == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
