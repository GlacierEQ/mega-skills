#!/usr/bin/env python3
"""
Delete merged/archived branches locally and remotely
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROTECTED_BRANCHES = {"main", "master", "develop", "production"}


def prune_merged_branches(repo_path: Path, base_branch: str = "main", dry_run: bool = True) -> dict:
    """Identify and safely prune branches already merged into base."""
    repo = repo_path.resolve()
    proc = subprocess.run(
        ["git", "-C", str(repo), "branch", "--merged", base_branch],
        capture_output=True, text=True, check=False,
    )
    candidates = []
    for line in proc.stdout.splitlines():
        b = line.strip().lstrip("* ")
        if b and b not in PROTECTED_BRANCHES and b != base_branch:
            candidates.append(b)

    deleted = []
    if not dry_run:
        for b in candidates:
            del_proc = subprocess.run(
                ["git", "-C", str(repo), "branch", "-d", b],
                capture_output=True, text=True, check=False,
            )
            if del_proc.returncode == 0:
                deleted.append(b)

    return {
        "repo": str(repo),
        "base_branch": base_branch,
        "merged_candidates": candidates,
        "deleted": deleted if not dry_run else [],
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="Prune merged branches safely")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to repository")
    parser.add_argument("--base", default="main", help="Base branch")
    parser.add_argument("--apply", action="store_true", help="Actually delete branches")
    args = parser.parse_args()

    result = prune_merged_branches(args.repo, base_branch=args.base, dry_run=not args.apply)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

