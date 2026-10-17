#!/usr/bin/env python3
"""linear-ops entry — discovery adapter + offline board analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "analyze" and len(args) >= 2:
        from scripts.analyze_board import analyze_file

        result = analyze_file(Path(args[1]))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    wants_execute = "--execute" in args
    payload = {
        "skill": "linear-ops",
        "adapter": True,
        "capability_executed": False,
        "status": "execution_unavailable" if wants_execute else "adapter_ready",
        "reason": (
            "Live Linear mutations use the host Linear connector/MCP. "
            "Offline: python skill.py analyze <issues.json>. See SKILL.md."
            if wants_execute
            else "linear-ops is discoverable. Load SKILL.md for agent contract."
        ),
        "paths": {
            "skill_md": str(ROOT / "SKILL.md"),
            "cleanup_playbook": str(ROOT / "references" / "cleanup-playbook.md"),
            "issue_schema": str(ROOT / "references" / "issue-schema.md"),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if wants_execute else 0


if __name__ == "__main__":
    raise SystemExit(main())
