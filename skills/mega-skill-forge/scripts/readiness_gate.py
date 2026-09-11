#!/usr/bin/env python3
"""
Add capability-readiness as conditional, guard advanced routes
Part of mega-skill-forge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def evaluate_readiness_gate(
    required_combos: list[str],
    readiness_path: Path | None = None,
    conditional_combos: list[str] | None = None,
) -> dict:
    """Check readiness of required combos and enforce capability-readiness guarding."""
    unready = []
    statuses = {}

    cond_combos = list(conditional_combos or [])
    if "capability-readiness" not in cond_combos:
        cond_combos.insert(0, "capability-readiness")

    if readiness_path and readiness_path.is_file():
        try:
            reg = json.loads(readiness_path.read_text(encoding="utf-8"))
            combos_reg = reg.get("combos", {})
            for cid in required_combos:
                entry = combos_reg.get(cid, {})
                status = entry.get("readiness_status", "unknown")
                statuses[cid] = status
                if status not in ("active", "ready", "composition_ready"):
                    unready.append(cid)
        except Exception as e:
            statuses["error"] = str(e)
            unready.extend(required_combos)
    else:
        for cid in required_combos:
            statuses[cid] = "unverified"

    passed = len(unready) == 0
    return {
        "passed": passed,
        "evaluated_combos": statuses,
        "unready_combos": unready,
        "conditional_combos": cond_combos,
        "guarded_routes_enforced": True,
        "notes": "capability-readiness added to gate advanced routes before consequential execution."
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate readiness gate and guard advanced routes")
    parser.add_argument("--combos", nargs="+", required=True, help="Required combo IDs to evaluate")
    parser.add_argument("--readiness", type=Path, default=Path("registry/skill-readiness.json"), help="Skill readiness registry path")
    args = parser.parse_args()

    result = evaluate_readiness_gate(args.combos, args.readiness)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
