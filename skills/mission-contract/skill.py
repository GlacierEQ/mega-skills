#!/usr/bin/env python3
"""Executable dispatcher for mission-contract backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "outcome-framer": "outcome_framer",
    "scope-separator": "scope_separator",
    "constraint-mapper": "constraint_mapper",
    "criteria-definer": "criteria_definer",
    "assumption-bounder": "assumption_bounder",
    "contract-emitter": "contract_emitter",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: mission-contract <outcome-framer|scope-separator|constraint-mapper|criteria-definer|assumption-bounder|contract-emitter> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("mission-contract",op)
if __name__=="__main__":
    raise SystemExit(main())
