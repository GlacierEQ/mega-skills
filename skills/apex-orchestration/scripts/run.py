#!/usr/bin/env python3
"""Entry point for apex-orchestration mission lifecycle engine.

Delegates to orchestrator.main() — runs the full INTAKE→DECOMPOSE→DISPATCH→
VERIFY→FUSE→DELIVER pipeline or a single-subtask lane routing query.
"""

import sys
from pathlib import Path

# Ensure sibling modules are importable
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrator import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
