#!/usr/bin/env python3
"""Executable Casey operator mission-selection kernel."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from always_on_atomic_runtime import load_payload  # noqa: E402
from operator_mission_kernel import run_operator_mission_kernel  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation", nargs="?", default="mission_select",
        choices=("mission_select", "dispatch_gate", "completion_gate", "purpose", "procedure", "output_contract"),
    )
    parser.add_argument("--input", help="JSON payload file; stdin is used when omitted")
    args = parser.parse_args()
    payload = load_payload(args.input)
    print(json.dumps(run_operator_mission_kernel(args.operation, payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
