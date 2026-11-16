#!/usr/bin/env python3
"""Executable entry for hidden-harm-counter-wave composition."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from hidden_harm_counter_wave import compose_plan  # noqa: E402


def main() -> int:
    args = sys.argv[1:]
    work = " ".join(a for a in args if not a.startswith("--")).strip()
    if not work:
        work = "general GlacierEQ material work"
    tags = []
    if "--execute" in args:
        # Execute means emit the composition plan for this work unit.
        plan = compose_plan(work, tags)
        plan["skill"] = "hidden-harm-counter-wave"
        plan["capability_executed"] = True
        plan["status"] = "composed"
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    plan = compose_plan(work, tags)
    print(
        json.dumps(
            {
                "skill": "hidden-harm-counter-wave",
                "adapter": False,
                "capability_executed": False,
                "status": "ready",
                "hint": "Pass --execute with a work description to compose specialists.",
                "sample_compose": [c["id"] for c in plan["composed"]],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
