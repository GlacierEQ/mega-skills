#!/usr/bin/env python3
"""
apex-ast-sentinel.
Entry point for apex-ast-sentinel skill.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def main():
    if len(sys.argv) < 2:
        print(f"Usage: apex-ast-sentinel <command> [args...]")
        print("Available commands:")
        for sn in ['this_skill.py', 'run.py']:
            print(f"  {sn.replace('.py', '')}")
        return 1

    command = sys.argv[1]
    script_path = Path(__file__).parent / "scripts" / f"{command}.py"
    if not script_path.exists():
        script_path = Path(__file__).parent / "scripts" / f"{command.replace('-', '_')}.py"
    if not script_path.exists():
        print(f"Unknown command: {command}")
        return 1

    exec_globals = {"__name__": "__main__"}
    exec(script_path.read_text(), exec_globals)
    return 0

if __name__ == "__main__":
    sys.exit(main())
