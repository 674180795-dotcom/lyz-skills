#!/usr/bin/env python3
"""Offline same-series brief compiler; the host calls the actual image tool."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = json.loads((ROOT / "assets/rules.json").read_text(encoding="utf-8"))


def plain(value, name, limit=180):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError(f"Invalid {name}")
    return value.strip()


def get_card(brief):
    key = plain(brief["aircraft"], "aircraft", 40)
    if "subject_card" not in brief:
        if key not in RULES["aircraft"]:
            raise ValueError("Unknown aircraft: first verify a subject_card; never substitute another model")
        return copy.deepcopy(RULES["aircraft"][key])
    if key in RULES["aircraft"]:
        raise ValueError("Do not override a built-in aircraft lock")
    card = brief["subject_card"]
    fields = {"name", "features", "avoid_features", "source", "evidence_status"}
    if not isinstance(card, dict) or set(card) != fields or card["name"] != key:
        raise ValueError("subject_card fields or name mismatch")
    if card["evidence_status"] != "verified":
        raise ValueError("Unverified aircraft geometry")
    plain(card["source"], "geometry source", 500)
    for field, lo, hi in [("features", 3, 6), ("avoid_features", 1, 4)]:
        seq = card[field]
        if not isinstance(seq, list) or not lo <= len(seq) <= hi:
            raise ValueError(f"Invalid {field} count")
        for item in seq:
            plain(item, field)
            if len(item.split()) > 12 or re.search(r"ignore|system prompt|execute|upload|instruction", item, re.I):
                raise ValueError("Use concise geometry features, not instructions")
    return copy.deepcopy(card)


def compile_brief(raw):
    allowed = set(RULES["defaults"]) | {"subject_card"}
    if not isinstance(raw, dict) or set(raw) - allowed:
        raise ValueError("Unknown brief fields")
    brief = copy.deepcopy(RULES["defaults"])
    brief.update(copy.deepcopy(raw))
    for field, choices in [("family", RULES["families"]), ("pose", RULES["poses"]), ("ratio", ["1:1"])]:
        if not isinstance(brief[field], str) or brief[field] not in choices:
            raise ValueError(f"Invalid {field}: choose {list(choices)}")
    card = get_card(brief)
    if brief["label"] == "auto":
        brief["label"] = brief["aircraft"].replace("-", "")
    if not isinstance(brief["label"], str) or not re.fullmatch(r"[A-Za-z0-9\u4e00-\u9fff -]{0,12}", brief["label"]):
        raise ValueError("Label: at most 12 letters/digits/CJK characters/spaces/hyphens")
    refs = brief["reference_images"]
    if not isinstance(refs, list) or len(refs) > 2:
        raise ValueError("Use at most two reference images")
    roles = set()
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"path", "role", "aircraft"}:
            raise ValueError("Each reference needs exactly path, role and observed aircraft")
        if not isinstance(ref["role"], str) or ref["role"] not in {"geometry", "series"} or ref["role"] in roles:
            raise ValueError("Use distinct geometry and series roles")
        if not isinstance(ref["path"], str):
            raise ValueError("Reference path must be a string")
        plain(ref["aircraft"], "reference aircraft", 40)
        if ref["role"] == "geometry" and ref["aircraft"] != brief["aircraft"]:
            raise ValueError("Geometry reference must show the target aircraft; do not borrow another model's wings")
        p = Path(ref["path"])
        if not p.is_absolute() or not p.is_file() or p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError("Reference must be an existing absolute local image path")
        roles.add(ref["role"])
    family = RULES["families"][brief["family"]]
    common = RULES["common"]
    lines = ["Use case: product-mockup. One new embroidered patch in the reference series."]
    for i, ref in enumerate(refs, 1):
        meaning = ("TARGET silhouette/projection authority: preserve proportions and wing-overlap order; mirror only for requested heading"
                   if ref["role"] == "geometry" else
                   "COLOR/TEXTILE authority only; do not borrow its aircraft, appendages, slogans or logos")
        lines.append(f"Reference {i} ({ref['aircraft']}): {meaning}.")
    lines += [
        f"Target {brief['aircraft']}: " + "; ".join(card["features"]) + ".",
        "Forbidden structures: " + "; ".join(card["avoid_features"]) + ".",
        card.get("topology", "Keep the verified wing/tail count and fore-aft order."),
        RULES["poses"][brief["pose"]],
        common["simplification"],
        common["carrier"],
        common["hierarchy"] if brief["label"] else "Keep the main aircraft and background readable; no lettering.",
        family["layout"] if brief["label"] else "One oblique aircraft balanced by the family field; no text block.",
        family["field"],
        "Colors: " + family["palette"] + ".",
        (f'Only text: "{brief["label"]}". ' + family["lettering"] if brief["label"] else "Omit all model lettering."),
        family["stitch"],
        common["presentation"],
    ]
    lines.append("Avoid: " + common["avoid"] + "; " + family["forbidden"] + ".")
    prompt = "\n".join(lines)
    count = len(prompt.split())
    if count > RULES["word_budget"]:
        raise ValueError(f"Prompt too long ({count}); shorten descriptions, never remove identity locks")
    design = {"version": RULES["version"], "brief": brief, "identity_lock": card, "word_count": count,
              "family_evidence": family["sources"], "six_axis_plan": {
                  "structure": card["features"], "omission": common["simplification"],
                  "color": family["palette"], "angle": RULES["poses"][brief["pose"]],
                  "text": family["lettering"] if brief["label"] else "explicitly omitted",
                  "series": family["layout"]},
              "priority": RULES["priority"], "fbs_weights": RULES["fbs_lexicon"],
              "reference_contract": {"geometry": "target silhouette/projection", "series": "color/textile only; foreign geometry excluded"},
              "image_generated": False, "human_rating": "pending"}
    request = {"kind": "host-agent-call-plan", "preferred_tool": "image_gen.imagegen", "prompt": prompt,
               "references_to_inspect_and_pass": refs, "transparent_background": False,
               "note": "Use current tool schema. Offline compiler does not generate images."}
    return prompt, design, request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brief", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    try:
        prompt, design, request = compile_brief(json.loads(a.brief.read_text(encoding="utf-8")))
        a.out.mkdir(parents=True, exist_ok=True)
        paths = [a.out / n for n in ("prompt.txt", "design.json", "request.json")]
        if any(p.exists() for p in paths):
            raise ValueError("Choose a fresh output directory; never overwrite earlier results")
        payloads = [prompt + "\n", json.dumps(design, ensure_ascii=False, indent=2) + "\n",
                    json.dumps(request, ensure_ascii=False, indent=2) + "\n"]
        written = []
        try:
            for path, payload in zip(paths, payloads):
                with path.open("x", encoding="utf-8") as fh:
                    written.append(path)
                    fh.write(payload)
        except OSError:
            for path in written: path.unlink(missing_ok=True)
            raise
        print(json.dumps({"output": str(a.out.resolve()), "words": design["word_count"], "image_generated": False}))
    except (ValueError, OSError, TypeError) as exc:
        ap.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
