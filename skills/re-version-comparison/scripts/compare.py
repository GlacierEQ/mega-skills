#!/usr/bin/env python3
"""Version-comparison discipline: inventories, dimensions, claim scope.

Local mirror of the rules REA's comparison tools enforce (verified live
on 6.7.0):
- Inputs must be COMPLETE evidence records of the right class. An
  artifact comparison cannot feed a behavior question - find_changed_
  behavior rejects it; a summary or partial record is refused, not
  approximated.
- Static changes are candidates. Only runtime corroboration promotes a
  candidate to an observed behavior change (correlation), and REA keeps
  the two counts separate forever.
- A comparison's dimensions bound its conclusions: claim scope is part
  of the record, not a narrative choice.
"""
from __future__ import annotations

import hashlib


def diff_inventories(left: list[dict], right: list[dict]) -> dict:
    """Diff two artifact inventories [{path, sha256}] by identity."""
    lmap = {entry["path"]: entry["sha256"] for entry in left}
    rmap = {entry["path"]: entry["sha256"] for entry in right}
    added = sorted(set(rmap) - set(lmap))
    removed = sorted(set(lmap) - set(rmap))
    changed = sorted(p for p in set(lmap) & set(rmap) if lmap[p] != rmap[p])
    unchanged = sorted(p for p in set(lmap) & set(rmap) if lmap[p] == rmap[p])
    return {"added": added, "removed": removed, "changed": changed,
            "unchanged": unchanged,
            "summary": {"added": len(added), "removed": len(removed),
                        "changed": len(changed), "unchanged": len(unchanged)}}


def require_complete(records: list[dict]) -> None:
    """Refuse partial inputs: every record must carry its full result,
    not a summary projection. Raises ValueError naming the gap."""
    for record in records:
        if record.get("summary_only") or "normalized_result" not in record:
            raise ValueError(
                "comparison inputs must be complete evidence records; "
                "a summary projection is refused (pass the full record)")


def check_claim_scope(comparison: dict, claim_kind: str) -> dict:
    """Decide whether a comparison supports a claim of the given kind.
    Artifact comparisons describe membership/content; behavior claims
    require process/function comparisons."""
    comparison_class = comparison.get("comparison_class")
    behavior_classes = {"process", "function"}
    if claim_kind == "behavior" and comparison_class not in behavior_classes:
        return {"supported": False,
                "reason": f"a {comparison_class} comparison cannot support a behavior claim; "
                          "run a process or function comparison"}
    if claim_kind == "membership" and comparison_class != "artifact":
        return {"supported": False,
                "reason": "membership claims require an artifact comparison"}
    return {"supported": True, "reason": f"{comparison_class} comparison supports {claim_kind} claims "
                                          f"within dimensions {sorted(comparison.get('dimensions', {}))}"}


def find_changed_behavior(comparisons: list[dict], runtime_comparisons: list[dict]) -> dict:
    """Separate static candidates from observed changes: a static
    difference becomes an observed behavior change only when a runtime
    comparison corroborates the same dimension."""
    candidates = 0
    observed = 0
    for comparison in comparisons:
        for dimension, verdict in comparison.get("dimensions", {}).items():
            if verdict == "changed":
                candidates += 1
                corroborated = any(
                    rt.get("dimensions", {}).get(dimension) == "changed"
                    for rt in runtime_comparisons)
                if corroborated:
                    observed += 1
    return {"static_candidates": candidates,
            "observed_changes": observed,
            "unresolved": candidates - observed,
            "rule": "static differences are candidates; runtime corroboration promotes them"}


def inventory_digest(entries: list[dict]) -> str:
    canonical = "|".join(f"{e['path']}:{e['sha256']}" for e in sorted(entries, key=lambda e: e["path"]))
    return hashlib.sha256(canonical.encode()).hexdigest()


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Diff two inventories given as JSON files.")
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args(argv)
    result = diff_inventories(json.load(open(args.left)), json.load(open(args.right)))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
