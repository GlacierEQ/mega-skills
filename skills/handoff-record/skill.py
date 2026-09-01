#!/usr/bin/env python3
"""Executable dispatcher for handoff-record backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "assumption-separator": "assumption_separator",
    "dead-end-recorder": "dead_end_recorder",
    "environment-capturer": "environment_capturer",
    "next-action-encoder": "next_action_encoder",
    "resume-point-encoder": "resume_point_encoder",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: handoff-record <assumption-separator|dead-end-recorder|environment-capturer|next-action-encoder|resume-point-encoder> --input payload.json")
        return 1
    op=OPERATIONS.get(sys.argv[1])
    if not op:
        print("Unknown command: "+sys.argv[1])
        return 1
    sys.argv=[sys.argv[0],*sys.argv[2:]]
    return cli("handoff-record",op)
if __name__=="__main__":
    raise SystemExit(main())
