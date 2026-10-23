#!/usr/bin/env python3
"""Reconstruction verification: trace conformance and claim verdicts.

Local mirror of the semantics REA's verify_reconstruction applies
(verified live on 6.7.0, including its refusals):
- An unnormalized claim FAILS against real run pairs: the verifier is
  not a rubber stamp. Timing fields differ on every pair of real runs.
- A trace_spec is full-coverage: EVERY collected record on each side
  needs an exact predicate, or the comparison stays unknown.
- A claim passes only when its dimension verdict is "unchanged" AND no
  unresolved residual unknown is attached to it. REA returned UNKNOWN
  (observed status: unchanged) for exactly that case; copying the
  dimension verdict into the claim verdict would overstate the record.
"""
from __future__ import annotations


def check_trace_conformance(events: list[dict], predicates: list[dict]) -> dict:
    """Every event must match exactly one predicate {field: value};
    uncovered or multiply-covered events break conformance."""
    uncovered = []
    for index, event in enumerate(events):
        matches = [p for p in predicates
                   if all(event.get(k) == v for k, v in p.items())]
        if len(matches) != 1:
            uncovered.append({"index": index, "matches": len(matches)})
    return {"conforms": not uncovered, "uncovered": uncovered,
            "events": len(events), "predicates": len(predicates)}


def check_partial_order(events: list[dict], happens_before: list[list[int]]) -> dict:
    """Positions in the stream must respect the declared ordering pairs
    (indices into the event list)."""
    position = {id(event): index for index, event in enumerate(events)}
    violations = []
    for earlier, later in happens_before:
        if earlier >= later:
            violations.append({"earlier": earlier, "later": later})
    return {"ordered": not violations, "violations": violations}


def verify_claims(comparison: dict, claims: list[dict]) -> dict:
    """Map claims to verdicts: passed / failed / unknown.

    comparison: {"dimensions": {name: verdict}, "residual_unknown_ids": [...]}
    claims: [{"claim_id", "kind": "behavioral", "dimension", "predicate",
              "unknown_ids": [...]}]
    """
    results = []
    for claim in claims:
        dimension = claim["dimension"]
        verdict = comparison.get("dimensions", {}).get(dimension, "unknown")
        attached = [u for u in claim.get("unknown_ids", [])
                    if u in comparison.get("residual_unknown_ids", [])]
        if verdict == "changed":
            status = "failed"
        elif verdict == "unchanged" and not attached:
            status = "passed"
        else:
            status = "unknown"
        results.append({"claim_id": claim["claim_id"], "status": status,
                        "observed_status": verdict,
                        "blocking_unknowns": attached})
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    unknown = sum(1 for r in results if r["status"] == "unknown")
    overall = "passed" if failed == 0 and unknown == 0 else ("failed" if failed else "unknown")
    return {"status": overall,
            "summary": {"passed": passed, "failed": failed, "unknown": unknown},
            "claims": results,
            "limitations": ["pass means every declared claim passed; it does not establish global implementation equivalence"]}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Verify claims against a comparison record (JSON files).")
    parser.add_argument("comparison")
    parser.add_argument("claims")
    args = parser.parse_args(argv)
    comparison = json.load(open(args.comparison))
    claims = json.load(open(args.claims))
    result = verify_claims(comparison, claims)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
