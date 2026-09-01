#!/usr/bin/env python3
"""Executable claim-calibration dispatcher for the Always-On worker runtime."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from always_on_atomic_runtime import cli
OPERATIONS={
    "boundary-recorder": "boundary_recorder",
    "claim-extractor": "claim_extractor",
    "evidence-mapper": "evidence_mapper",
    "scope-enforcer": "scope_enforcer",
}
def main()->int:
    if len(sys.argv)<2:
        print("Available commands: "+", ".join(sorted(OPERATIONS)))
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1]); return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("claim-calibration",op)
if __name__=="__main__": raise SystemExit(main())
