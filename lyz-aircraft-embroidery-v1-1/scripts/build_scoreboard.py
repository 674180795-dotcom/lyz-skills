#!/usr/bin/env python3
"""Render a blind page from public-only metadata; never reads the version key."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def relative_image(value):
    if not isinstance(value, str):
        raise ValueError("Image path must be text")
    p = Path(value)
    if p.is_absolute() or ".." in p.parts or ":" in value or p.suffix not in {".png", ".webp", ".jpg", ".jpeg"}:
        raise ValueError("Use relative public image paths")


def render_review(data):
    if set(data) != {"session_id", "rubric_version", "title", "intro", "criteria", "cases"}:
        raise ValueError("Review data must not contain extra/private fields")
    if data["rubric_version"] != "r2" or len(data["criteria"]) != 5:
        raise ValueError("Require the frozen r2 five-criterion rubric")
    expected = [("structure", 3, True), ("series", 3, True), ("color", 2, False),
                ("angle", 2, False), ("text", 1, False)]
    for criterion, (name, weight, critical) in zip(data["criteria"], expected):
        if set(criterion) != {"id", "label", "weight", "critical", "target", "anchors"}:
            raise ValueError("Unknown criterion fields")
        if (criterion["id"], criterion["weight"], criterion["critical"]) != (name, weight, critical):
            raise ValueError("Frozen r2 criterion order/weight/core flag changed")
        if set(criterion["anchors"]) != {"1", "3", "5"}:
            raise ValueError("Unknown anchor fields")
    if len(data["cases"]) != 3:
        raise ValueError("Require three matched tasks")
    labels = []
    for case in data["cases"]:
        if set(case) != {"id", "title", "prompt", "references", "variants"} or len(case["variants"]) != 2:
            raise ValueError("Unknown public task fields or unmatched variants")
        for ref in case["references"]:
            if set(ref) != {"id", "image"}:
                raise ValueError("Unknown reference fields")
            relative_image(ref["image"])
        for variant in case["variants"]:
            if set(variant) != {"id", "content", "image", "links"} or variant["links"]:
                raise ValueError("Use anonymous images without private links")
            labels.append(variant["id"])
            relative_image(variant["image"])
    if sorted(labels) != list("ABCDEF"):
        raise ValueError("Require six unique anonymous labels A-F")
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    template = (ROOT / "assets/human-scorecard.html").read_text(encoding="utf-8")
    return re.sub(r'(<script type="application/json" id="review-data">)[\s\S]*?(</script>)',
                  lambda m: m[1] + "\n" + encoded + "\n" + m[2], template, count=1)


def render(data):
    if "rubric_version" in data:
        return render_review(data)
    if set(data) != {"session", "assignment_commitment_sha256", "cases", "items"}:
        raise ValueError("Public manifest must not contain extra/private fields")
    if {i.get("label") for i in data["items"]} != set("ABCDEF") or len(data["items"]) != 6:
        raise ValueError("Require exactly six anonymous images")
    for item in data["items"]:
        if set(item) != {"label", "task_id", "image"}:
            raise ValueError("Anonymous item may contain only label/task_id/image")
        p = Path(item["image"])
        if p.is_absolute() or ".." in p.parts or p.suffix != ".png":
            raise ValueError("Use relative anonymous PNG filenames")
    for case in data["cases"]:
        if set(case) != {"id", "title", "label", "references"}:
            raise ValueError("Unknown public case fields")
        for reference in case["references"]:
            if set(reference) != {"id", "image"}:
                raise ValueError("Unknown reference fields")
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return (ROOT/'assets/scoreboard-template.html').read_text(encoding='utf-8').replace('__PUBLIC_DATA__', encoded)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    try:
        result = render(json.loads(a.manifest.read_text(encoding='utf-8')))
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(result, encoding='utf-8')
        print(json.dumps({'output':str(a.out.resolve()),'version_key_read':False}))
    except (OSError, ValueError, KeyError, TypeError) as e:
        ap.exit(2, f'ERROR: {e}\n')


if __name__=='__main__': main()
