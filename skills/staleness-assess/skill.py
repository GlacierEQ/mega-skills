#!/usr/bin/env python3
"""Executable dispatcher for staleness-assess backed by the shared long-horizon runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from long_horizon_atomic_runtime import cli
OPERATIONS = {
    "purpose": "purpose",
    "procedure": "procedure",
    "output_contract": "output_contract",
}
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: staleness-assess <purpose|procedure|output_contract>")
        return 1
    if sys.argv[1] not in OPERATIONS:
        print("Unknown command: " + sys.argv[1])
        return 1
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    return cli("staleness-assess", sys.argv[1] if len(sys.argv) > 1 else None)
if __name__ == "__main__":
    raise SystemExit(main())
