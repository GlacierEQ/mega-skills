#!/usr/bin/env python3
"""
Draft mission contract with boundary, non-goals, artifact, state
Part of mega-skill-forge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def draft_mission_contract(
    mega_id: str,
    outcome: str,
    required_combos: list[str],
    non_goals: list[str] | None = None,
    artifacts: list[str] | None = None,
    conditional_combos: list[str] | None = None,
) -> dict:
    """Draft a structured mission contract conforming to APEX Mega Skill standards."""
    if not mega_id:
        raise ValueError("mega_id cannot be empty")
    if not outcome:
        raise ValueError("outcome cannot be empty")
    if len(required_combos) < 2:
        raise ValueError("A Mega Skill requires at least two required Combo Skills")

    combos_str = ", ".join(required_combos)
    contract = {
        "mega_id": mega_id,
        "outcome": outcome,
        "operational_boundary": f"Orchestrates bounded end-to-end execution across [{combos_str}].",
        "non_goals": non_goals or [
            "Do not bypass individual combo validation assertions",
            "Do not run external unverified mutations without guarded approval",
        ],
        "required_combos": required_combos,
        "conditional_combos": conditional_combos or ["capability-readiness"],
        "compound_artifacts": artifacts or [
            "mission-execution-plan.json",
            "cross-combo-evidence-pack.json",
            "final-acceptance-report.md",
        ],
        "durable_state_artifacts": [
            "mission-state.json",
            "checkpoint-ledger.jsonl",
            "recovery-plan.json",
            "readiness-receipt.json",
            "final-verdict.json",
        ],
        "recovery_rule": "On failure in any member combo, freeze execution, checkpoint intermediate state, and generate diagnostic artifact.",
        "approval_boundary": "Consequential external effects and irreversible operations require explicit user confirmation.",
        "integration_delta": f"Coordinates end-to-end state transitions, shared recovery, and synthesis across {len(required_combos)} combos which cannot be performed by any single combo.",
    }
    return contract


def main():
    parser = argparse.ArgumentParser(description="Draft a mission contract for a Mega Skill")
    parser.add_argument("--id", required=True, help="Mega skill ID")
    parser.add_argument("--outcome", required=True, help="Intended mission outcome")
    parser.add_argument("--combos", nargs="+", required=True, help="Required combo skill IDs (at least 2)")
    parser.add_argument("--output", type=Path, help="Optional output JSON path")
    args = parser.parse_args()

    contract = draft_mission_contract(args.id, args.outcome, args.combos)
    if args.output:
        args.output.write_text(json.dumps(contract, indent=2), encoding="utf-8")
        print(f"Wrote mission contract to {args.output}")
    else:
        print(json.dumps(contract, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
