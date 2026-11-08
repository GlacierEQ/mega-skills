#!/usr/bin/env python3
"""Executable dispatcher for quality-gate backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "artifact-inspector": "artifact_inspector",
    "criteria-reader": "criteria_reader",
    "decision-recorder": "decision_recorder",
    "failure-classifier": "failure_classifier",
    "verifier-coordinator": "verifier_coordinator",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: quality-gate <artifact-inspector|criteria-reader|decision-recorder|failure-classifier|verifier-coordinator> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("quality-gate",op)
if __name__=="__main__":
    raise SystemExit(main())
