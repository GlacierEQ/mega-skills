#!/usr/bin/env python3
"""Read-only fleet branch sprawl snapshot for GlacierEQ (or any GitHub owner).

Emits JSON suitable for branch-lifecycle-intelligence / harmonious-merge planning.
Does not delete or mutate remotes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def gh_json(args: list[str]) -> Any:
    proc = subprocess.run(
        ["gh", "api", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout or "null")


def list_owner_repos(owner: str, limit: int) -> list[dict[str, Any]]:
    proc = subprocess.run(
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            str(limit),
            "--json",
            "name,isArchived,isFork,defaultBranchRef",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def branch_count(owner: str, repo: str) -> tuple[int, str | None]:
    try:
        proc = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{owner}/{repo}/branches",
                "--paginate",
                "-q",
                ".[].name",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        names = [line for line in proc.stdout.splitlines() if line.strip()]
        default = None
        return len(names), default
    except subprocess.CalledProcessError:
        return -1, "branch_list_failed"


def open_pr_count(owner: str, repo: str) -> int:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            f"{owner}/{repo}",
            "--state",
            "open",
            "--json",
            "number",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return len(json.loads(proc.stdout))


def main() -> int:
    parser = argparse.ArgumentParser(description="Fleet branch sprawl snapshot (read-only)")
    parser.add_argument("--owner", default="GlacierEQ")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--output", help="Write JSON to path (default: stdout)")
    parser.add_argument(
        "--min-branches",
        type=int,
        default=2,
        help="Only include repos with more than this many branches (default: 2 = more than main only)",
    )
    args = parser.parse_args()

    repos = list_owner_repos(args.owner, args.limit)
    rows: list[dict[str, Any]] = []
    for row in repos:
        if row.get("isArchived") or row.get("isFork"):
            continue
        name = row["name"]
        count, err = branch_count(args.owner, name)
        if count < 0:
            rows.append(
                {
                    "repository": f"{args.owner}/{name}",
                    "branch_count": None,
                    "error": err,
                }
            )
            continue
        non_default = max(0, count - 1)
        if non_default < args.min_branches:
            continue
        try:
            open_prs = open_pr_count(args.owner, name)
        except subprocess.CalledProcessError:
            open_prs = None
        rows.append(
            {
                "repository": f"{args.owner}/{name}",
                "branch_count": count,
                "non_default_branch_count": non_default,
                "open_pull_requests": open_prs,
                "default_branch": (row.get("defaultBranchRef") or {}).get("name", "main"),
            }
        )

    rows.sort(key=lambda r: (-(r.get("non_default_branch_count") or 0), r["repository"]))
    report = {
        "schema": "glaciereq.fleet-branch-sprawl-snapshot.v1",
        "owner": args.owner,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repositories_scanned": len(repos),
        "repositories_with_sprawl": len(rows),
        "rows": rows,
        "routing": {
            "combo": "branch-sprawl-control-loop",
            "mega_when_multi_repo": "apex-fleet-harmonizer",
            "per_repo_combo": "fleet-recon-and-harmonize",
        },
    }
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())