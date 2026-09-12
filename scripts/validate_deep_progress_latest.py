#!/usr/bin/env python3
"""Fail closed when the Deep Progress Forge continuation pointer drifts."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "evidence" / "deep-progress-forge" / "LATEST.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_LEDGER = {
    "stream", "run_sequence", "verbatim_sources", "failure_pattern_attacked",
    "durable_sources_changed", "concrete_outputs", "verification",
    "objective_state_delta", "unresolved", "next_executable_frontier",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_last_change(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(rel)],
        cwd=ROOT, text=True,
    ).strip()


def validate_pointer(
    pointer: dict,
    root: Path = ROOT,
    commit_lookup: Callable[[Path], str] | None = None,
) -> dict:
    if pointer.get("stream") != "deep-progress-forge":
        raise ValueError("unexpected continuation stream")
    sequence = pointer.get("run_sequence")
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("run_sequence must be a positive integer")
    run_rel = pointer.get("current_run")
    if not isinstance(run_rel, str) or not run_rel.startswith("evidence/deep-progress-forge/"):
        raise ValueError("current_run must stay inside the forge evidence directory")
    if run_rel.endswith("LATEST.json"):
        raise ValueError("LATEST.json cannot point to itself")
    run_path = root / run_rel
    if not run_path.is_file():
        raise ValueError(f"current_run does not exist: {run_rel}")
    expected_commit = pointer.get("current_run_commit", "")
    if not HEX40.fullmatch(expected_commit):
        raise ValueError("current_run_commit must be a full Git SHA")
    lookup = commit_lookup or git_last_change
    actual_commit = lookup(run_path)
    if actual_commit != expected_commit:
        raise ValueError(
            f"current_run_commit drifted: pointer={expected_commit}, file={actual_commit}"
        )

    receipt = load_json(run_path)
    missing = REQUIRED_LEDGER - set(receipt)
    if missing:
        raise ValueError(f"current run ledger incomplete: missing={sorted(missing)}")
    if receipt["stream"] != pointer["stream"]:
        raise ValueError("current run stream disagrees with pointer")
    if receipt["run_sequence"] != sequence:
        raise ValueError("current run sequence disagrees with pointer")
    delta = receipt.get("objective_state_delta")
    if not isinstance(delta, dict) or delta.get("changed") is not True:
        raise ValueError("current run must prove objective_state_delta.changed=true")
    if not delta.get("before") or not delta.get("after"):
        raise ValueError("objective-state delta requires explicit before/after state")
    if receipt["next_executable_frontier"] != pointer.get("next_executable_frontier"):
        raise ValueError("pointer frontier disagrees with current run receipt")
    if not receipt["verbatim_sources"]:
        raise ValueError("current run must preserve verbatim source excerpts")
    if not receipt["durable_sources_changed"] or not receipt["concrete_outputs"]:
        raise ValueError("current run must contain durable mutation and concrete outputs")
    return {
        "status": "PASS",
        "run_sequence": sequence,
        "current_run": run_rel,
        "current_run_commit": actual_commit,
        "next_executable_frontier": receipt["next_executable_frontier"],
    }


def main() -> int:
    result = validate_pointer(load_json(POINTER))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
