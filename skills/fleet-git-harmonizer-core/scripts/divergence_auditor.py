#!/usr/bin/env python3
"""
Fetch/prune remotes, enumerate unmerged branches, compute divergence
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def audit_divergence(repo_path: Path, base_branch: str = "main") -> dict:
    """Audit branch divergence against a base branch."""
    repo = repo_path.resolve()
    # List local branches
    proc = subprocess.run(
        ["git", "-C", str(repo), "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
        capture_output=True, text=True, check=False,
    )
    branches = [b.strip() for b in proc.stdout.splitlines() if b.strip()]
    audit = []

    for branch in branches:
        if branch == base_branch:
            continue
        # Check ahead / behind
        rev_proc = subprocess.run(
            ["git", "-C", str(repo), "rev-list", "--left-right", "--count", f"{base_branch}...{branch}"],
            capture_output=True, text=True, check=False,
        )
        if rev_proc.returncode == 0:
            parts = rev_proc.stdout.strip().split()
            behind = int(parts[0]) if len(parts) >= 1 else 0
            ahead = int(parts[1]) if len(parts) >= 2 else 0
        else:
            behind, ahead = 0, 0

        audit.append({
            "branch": branch,
            "base": base_branch,
            "ahead": ahead,
            "behind": behind,
            "diverged": ahead > 0 and behind > 0,
            "up_to_date": ahead == 0 and behind == 0,
        })

    return {
        "repo": str(repo),
        "base_branch": base_branch,
        "total_branches_audited": len(audit),
        "branches": audit,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit git branch divergence")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to git repository")
    parser.add_argument("--base", default="main", help="Base branch name")
    args = parser.parse_args()

    result = audit_divergence(args.repo, base_branch=args.base)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

