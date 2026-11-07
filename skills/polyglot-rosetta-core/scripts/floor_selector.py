#!/usr/bin/env python3
"""
Select optimal target floor (Rust/Cap'n Proto/eBPF/Lean4/Cairo)
Part of polyglot-rosetta-core skill.
"""

import argparse
import json
import sys
from pathlib import Path

import os
from pathlib import Path
import yaml

_CATALOG_PATH = Path(__file__).resolve().parents[1] / "resources" / "floor_catalog.yaml"

def _load_catalog():
    if _CATALOG_PATH.exists():
        data = yaml.safe_load(_CATALOG_PATH.read_text())
        out = {}
        for f in data.get("floors", []):
            out[f["language"]] = {
                "domains": f.get("domains", []),
                "memory_safety": f.get("memory_safety"),
                "speed_tier": f.get("speed_tier"),
                "binary": f.get("binary"),
                "id": f.get("id"),
                "proof_target": f.get("proof_target"),
            }
        # alias capnp -> capnproto style not needed; keep capnp entry for ipc/zero_copy
        out.setdefault("capnp", {"domains": ["ipc", "zero_copy", "serialization", "streaming"], "memory_safety": "arena_allocation", "speed_tier": "zero_copy", "binary": "capnp", "id": 0, "proof_target": "lean4"})
        return out
    return {}

FLOOR_CAPABILITIES = _load_catalog()


def select_target_floor(requirements: list[str]) -> dict:
    """Select the optimal polyglot floor given functional and architectural requirements."""
    req_set = {r.lower() for r in requirements}
    best_floor = "rust"
    best_score = -1
    best_id = 9999

    for floor, profile in FLOOR_CAPABILITIES.items():
        score = sum(1 for d in profile["domains"] if d in req_set)
        fid = profile.get("id", 9999) or 9999
        if score > best_score or (score == best_score and fid < best_id):
            best_score = score
            best_floor = floor
            best_id = fid

    return {
        "selected_floor": best_floor,
        "profile": FLOOR_CAPABILITIES[best_floor],
        "matched_requirements": [r for r in requirements if r.lower() in FLOOR_CAPABILITIES[best_floor]["domains"]],
        "all_requirements": requirements,
    }


def main():
    parser = argparse.ArgumentParser(description="Select optimal polyglot target floor")
    parser.add_argument("--requirements", nargs="+", default=["zero_copy", "ipc"], help="List of requirement tags")
    args = parser.parse_args()

    result = select_target_floor(args.requirements)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

