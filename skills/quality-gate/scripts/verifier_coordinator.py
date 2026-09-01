#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from long_horizon_atomic_runtime import cli
if __name__ == "__main__":
    raise SystemExit(cli("quality-gate", "verifier_coordinator"))
