#!/usr/bin/env python3
"""Executable quality-pitstop calibrator (hidden-harm-governance)."""
from __future__ import annotations

import argparse
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def _load_kernel():
    spec = spec_from_file_location(
        "operator_mission_kernel",
        SCRIPTS / "operator_mission_kernel.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("unable to load scripts/operator_mission_kernel.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_payload(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    return json.loads(raw) if raw else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation",
        nargs="?",
        default="gate_polarity",
        choices=("gate_polarity", "counter_gate", "invert_gate", "calibrate"),
    )
    parser.add_argument("--input", help="JSON payload file; stdin when omitted")
    args = parser.parse_args()
    kernel = _load_kernel()
    operation = "gate_polarity" if args.operation == "calibrate" else args.operation
    payload = _load_payload(args.input)
    print(json.dumps(kernel.run_operator_mission_kernel(operation, payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
