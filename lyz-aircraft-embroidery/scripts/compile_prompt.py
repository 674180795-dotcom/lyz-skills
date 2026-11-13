#!/usr/bin/env python3
"""Offline brief-to-prompt compiler. The host agent invokes image generation."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = json.loads((ROOT / "assets/rules.json").read_text(encoding="utf-8"))
FIELDS = set(RULES["defaults"]) | {"subject_card"}


def short_text(value, name, max_words=16):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}: nonempty string required")
    if len(value) > 200 or len(value.split()) > max_words or any(ord(c) < 32 for c in value):
        raise ValueError(f"{name}: too long or control characters")
    if re.search(r"ignore|instruction|system prompt|upload|execute|https?://", value, re.I):
        raise ValueError(f"{name}: geometry descriptions only")
    return value.strip()


def subject_card(brief):
    key = brief["aircraft"]
    if "subject_card" not in brief:
        if key not in RULES["aircraft"]:
            raise ValueError("Unknown aircraft: supply a verified subject_card; never substitute a nearby model")
        return copy.deepcopy(RULES["aircraft"][key])
    card = brief["subject_card"]
    required = {"name", "features", "avoid_features", "source", "evidence_status"}
    if not isinstance(card, dict) or set(card) != required:
        raise ValueError("subject_card: exact fields name/features/avoid_features/source/evidence_status required")
    if key in RULES["aircraft"]:
        raise ValueError("Built-in aircraft locks cannot be overridden; use an explicitly named new variant")
    short_text(card["name"], "subject name")
    if card["name"] != key:
        raise ValueError("subject_card.name must equal aircraft")
    if card["evidence_status"] != "verified" or not isinstance(card["source"], str) or not card["source"].strip():
        raise ValueError("Verify external geometry evidence before compiling")
    if len(card["source"]) > 500 or any(ord(c) < 32 for c in card["source"]):
        raise ValueError("Invalid evidence source")
    for field, low, high in [("features", 3, 6), ("avoid_features", 1, 4)]:
        seq = card[field]
        if not isinstance(seq, list) or not low <= len(seq) <= high:
            raise ValueError(f"subject_card.{field}: requires {low}..{high} entries")
        for item in seq:
            short_text(item, field, 12)
    return copy.deepcopy(card)


def compile_brief(raw):
    if not isinstance(raw, dict) or set(raw) - FIELDS:
        raise ValueError("Brief must be an object using only documented fields")
    brief = copy.deepcopy(RULES["defaults"])
    brief.update(copy.deepcopy(raw))
    if not isinstance(brief["concept"], str) or brief["concept"] not in RULES["concepts"]:
        raise ValueError("concept: choose one documented design event")
    concept = RULES["concepts"][brief["concept"]]
    for field in ("composition", "rhythm", "palette", "heading"):
        if brief[field] == "auto":
            brief[field] = concept[field]
    for field, choices in [("composition", RULES["compositions"]), ("shape", RULES["shapes"]),
                           ("rhythm", RULES["rhythms"]), ("palette", RULES["palettes"]),
                           ("heading", ["upper right", "upper left"]),
                           ("ratio", RULES["ratios"])]:
        if not isinstance(brief[field], str) or brief[field] not in choices:
            raise ValueError(f"{field}: select one of {list(choices)}")
    short_text(brief["aircraft"], "aircraft")
    if not isinstance(brief["text"], str) or not re.fullmatch(r"[A-Za-z0-9\u4e00-\u9fff -]{0,12}", brief["text"]):
        raise ValueError("text: at most 12 letters/digits/CJK characters/spaces/hyphens")
    card = subject_card(brief)
    refs = brief["reference_images"]
    if not isinstance(refs, list) or len(refs) > 2:
        raise ValueError("reference_images: at most one geometry and one material image")
    roles = set()
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"path", "role"}:
            raise ValueError("Each reference requires exactly path and role")
        if not isinstance(ref["role"], str) or ref["role"] not in {"geometry", "material"} or ref["role"] in roles:
            raise ValueError("Reference role must be unique: geometry or material")
        if not isinstance(ref["path"], str) or not Path(ref["path"]).is_absolute() or not Path(ref["path"]).is_file():
            raise ValueError("Reference path must name an existing absolute local file")
        roles.add(ref["role"])
    adjustments = []
    if brief["rhythm"] == "grid" and brief["composition"] != "axial":
        adjustments.append({"field": "rhythm", "from": "grid", "to": "none",
                            "reason": "B_GRID conflicts with selected projection; preserve aircraft and composition"})
        brief["rhythm"] = "none"
    if brief["rhythm"] == "grid" and brief["concept"] != "identity_study":
        adjustments.append({"field": "rhythm", "from": "grid", "to": "none",
                            "reason": "Grid competes with narrative scene; preserve selected design event"})
        brief["rhythm"] = "none"
    patterns = ["P_IDENTITY", "P_HIERARCHY", RULES["compositions"][brief["composition"]]["pattern"]]
    patterns.append(concept["pattern"])
    if RULES["rhythms"][brief["rhythm"]]["pattern"]:
        patterns.append(RULES["rhythms"][brief["rhythm"]]["pattern"])
    patterns += ["P_THREAD", "P_EDGE", "P_PRESENT"]
    for pattern in RULES["patterns"]:
        if pattern["id"] in patterns:
            if set(pattern["requires"]) - set(patterns) or set(pattern["excludes"]) & set(patterns):
                raise ValueError(f"Unresolved pattern dependency/conflict: {pattern['id']}")
    # Weight 5 identity always precedes material; lower weights are optional by scope.
    active = {"identity", "texture", "hierarchy", "series", "originality", "photography", "aesthetic"}
    if brief["rhythm"] != "none":
        active.add("rhythm")
    if brief["text"]:
        active.add("text")
    lex = sorted((x for x in RULES["fbs_lexicon"] if x["scope"] in active),
                 key=lambda x: (-x["positive_weight"], x["id"]))
    by_id = {item["id"]: item for item in lex}
    # Reserve text behavior; then admit negative terms by quantified FBS priority.
    negative = list(card["avoid_features"]) + (["gibberish", "extra slogans"] if brief["text"] else ["text"])
    for item in sorted(lex, key=lambda x: (-x["negative_weight"], x["id"])):
        for term in item["negative"].split(", "):
            if term not in negative and len(negative) < 12:
                negative.append(term)
    lines = [
        "Use case: product-mockup.",
        f"One embroidered aircraft patch depicting {card['name']}.",
        "Identity lock: " + "; ".join(card["features"]) + ".",
        RULES["compositions"][brief["composition"]]["prompt"].format(heading=brief["heading"]),
        f"A {RULES['shapes'][brief['shape']]} patch; {by_id['F03']['positive']}; aircraft spans 65–78% of inner width.",
        concept["prompt"],
        by_id["F02"]["positive"].capitalize() + ", rim about 3% of patch width.",
        RULES["rhythms"][brief["rhythm"]]["prompt"],
        RULES["palettes"][brief["palette"]]["prompt"],
        (f'Only label: "{brief["text"]}", small block letters below the aircraft.' if brief["text"] else "No lettering."),
        f"Front near-overhead product photograph on white; soft side light, faint contact shadow; complete rim with 8% outer margin. Image ratio {brief['ratio']}.",
    ]
    for i, ref in enumerate(refs, 1):
        purpose = ("aircraft geometry only; preserve identity locks" if ref["role"] == "geometry" else
                   "thread and rim texture only; do not copy its subject, text or layout")
        lines.append(f"Input image {i}: {purpose}.")
    lines.append("Avoid: " + ", ".join(negative) + ".")
    prompt = "\n".join(line for line in lines if line)
    words = len(prompt.split())
    if words > RULES["prompt_word_budget"]:
        raise ValueError(f"Prompt exceeds {RULES['prompt_word_budget']} words ({words}); shorten subject card; never drop identity locks")
    design = {"version": RULES["version"], "brief": brief, "identity_lock": card,
              "patterns": patterns, "priority": RULES["priority"], "adjustments": adjustments,
              "fbs_selection": lex, "word_count": words, "visual_validation": "not_run",
              "aesthetic_plan": {k: concept[k] for k in ("name", "function", "contrast", "source_patterns", "omit", "gesture")},
              "image_generated": False, "weight_semantics": "selection priority; no model-native numerical weighting"}
    request = {"kind": "host-agent-call-plan", "preferred_tool": "image_gen.imagegen", "prompt": prompt,
               "references_to_inspect_and_pass": refs, "transparent_background": False,
               "note": "Inspect current tool schema; this file is not an API request. Host must call the tool."}
    return prompt, design, request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = json.loads(args.brief.read_text(encoding="utf-8"))
        prompt, design, request = compile_brief(raw)
        args.out.mkdir(parents=True, exist_ok=True)
        paths = [args.out / f for f in ("prompt.txt", "design.json", "request.json")]
        if any(p.exists() for p in paths):
            raise ValueError("Refusing to overwrite existing outputs; choose a new job directory")
        # Exclusive creation also protects an output created between the check and write.
        payloads = [prompt + "\n", json.dumps(design, ensure_ascii=False, indent=2) + "\n",
                    json.dumps(request, ensure_ascii=False, indent=2) + "\n"]
        created = []
        try:
            for path, payload in zip(paths, payloads):
                with path.open("x", encoding="utf-8") as fh:
                    created.append(path)
                    fh.write(payload)
        except OSError:
            for path in created:
                path.unlink(missing_ok=True)
            raise
        print(json.dumps({"out": str(args.out.resolve()), "words": design["word_count"],
                          "adjustments": design["adjustments"], "image_generated": False}, ensure_ascii=False))
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
