#!/usr/bin/env python3
"""Reveal and compare only after receiving complete real human ratings."""
import argparse
import hashlib
import json
from pathlib import Path

DIMENSIONS = ("structure", "omission", "color", "angle", "text", "series")
R4_WEIGHTS = {"structure": 3, "series": 3, "originality": 3, "aesthetic": 2, "text": 1}
R4_CORE = ("structure", "series", "originality")
R5_WEIGHTS = {"simplification": 3, "integration": 3, "series": 3, "aesthetic": 2, "originality": 3}
R5_CORE = ("simplification", "integration", "series", "originality")


def commitment(key):
    return hashlib.sha256(json.dumps(key, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def compare(ratings, key):
    if not isinstance(ratings, dict) or not isinstance(key, dict):
        raise ValueError("Ratings and frozen key must be objects")
    if key.get("rubric_version") in {"r4", "r5"}:
        return compare_r4(ratings, key)
    if ratings.get("qa") is True:
        raise ValueError("QA exports are not real human ratings")
    if ratings.get("session") != key.get("session") or ratings.get("assignment_commitment_sha256") != commitment(key):
        raise ValueError("Session or assignment commitment mismatch")
    values = ratings.get("ratings")
    if not isinstance(values, dict) or set(values) != set("ABCDEF"):
        raise ValueError("Require exactly six anonymous entries A-F")
    for label, scores in values.items():
        if not isinstance(scores, dict) or set(scores) - set(DIMENSIONS) - {"comment"}:
            raise ValueError(f"Unknown rating fields for {label}")
        for dimension in DIMENSIONS:
            score = scores.get(dimension)
            if type(score) is not int or not 1 <= score <= 5:
                raise ValueError(f"Incomplete/invalid human rating: {label}.{dimension}; no verdict can be issued")
        if not isinstance(scores.get("comment", ""), str):
            raise ValueError("Comment must be text")
    jobs = key.get("jobs", [])
    if len(jobs) != 6 or {j.get("label") for j in jobs} != set("ABCDEF"):
        raise ValueError("Invalid frozen assignment")
    pairs = {}
    for job in jobs:
        if job.get("version") not in {"baseline", "candidate"}:
            raise ValueError("Unknown frozen version")
        pair = pairs.setdefault(job["task_id"], {})
        if job["version"] in pair:
            raise ValueError("Duplicate task/version assignment")
        score = values[job["label"]]
        pair[job["version"]] = {"label": job["label"], "mean": sum(score[d] for d in DIMENSIONS) / 6,
                                 "scores": {d: score[d] for d in DIMENSIONS}}
    if len(pairs) != 3 or any(set(pair) != {"baseline", "candidate"} for pair in pairs.values()):
        raise ValueError("Need three complete matched pairs")
    rows = []
    for task, pair in sorted(pairs.items()):
        delta = pair["candidate"]["mean"] - pair["baseline"]["mean"]
        rows.append({"task": task, **pair, "delta": round(delta, 4),
                     "winner": "candidate" if delta > 1e-9 else ("baseline" if delta < -1e-9 else "tie")})
    by_version = {v: {d: sum(pair[v]["scores"][d] for pair in pairs.values()) / 3 for d in DIMENSIONS}
                  for v in ("baseline", "candidate")}
    old_mean = sum(by_version["baseline"].values()) / 6
    new_mean = sum(by_version["candidate"].values()) / 6
    wins = sum(row["winner"] == "candidate" for row in rows)
    structure_ok = by_version["candidate"]["structure"] >= by_version["baseline"]["structure"]
    no_structure_one = all(pair["candidate"]["scores"]["structure"] != 1 for pair in pairs.values())
    improved = wins >= 2 and new_mean - old_mean >= 0.5 - 1e-9 and structure_ok and no_structure_one
    return {"session": key["session"], "status": "scored", "pairs": rows, "dimension_means": by_version,
            "baseline_mean": round(old_mean, 4), "candidate_mean": round(new_mean, 4),
            "delta": round(new_mean - old_mean, 4), "candidate_paired_wins": wins,
            "structure_not_degraded": structure_ok, "no_candidate_structure_one": no_structure_one,
            "iteration_success_under_preregistered_rule": improved,
            "scope": "This three-task single-blind sample only; no statistical significance or generalization claim."}


def compare_r4(ratings, key):
    """Fixed five-pair protocol; incomplete scores never reveal the assignment."""
    rubric = key["rubric_version"]
    weights, core = (R5_WEIGHTS, R5_CORE) if rubric == "r5" else (R4_WEIGHTS, R4_CORE)
    divisor = sum(weights.values())
    if ratings.get("qa") is True or ratings.get("rubric_version") != rubric:
        raise ValueError("Require real human scores for the frozen rubric")
    if ratings.get("session") != key.get("session") or ratings.get("assignment_commitment_sha256") != commitment(key):
        raise ValueError("Session or assignment commitment mismatch")
    values = ratings.get("ratings")
    if not isinstance(values, dict) or set(values) != set("ABCDEFGHIJ"):
        raise ValueError("Require ten anonymous entries A-J")
    for label, scores in values.items():
        if not isinstance(scores, dict) or set(scores) != set(weights):
            raise ValueError("Require exactly the five frozen dimensions")
        if any(type(n) is not int or not 1 <= n <= 5 for n in scores.values()):
            raise ValueError(f"Incomplete/invalid human rating for {label}; no verdict can be issued")
    jobs = key.get("jobs", [])
    if len(jobs) != 10 or {j.get("label") for j in jobs} != set(values):
        raise ValueError("Invalid frozen ten-image assignment")
    pairs = {}
    for job in jobs:
        version = job.get("version")
        pair = pairs.setdefault(job["task_id"], {})
        if version not in {"baseline", "candidate"} or version in pair:
            raise ValueError("Invalid/duplicate task-version assignment")
        scores = values[job["label"]]
        pair[version] = {"label": job["label"], "scores": scores,
                         "mean": sum(scores[d] * w for d, w in weights.items()) / divisor}
    if len(pairs) != 5 or any(set(p) != {"baseline", "candidate"} for p in pairs.values()):
        raise ValueError("Need five complete matched pairs")
    means = {v: {d: sum(p[v]["scores"][d] for p in pairs.values()) / 5 for d in weights}
             for v in ("baseline", "candidate")}
    totals = {v: sum(means[v][d] * w for d, w in weights.items()) / divisor for v in means}
    rows = []
    for task, pair in sorted(pairs.items()):
        delta = pair["candidate"]["mean"] - pair["baseline"]["mean"]
        rows.append({"task": task, **pair, "delta": delta,
                     "winner": "candidate" if delta > 1e-9 else ("baseline" if delta < -1e-9 else "tie")})
    checks = {
        "candidate_weighted_mean_at_least_4": totals["candidate"] >= 4 - 1e-9,
        "every_candidate_core_at_least_3": all(p["candidate"]["scores"][d] >= 3 for p in pairs.values() for d in core),
        "delta_at_least_0_3": totals["candidate"] - totals["baseline"] >= .3 - 1e-9,
        "each_core_mean_not_degraded": all(means["candidate"][d] >= means["baseline"][d] for d in core),
        "at_least_three_paired_wins": sum(r["winner"] == "candidate" for r in rows) >= 3,
    }
    return {"session": key["session"], "rubric_version": rubric, "status": "scored", "pairs": rows,
            "dimension_means": means, "baseline_mean": totals["baseline"], "candidate_mean": totals["candidate"],
            "delta": totals["candidate"] - totals["baseline"], "checks": checks,
            "candidate_accepted": checks["candidate_weighted_mean_at_least_4"] and checks["every_candidate_core_at_least_3"],
            "iteration_success_under_preregistered_rule": all(checks.values()),
            "scope": "This five-task single-blind sample only; no statistical significance or generalization claim."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ratings", type=Path)
    ap.add_argument("--key", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    try:
        result = compare(json.loads(a.ratings.read_text()), json.loads(a.key.read_text()))
        a.out.parent.mkdir(parents=True, exist_ok=True)
        with a.out.open("x", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(json.dumps({"status": "scored", "output": str(a.out.resolve())}))
    except (ValueError, OSError, TypeError, KeyError) as e:
        ap.exit(2, f"ERROR: {e}\n")


if __name__ == "__main__":
    main()
