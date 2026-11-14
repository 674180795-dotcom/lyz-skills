---
name: 技能工坊
description: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use for skill creation, reusable workflow packaging, skill improvement, evals, and team-ready distribution.
metadata:
  author: Yao Team
---

# Yao Meta Skill

## Router Rules

- Keep `SKILL.md` lean; put guidance in `references/`, logic in `scripts/`, and evidence in `reports/`.
- Use the lightest reliable process.

## Modes

- `Scaffold`: exploratory/personal. `Production`: team reuse. `Library`: shared infrastructure. `Governed`: high-trust, policy-sensitive, or release-critical.
- [Operating Modes](references/operating-modes.md) · [Resource Boundaries](references/resource-boundaries.md).

## Compact Workflow

1. For one-off/no reusable process: `Do not create a skill`; `near-neighbor`; require `repeated use` + `reusable output contract`.
2. Capture job, output, exclusions, constraints, standards, and the lightest fit.
3. Scan references in order: external benchmark, user source, local fit; surface only uncertainty or conflict.
4. Write `description` early, test route quality, then add only earned folders and gates.
5. Add output-risk, artifact-design, prompt-quality, system-model, and next directions only when useful.

Playbooks: [Method](references/skill-engineering-method.md), [Intent](references/intent-dialogue.md), [Skill IR](references/skill-ir-method.md), [Output Eval](references/output-eval-method.md), [Review Studio](references/review-studio-method.md).

## Human Evaluation for Iterations

Every iteration (this meta-skill and Scaffold included) must follow [Human Evaluation](references/human-evaluation.md): freeze 3–5 task criteria/thresholds, run actual outputs, collect human scores via the [option/copy template](assets/human-scorecard.html) or chat. No JSON/reason required. Missing/N stays `pending_human`; critical failures override averages. Automated checks/waivers cannot substitute. Allow coexisting versions or explicit replacement; trial installation is not acceptance.

Image scorecards keep a bounded image on the left and its scores on the right in one viewport; switch candidates in place. Never force scrolling between the image and its scoring controls.

## Skill OS 2.0 Gates

Before production/library/governed/team release, run Skill IR, target compiler, trigger + output eval, Skill Atlas, conformance, trust, registry/package/install, upgrade, drift, waiver, and Review Studio gates.

## Governed Package Boundary

For file-backed, release-critical, or governed packages, name `input_files` as `file-backed fixture` evidence; include `owner`, `review cadence`, `input_files`, `output contract`, `rollback boundary`; require `trust report` and `reports/output_quality_scorecard.md`; mark unavailable telemetry, approvals, metrics, or benchmarks as `missing evidence`; do not fabricate evidence.

Preserve these audit labels literally. See [Governance](references/governance.md).

## First-Turn Style

Start from outcomes. Ask `2-3` key questions only if needed. Chinese: soft, companion-like; [Intent Dialogue](references/intent-dialogue.md).

## Output Contract

Unless asked otherwise, produce `SKILL.md`, aligned `agents/interface.yaml`, justified assets, and a short summary of boundary, exclusions, gates, and next steps.
