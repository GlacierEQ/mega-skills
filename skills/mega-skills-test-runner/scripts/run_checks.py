#!/usr/bin/env python3
"""Run the trusted local validation gate for a GlacierEQ Mega Skills repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def command_result(name: str, command: list[str], repo: Path) -> dict[str, Any]:
    result = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)
    return {
        "name": name,
        "command": command,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Path to the trusted Mega Skills repository root.")
    parser.add_argument("--report", type=Path, help="Optional path for a JSON validation report.")
    parser.add_argument("--skip-diff-check", action="store_true", help="Skip git diff whitespace validation.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed executable check.")
    return parser.parse_args()


def require_repository(root: Path) -> None:
    required = (root / "scripts" / "validate_hierarchy.py", root / "tests", root / "registry")
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        raise ValueError(f"not a Mega Skills repository root; missing: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    try:
        require_repository(repo)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    checks: list[dict[str, Any]] = []
    sequence = [
        ("hierarchy-validator", [sys.executable, "scripts/validate_hierarchy.py"]),
        ("regression-suite", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ]
    if not args.skip_diff_check:
        sequence.append(("diff-hygiene", ["git", "diff", "--check"]))

    for name, command in sequence:
        check = command_result(name, command, repo)
        checks.append(check)
        print(f"{'PASS' if check['passed'] else 'FAIL'} {name}")
        if check["stdout"]:
            print(check["stdout"], end="")
        if check["stderr"]:
            print(check["stderr"], end="", file=sys.stderr)
        if args.fail_fast and not check["passed"]:
            break

    status = command_result("repository-state", ["git", "status", "--short", "--branch"], repo)
    checks.append(status)
    passed = all(check["passed"] for check in checks if check["name"] != "repository-state")
    report = {
        "schema_version": 1,
        "repository": str(repo),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "checks": checks,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report: {args.report}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
