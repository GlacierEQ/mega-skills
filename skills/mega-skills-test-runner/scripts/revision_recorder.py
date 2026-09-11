#!/usr/bin/env python3
"""
Record tested revision state for evidence
Part of mega-skills-test-runner skill.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def record_revision(repo_path: Path) -> dict:
    """Capture HEAD commit and git status for evidence tracking."""
    repo = repo_path.resolve()
    rev = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--branch"],
        capture_output=True, text=True, check=False,
    )
    head = rev.stdout.strip() if rev.returncode == 0 else "unknown"
    branch_summary = status.stdout.splitlines()[0] if status.stdout else ""
    return {
        "repo": str(repo),
        "head": head,
        "branch_summary": branch_summary,
        "clean": len(status.stdout.strip().splitlines()) <= 1 if status.returncode == 0 else False,
    }


def main():
    parser = argparse.ArgumentParser(description="Record tested revision state")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to git repository")
    parser.add_argument("--output", type=Path, help="Optional output JSON file")
    args = parser.parse_args()

    record = record_revision(args.repo)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

