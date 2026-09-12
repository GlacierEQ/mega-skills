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
CURRENT_REPO = "GlacierEQ/mega-skills"
PROVIDER_STATE_SCHEMA_VERSION = 2
PROVIDER_TYPES = {"repo_commit", "cross_repo_commit", "blob"}
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


def git_commit_reachable(sha: str, root: Path = ROOT) -> bool:
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=root, capture_output=True, text=True,
    )
    if exists.returncode != 0:
        return False
    reachable = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=root, capture_output=True, text=True,
    )
    return reachable.returncode == 0


def validate_provider_state(
    pointer: dict,
    root: Path = ROOT,
    commit_reachable: Callable[[str, Path], bool] | None = None,
) -> dict:
    version = pointer.get("provider_state_schema_version")
    if version is None:
        return {"status": "LEGACY", "checked": 0}
    if version != PROVIDER_STATE_SCHEMA_VERSION:
        raise ValueError(
            f"provider_state_schema_version must be {PROVIDER_STATE_SCHEMA_VERSION}"
        )
    state = pointer.get("verified_provider_state")
    if not isinstance(state, dict) or not state:
        raise ValueError("verified_provider_state must be a non-empty object")
    lookup = commit_reachable or git_commit_reachable
    checked = 0
    same_repo_commits = 0
    for name, entry in state.items():
        if not isinstance(entry, dict):
            raise ValueError(f"provider state {name} must be a typed object")
        kind = entry.get("type")
        repo = entry.get("repo")
        sha = entry.get("sha")
        if kind not in PROVIDER_TYPES:
            raise ValueError(f"provider state {name} has unsupported type={kind!r}")
        if not isinstance(repo, str) or "/" not in repo:
            raise ValueError(f"provider state {name} requires owner/repo")
        if not isinstance(sha, str) or not HEX40.fullmatch(sha):
            raise ValueError(f"provider state {name} requires a full 40-hex SHA")
        if kind == "repo_commit":
            if repo != CURRENT_REPO:
                raise ValueError(
                    f"provider state {name} repo_commit must target {CURRENT_REPO}; "
                    "use cross_repo_commit for external repositories"
                )
            if not lookup(sha, root):
                raise ValueError(
                    f"provider state {name} commit is not reachable from repository HEAD: {sha}"
                )
            same_repo_commits += 1
        elif kind == "cross_repo_commit" and repo == CURRENT_REPO:
            raise ValueError(
                f"provider state {name} cannot classify a same-repository commit as cross_repo_commit"
            )
        checked += 1
    if same_repo_commits == 0:
        raise ValueError("provider state v2 must contain at least one reachable same-repository commit")
    return {"status": "PASS", "checked": checked, "same_repo_commits": same_repo_commits}


def validate_pointer(
    pointer: dict,
    root: Path = ROOT,
    commit_lookup: Callable[[Path], str] | None = None,
    provider_commit_reachable: Callable[[str, Path], bool] | None = None,
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
    provider_result = validate_provider_state(
        pointer, root, provider_commit_reachable
    )
    return {
        "status": "PASS",
        "run_sequence": sequence,
        "current_run": run_rel,
        "current_run_commit": actual_commit,
        "provider_state": provider_result,
        "next_executable_frontier": receipt["next_executable_frontier"],
    }


def main() -> int:
    result = validate_pointer(load_json(POINTER))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
