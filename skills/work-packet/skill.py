#!/usr/bin/env python3
"""Executable dispatcher for work-packet backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "emit": "emit",
    "acceptance-tester": "acceptance_tester",
    "boundary-enforcer": "boundary_enforcer",
    "input-lister": "input_lister",
    "objective-namer": "objective_namer",
    "output-specifier": "output_specifier",
    "state-updater": "state_updater",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: work-packet <acceptance-tester|boundary-enforcer|input-lister|objective-namer|output-specifier|state-updater> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("work-packet",op)
if __name__=="__main__":
    raise SystemExit(main())
