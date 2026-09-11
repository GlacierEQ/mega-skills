#!/usr/bin/env python3
"""
Select optimal target floor (Rust/Cap'n Proto/eBPF/Lean4/Cairo)
Part of polyglot-rosetta-core skill.
"""

import argparse
import json
import sys
from pathlib import Path

FLOOR_CAPABILITIES = {
    "rust": {"domains": ["systems", "concurrency", "performance", "cli"], "memory_safety": "borrow_checker", "speed_tier": "native"},
    "capnp": {"domains": ["ipc", "zero_copy", "serialization", "streaming"], "memory_safety": "arena_allocation", "speed_tier": "zero_copy"},
    "ebpf": {"domains": ["kernel", "telemetry", "tracing", "packet_filter"], "memory_safety": "kernel_verifier", "speed_tier": "in_kernel"},
    "lean4": {"domains": ["formal_verification", "proofs", "invariants", "correctness"], "memory_safety": "dependent_types", "speed_tier": "proven"},
    "cairo": {"domains": ["zk_stark", "verifiable_computation", "blockchain", "receipts"], "memory_safety": "algebraic_vm", "speed_tier": "verifiable"},
}


def select_target_floor(requirements: list[str]) -> dict:
    """Select the optimal polyglot floor given functional and architectural requirements."""
    req_set = {r.lower() for r in requirements}
    best_floor = "rust"
    best_score = -1

    for floor, profile in FLOOR_CAPABILITIES.items():
        score = sum(1 for d in profile["domains"] if d in req_set)
        if score > best_score:
            best_score = score
            best_floor = floor

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

