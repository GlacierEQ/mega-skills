#!/usr/bin/env python3
"""Executable dispatcher for evidence-register backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "id-assigner": "id_assigner",
    "claim-tracer": "claim_tracer",
    "register-updater": "register_updater",
    "integrity-checker": "integrity_checker",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: evidence-register <id-assigner|claim-tracer|register-updater|integrity-checker> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("evidence-register",op)
if __name__=="__main__":
    raise SystemExit(main())
