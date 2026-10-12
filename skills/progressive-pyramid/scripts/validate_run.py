#!/usr/bin/env python3
"""Deterministic Progressive Pyramid handoff and finish-line validation.

This checks the *shape* of a mission's evidence. Terminal verification requires
an independent provider-aware verifier passed by the host. A self-declared
"verified" flag never makes a mission complete.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

STAGES = (("corner_1_context", "V1"), ("corner_2_objective", "V2"),
          ("corner_3_constraints", "V3"), ("corner_4_resources", "V4"))
STATUSES = {"ACTIVE", "BLOCKED", "MISSION_COMPLETE"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_run(run: dict[str, Any], contract: dict[str, Any], *,
                 verifier: Callable[[str, str], bool] | None = None) -> list[str]:
    """Return explicit violations; never infer provider truth from a JSON receipt."""
    errors: list[str] = []
    if not isinstance(run, dict) or not isinstance(contract, dict):
        return ["run and contract must be JSON objects"]
    if run.get("protocol") != contract.get("schema_id"):
        errors.append("protocol does not match canonical contract")
    for name in ("mission_id", "original_outcome"):
        if not _nonempty(run.get(name)):
            errors.append(f"missing {name}")
    sources = run.get("recovered_sources")
    if not isinstance(sources, list) or not sources or not all(map(_nonempty, sources)):
        errors.append("recovered_sources must contain source references")
    criteria = run.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria or not all(map(_nonempty, criteria)) or len(criteria) != len(set(criteria)):
        errors.append("acceptance_criteria must contain distinct nonempty IDs")
        criteria = []
    stages = run.get("stages")
    if not isinstance(stages, list) or len(stages) != len(STAGES):
        errors.append("four ordered stages are required")
        stages = []
    previous_artifact = None
    previous_gains: set[str] = set()
    for i, (expected_stage, expected_version) in enumerate(STAGES):
        if i >= len(stages):
            break
        record = stages[i]
        if not isinstance(record, dict):
            errors.append(f"{expected_version} must be an object")
            continue
        if record.get("stage") != expected_stage or record.get("version") != expected_version:
            errors.append(f"{expected_version} stage order/name mismatch")
        ref = record.get("artifact_ref")
        if not _nonempty(ref):
            errors.append(f"{expected_version} missing artifact_ref")
        if record.get("inherits") != previous_artifact:
            errors.append(f"{expected_version} inheritance link is broken")
        gains = record.get("verified_gains")
        if not isinstance(gains, list) or not all(map(_nonempty, gains)):
            errors.append(f"{expected_version} verified_gains must be an array of IDs")
            gains = []
        if not previous_gains.issubset(set(gains)):
            errors.append(f"{expected_version} lost inherited verified gain IDs")
        previous_gains = set(gains)
        previous_artifact = ref
    center = run.get("center_point")
    if not isinstance(center, dict):
        return errors + ["center_point must be an object"]
    status = center.get("status")
    if status not in STATUSES:
        errors.append("center_point has invalid status")
    if status == "BLOCKED" and not center.get("blockers"):
        errors.append("BLOCKED requires recorded blocker(s)")
    if status == "MISSION_COMPLETE":
        proofs = center.get("outcome_proofs")
        if not isinstance(proofs, list) or not proofs:
            errors.append("MISSION_COMPLETE requires outcome proofs")
            proofs = []
        seen: set[str] = set()
        for p in proofs:
            if not isinstance(p, dict):
                errors.append("outcome proof must be object")
                continue
            criterion, receipt = p.get("criterion"), p.get("source_ref")
            if criterion not in criteria or criterion in seen or not _nonempty(receipt):
                errors.append("outcome proof has missing/duplicate/unknown criterion or source_ref")
                continue
            seen.add(criterion)
            if verifier is None:
                errors.append(f"independent verifier missing for {criterion}")
            else:
                try:
                    if verifier(criterion, receipt) is not True:
                        errors.append(f"provider verification failed for {criterion}")
                except Exception as exc:
                    errors.append(f"provider verification failed for {criterion}: {type(exc).__name__}")
        if seen != set(criteria):
            errors.append("MISSION_COMPLETE missing proof for acceptance criteria")
    return errors


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("run", type=Path)
    cli.add_argument("--contract", type=Path, default=Path(__file__).resolve().parents[1] / "progressive_pyramid.contract.json")
    args = cli.parse_args()
    try:
        run = json.loads(args.run.read_text(encoding="utf-8"))
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        issues = validate_run(run, contract)
    except (OSError, ValueError, TypeError) as exc:
        issues = [f"invalid input: {exc}"]
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())
