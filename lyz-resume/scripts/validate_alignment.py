#!/usr/bin/env python3
"""Validate role analysis -> resume plan -> resume data alignment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TIERS = {"core", "supporting", "brief", "omit"}
SECTIONS = ("experience", "projects", "education", "skills", "awards")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} 根节点必须是对象")
    return value


def string_set(raw: Any) -> set[str]:
    if not isinstance(raw, list):
        return set()
    return {str(value).strip() for value in raw if str(value).strip()}


def resume_evidence(data: dict[str, Any]) -> tuple[set[str], dict[str, int], list[str]]:
    included: set[str] = set()
    bullet_counts: dict[str, int] = {}
    visible_order: list[str] = []
    requested = data.get("section_order")
    order = [value for value in requested if value in SECTIONS] if isinstance(requested, list) else list(SECTIONS)
    order.extend(section for section in SECTIONS if section not in order)
    for section in order:
        if section not in {"experience", "projects"}:
            continue
        for item in data.get(section, []) or []:
            if not isinstance(item, dict):
                continue
            ids = string_set(item.get("evidence_ids"))
            for bullet in item.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    ids.update(string_set(bullet.get("evidence_ids")))
            for evidence_id in ids:
                included.add(evidence_id)
                bullet_counts[evidence_id] = bullet_counts.get(evidence_id, 0) + len(item.get("bullets", []) or [])
                if evidence_id not in visible_order:
                    visible_order.append(evidence_id)
    return included, bullet_counts, visible_order


def validate_alignment(
    role: dict[str, Any],
    plan: dict[str, Any],
    resume: dict[str, Any],
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    role_target = str((role.get("target") or {}).get("role", "")).strip()
    plan_target = str((plan.get("target") or {}).get("role", "")).strip()
    resume_target = str((resume.get("target") or {}).get("role", "")).strip()
    if not role_target or len({role_target, plan_target, resume_target}) != 1:
        errors.append("role-analysis、resume-plan 与 resume-data 的目标岗位必须一致")

    requirements = {
        str(item.get("id", "")).strip(): item
        for item in role.get("requirements", []) or []
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    priority_ids = string_set(plan.get("priority_requirement_ids"))
    unknown_priority = sorted(priority_ids - set(requirements))
    if unknown_priority:
        errors.append(f"resume-plan 引用了未知岗位要求：{', '.join(unknown_priority)}")
    if not priority_ids:
        errors.append("resume-plan 至少需要一个 priority_requirement_id")

    decisions: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(plan.get("evidence_decisions", []) or [], 1):
        if not isinstance(item, dict):
            errors.append(f"evidence_decisions[{index}] 必须是对象")
            continue
        evidence_id = str(item.get("evidence_id", "")).strip()
        tier = str(item.get("tier", "")).strip()
        budget = item.get("bullet_budget")
        if not evidence_id:
            errors.append(f"evidence_decisions[{index}] 缺少 evidence_id")
            continue
        if evidence_id in decisions:
            errors.append(f"evidence_decisions 重复：{evidence_id}")
        decisions[evidence_id] = item
        if tier not in TIERS:
            errors.append(f"{evidence_id} 的 tier 无效")
        if not isinstance(budget, int) or not 0 <= budget <= 5:
            errors.append(f"{evidence_id} 的 bullet_budget 必须为 0–5")
        elif tier == "omit" and budget != 0:
            errors.append(f"{evidence_id} 已 omit，bullet_budget 必须为 0")
        elif tier == "brief" and budget > 1:
            errors.append(f"{evidence_id} 为 brief，bullet_budget 不得超过 1")
        decision_requirements = string_set(item.get("requirement_ids"))
        unknown = sorted(decision_requirements - set(requirements))
        if unknown:
            errors.append(f"{evidence_id} 关联未知岗位要求：{', '.join(unknown)}")
        if not str(item.get("reason", "")).strip():
            errors.append(f"{evidence_id} 缺少取舍理由")

    if plan.get("content_mode") == "layout-only" and any(
        str(item.get("tier")) == "omit" for item in decisions.values()
    ):
        errors.append("只换版式路径不得通过 resume-plan 删除原内容")

    for requirement_id, requirement in requirements.items():
        if requirement.get("priority") != "must" or requirement.get("status") != "supported":
            continue
        evidence_ids = string_set(requirement.get("evidence_ids"))
        if evidence_ids and not any(
            evidence_id in decisions and decisions[evidence_id].get("tier") != "omit"
            for evidence_id in evidence_ids
        ):
            errors.append(f"受支持的 must 要求未进入简历计划：{requirement_id}")

    included, bullet_counts, visible_order = resume_evidence(resume)
    omitted = {evidence_id for evidence_id, item in decisions.items() if item.get("tier") == "omit"}
    planned_included = set(decisions) - omitted
    leaked = sorted(included & omitted)
    if leaked:
        errors.append(f"被标记 omit 的证据仍出现在成稿：{', '.join(leaked)}")
    missing = sorted(planned_included - included)
    if missing:
        errors.append(f"计划纳入的证据未出现在成稿：{', '.join(missing)}")
    unplanned = sorted(included - set(decisions))
    if unplanned:
        errors.append(f"成稿包含未经过计划的证据：{', '.join(unplanned)}")

    for evidence_id, count in bullet_counts.items():
        decision = decisions.get(evidence_id, {})
        budget = decision.get("bullet_budget")
        if isinstance(budget, int) and count > budget:
            errors.append(f"{evidence_id} 实际 {count} 条 bullet，超过计划预算 {budget}")

    core_ids = {evidence_id for evidence_id, item in decisions.items() if item.get("tier") == "core"}
    if core_ids and not core_ids.intersection(visible_order[:2]):
        warnings.append("核心证据没有出现在前两个可见实践条目中")

    targeting = resume.get("targeting") if isinstance(resume.get("targeting"), dict) else {}
    declared_included = string_set(targeting.get("included_evidence_ids"))
    declared_omitted = string_set(targeting.get("omitted_evidence_ids"))
    if declared_included != included:
        errors.append("resume-data.targeting.included_evidence_ids 与成稿证据不一致")
    if declared_omitted != omitted:
        errors.append("resume-data.targeting.omitted_evidence_ids 与计划不一致")
    if str(targeting.get("role_thesis", "")).strip() != str(plan.get("role_thesis", "")).strip():
        errors.append("resume-data 的 role_thesis 与 resume-plan 不一致")

    facts = {
        "target_role": resume_target,
        "priority_requirements": sorted(priority_ids),
        "planned_evidence": len(decisions),
        "included_evidence": sorted(included),
        "omitted_evidence": sorted(omitted),
        "core_evidence": sorted(core_ids),
        "visible_evidence_order": visible_order,
    }
    return errors, warnings, facts


def main() -> None:
    parser = argparse.ArgumentParser(description="检查岗位分析、简历计划和成稿之间的取舍与追溯关系。")
    parser.add_argument("role_analysis")
    parser.add_argument("resume_plan")
    parser.add_argument("resume_data")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    try:
        role = load_object(Path(args.role_analysis).expanduser().resolve())
        plan = load_object(Path(args.resume_plan).expanduser().resolve())
        resume = load_object(Path(args.resume_data).expanduser().resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    errors, warnings, facts = validate_alignment(role, plan, resume)
    report = {"ok": not errors, "facts": facts, "errors": errors, "warnings": warnings}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
