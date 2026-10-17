#!/usr/bin/env python3
"""Compatibility runner for linear-ops package discovery."""
import json
import sys


def main() -> int:
    wants_execute = "--execute" in sys.argv[1:]
    payload = {
        "skill": "linear-ops",
        "adapter": True,
        "capability_executed": False,
        "status": "execution_unavailable" if wants_execute else "adapter_ready",
        "reason": (
            "Use host Linear tools for mutations, or skill.py analyze <export.json> offline."
            if wants_execute
            else "Compatibility adapter is installed and discoverable."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if wants_execute else 0


if __name__ == "__main__":
    raise SystemExit(main())
