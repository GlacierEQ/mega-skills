#!/usr/bin/env python3
"""
Execute test suites before merge permission
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_regression_gate(repo_path: Path, test_cmd: list[str] = None) -> dict:
    """Execute regression test gate before allowing branch merges."""
    repo = repo_path.resolve()
    cmd = test_cmd or [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, check=False)
    passed = proc.returncode == 0

    return {
        "repo": str(repo),
        "command": cmd,
        "passed": passed,
        "merge_allowed": passed,
        "returncode": proc.returncode,
        "summary": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "OK",
    }


def main():
    parser = argparse.ArgumentParser(description="Regression test gatekeeper")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to repository")
    args = parser.parse_args()

    result = run_regression_gate(args.repo)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

