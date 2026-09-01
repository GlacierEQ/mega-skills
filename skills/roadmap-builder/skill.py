#!/usr/bin/env python3
"""Executable dispatcher for roadmap-builder backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "artifact-lister": "artifact_lister",
    "dependency-optimizer": "dependency_optimizer",
    "phase-grouper": "phase_grouper",
    "chunk-definer": "chunk_definer",
    "parallelism-validator": "parallelism_validator",
    "roadmap-emitter": "roadmap_emitter",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: roadmap-builder <artifact-lister|dependency-optimizer|phase-grouper|chunk-definer|parallelism-validator|roadmap-emitter> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("roadmap-builder",op)
if __name__=="__main__":
    raise SystemExit(main())
