#!/usr/bin/env python3
"""Read-only Buildkite receipt generator for the Harmonious Merge Protocol."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path

PROTECTED_EXACT = {"main", "master", "develop", "development", "production", "prod", "staging"}
PROTECTED_PREFIXES = ("release/", "hotfix/")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def is_protected(branch: str) -> bool:
    return branch in PROTECTED_EXACT or branch.startswith(PROTECTED_PREFIXES)


def ref_list(prefix: str) -> list[tuple[str, str]]:
    output = git("for-each-ref", "--format=%(refname:short)\t%(objectname)", prefix)
    refs: list[tuple[str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        name, sha = line.split("\t", 1)
        if prefix == "refs/remotes/origin":
            if name == "origin/HEAD":
                continue
            name = name.removeprefix("origin/")
        refs.append((name, sha))
    return refs


def branch_record(name: str, sha: str, baseline: str) -> dict[str, object]:
    try:
        merge_base = git("merge-base", baseline, sha)
        counts = git("rev-list", "--left-right", "--count", f"{baseline}...{sha}").split()
        behind, ahead = (int(counts[0]), int(counts[1]))
        merged = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, baseline],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        evidence_status = "complete"
    except subprocess.CalledProcessError:
        merge_base, behind, ahead, merged, evidence_status = None, None, None, False, "incomplete"

    disposition = "preserve_pending_human_value_review"
    if evidence_status != "complete":
        disposition = "block_incomplete_evidence"
    elif name == baseline or is_protected(name):
        disposition = "preserve_protected"
    elif merged:
        disposition = "eligible_for_approved_retirement_review"

    return {
        "name": name,
        "sha": sha,
        "protected": is_protected(name),
        "merge_base": merge_base,
        "ahead_of_baseline": ahead,
        "behind_baseline": behind,
        "merged_into_baseline": merged,
        "evidence_status": evidence_status,
        "disposition": disposition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default=os.environ.get("HARMONIOUS_MERGE_BASELINE", "main"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    baseline_sha = git("rev-parse", args.baseline)
    branches = [branch_record(name, sha, args.baseline) for name, sha in ref_list("refs/remotes/origin")]
    if not branches:
        branches = [branch_record(name, sha, args.baseline) for name, sha in ref_list("refs/heads")]
    tags = [{"name": name, "sha": sha} for name, sha in ref_list("refs/tags")]

    divergent = [b for b in branches if b["evidence_status"] == "complete" and b["ahead_of_baseline"] not in (None, 0)]
    incomplete = [b for b in branches if b["evidence_status"] != "complete"]
    status = "REQUIRES_HUMAN_HARMONIZATION" if divergent or incomplete else "NO_DIVERGENT_BRANCHES_DETECTED"

    receipt = {
        "schema": "glaciereq.harmonious-merge-watch.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "mode": "read_only",
        "baseline": {"name": args.baseline, "sha": baseline_sha},
        "build": {
            "branch": os.environ.get("BUILDKITE_BRANCH"),
            "commit": os.environ.get("BUILDKITE_COMMIT"),
            "url": os.environ.get("BUILDKITE_BUILD_URL"),
        },
        "status": status,
        "branches": branches,
        "tags": tags,
        "summary": {
            "branch_count": len(branches),
            "tag_count": len(tags),
            "divergent_branch_count": len(divergent),
            "incomplete_evidence_count": len(incomplete),
        },
        "enforcement": {
            "automatic_merge": False,
            "automatic_ref_deletion": False,
            "automatic_tag_mutation": False,
            "automatic_history_rewrite": False,
            "next_action": "Conduct an evidence-backed, human-approved Harmonious Merge Audit for every divergent or incomplete branch.",
        },
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
