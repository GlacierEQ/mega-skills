#!/usr/bin/env python3
"""Executable dispatcher for context-capsule backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "assumption-tracker": "assumption_tracker",
    "capsule-generator": "capsule_generator",
    "drift-detector": "drift_detector",
    "state-compactor": "state_compactor",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: context-capsule <assumption-tracker|capsule-generator|drift-detector|state-compactor> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("context-capsule",op)
if __name__=="__main__":
    raise SystemExit(main())
