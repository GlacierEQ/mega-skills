#!/usr/bin/env python3
"""Validate provider-side continuity without coupling generic CI to host-proof freshness.

The strict validator remains authoritative for host-aware execution. This CI surface
preserves every durable/provider integrity check while treating host freshness as an
informational lane that must be renewed by a host-capable executor.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import validate_deep_progress_latest as core

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "evidence/deep-progress-forge/LATEST.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate_host_integrity(pointer: dict, root: Path = ROOT, *, now: datetime | None = None) -> dict:
    binding = pointer.get("host_runtime_proof")
    if not isinstance(binding, dict):
        raise ValueError("host_runtime_proof is required for provider-state v4")
    rel = binding.get("path")
    if not isinstance(rel, str) or not rel.startswith("evidence/deep-progress-forge/"):
        raise ValueError("host runtime proof must stay inside forge evidence directory")
    path = root / rel
    if not path.is_file():
        raise ValueError(f"host runtime proof does not exist: {rel}")
    receipt = core.load_json(path)
    expected = binding.get("receipt_digest_sha256")
    if not isinstance(expected, str) or not HEX64.fullmatch(expected):
        raise ValueError("host runtime binding requires receipt_digest_sha256")
    if core.receipt_digest(receipt) != expected or receipt.get("receipt_digest_sha256") != expected:
        raise ValueError("host runtime receipt digest mismatch")
    observed = core.parse_utc(binding.get("observed_at"))
    due = core.parse_utc(binding.get("revalidate_after"))
    if due <= observed:
        raise ValueError("host runtime revalidate_after must be later than observed_at")
    executable_sha = binding.get("executable_sha256")
    if not isinstance(executable_sha, str) or not HEX64.fullmatch(executable_sha):
        raise ValueError("host runtime proof requires executable_sha256")
    if receipt.get("skills_bin_sha256") != executable_sha:
        raise ValueError("host runtime executable fingerprint disagrees with receipt")
    current = now or datetime.now(timezone.utc)
    fresh = current <= due
    return {
        "status": "PASS" if fresh else "STALE_HOST_LANE",
        "fresh": fresh,
        "observed_at": binding["observed_at"],
        "revalidate_after": binding["revalidate_after"],
        "executable_sha256": executable_sha,
        "policy": "host freshness is informational in generic provider CI; strict validator remains fail-closed",
    }


def validate_provider_ci(pointer: dict, root: Path = ROOT, *, now: datetime | None = None) -> dict:
    if pointer.get("stream") != "deep-progress-forge":
        raise ValueError("unexpected continuation stream")
    sequence = pointer.get("run_sequence")
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("run_sequence must be a positive integer")
    run_rel = pointer.get("current_run")
    if not isinstance(run_rel, str) or not run_rel.startswith("evidence/deep-progress-forge/") or run_rel.endswith("LATEST.json"):
        raise ValueError("current_run must identify a forge receipt")
    run_path = root / run_rel
    if not run_path.is_file():
        raise ValueError(f"current_run does not exist: {run_rel}")
    expected_commit = pointer.get("current_run_commit", "")
    if not core.HEX40.fullmatch(expected_commit):
        raise ValueError("current_run_commit must be a full Git SHA")
    actual_commit = core.git_last_change(run_path)
    if actual_commit != expected_commit:
        raise ValueError(f"current_run_commit drifted: pointer={expected_commit}, file={actual_commit}")

    receipt = core.load_json(run_path)
    missing = core.REQUIRED_LEDGER - set(receipt)
    if missing:
        raise ValueError(f"current run ledger incomplete: missing={sorted(missing)}")
    if receipt.get("stream") != pointer["stream"] or receipt.get("run_sequence") != sequence:
        raise ValueError("current run receipt disagrees with pointer")
    delta = receipt.get("objective_state_delta")
    if not isinstance(delta, dict) or delta.get("changed") is not True or not delta.get("before") or not delta.get("after"):
        raise ValueError("current run must prove an explicit objective-state delta")
    if receipt.get("next_executable_frontier") != pointer.get("next_executable_frontier"):
        raise ValueError("pointer frontier disagrees with current run receipt")
    if not receipt.get("verbatim_sources") or not receipt.get("durable_sources_changed") or not receipt.get("concrete_outputs"):
        raise ValueError("current run lacks source-bearing durable execution evidence")

    provider = core.validate_provider_state(pointer, root, now=now)
    host = validate_host_integrity(pointer, root, now=now)
    abandoned = core.validate_no_abandoned_renewal(root)
    renewal = core.validate_latest_renewal_chain(pointer, root)
    recovery = core.validate_latest_abandoned_recovery(pointer, root)
    return {
        "status": "PASS",
        "scope": "provider-ci",
        "run_sequence": sequence,
        "current_run": run_rel,
        "current_run_commit": actual_commit,
        "provider_state": provider,
        "host_runtime_integrity": host,
        "abandoned_renewal": abandoned,
        "proof_renewal_chain": renewal,
        "latest_abandoned_recovery": recovery,
        "next_executable_frontier": receipt["next_executable_frontier"],
    }


def main() -> int:
    history = core.ensure_repository_history(ROOT)
    result = validate_provider_ci(core.load_json(POINTER))
    result["repository_history"] = history
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
