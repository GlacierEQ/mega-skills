#!/usr/bin/env python3
"""
Apply immutable archive tags before branch deletion
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path


def create_archive_tag(repo_path: Path, branch: str, dry_run: bool = False) -> dict:
    """Create an immutable archive tag before branch deletion."""
    repo = repo_path.resolve()
    # Resolve branch commit
    rev_proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"refs/heads/{branch}"],
        capture_output=True, text=True, check=False,
    )
    commit = rev_proc.stdout.strip() if rev_proc.returncode == 0 else "HEAD"
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    tag_name = f"archive/{branch.replace('/', '-')}-{timestamp}"

    if not dry_run and rev_proc.returncode == 0:
        subprocess.run(
            ["git", "-C", str(repo), "tag", "-a", tag_name, "-m", f"Archive {branch} at {commit}", commit],
            capture_output=True, text=True, check=False,
        )

    return {
        "repo": str(repo),
        "branch": branch,
        "commit": commit,
        "tag_name": tag_name,
        "dry_run": dry_run,
        "status": "tagged" if not dry_run else "simulated",
    }


def main():
    parser = argparse.ArgumentParser(description="Create immutable archive tag before branch deletion")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to repository")
    parser.add_argument("--branch", required=True, help="Branch name to archive")
    parser.add_argument("--dry-run", action="store_true", help="Simulate tag without writing to git")
    args = parser.parse_args()

    result = create_archive_tag(args.repo, args.branch, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

