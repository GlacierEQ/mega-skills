#!/usr/bin/env python3
"""
Optional JSON evidence report outside tracked source tree
Part of mega-skills-test-runner skill.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path


def emit_report(report_path: Path, status: str, checks: list = None, metadata: dict = None) -> dict:
    """Emit a structured validation evidence report to the specified path."""
    target = report_path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target": str(target),
        "checks": checks or [],
        "metadata": metadata or {},
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description="Emit validation evidence report")
    parser.add_argument("--report", type=Path, required=True, help="Destination report JSON file")
    parser.add_argument("--status", default="PASS", choices=("PASS", "FAIL"), help="Overall test status")
    parser.add_argument("--input", type=Path, help="Optional raw checks JSON file to embed")
    args = parser.parse_args()

    checks = []
    if args.input and args.input.is_file():
        try:
            checks = json.loads(args.input.read_text(encoding="utf-8"))
        except Exception:
            pass

    payload = emit_report(args.report, args.status, checks=checks)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

