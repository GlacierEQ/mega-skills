#!/usr/bin/env python3
"""
local-skill.
Entry point for local-skill meta-skill.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def main():
    """Main entry point - dispatches to appropriate script based on args."""
    if len(sys.argv) < 2:
        print("Usage: local-skill <command> [args...]")
        print("Available commands:")
        for sn in [
            "inspect_skill.py",
            "extract.py",
            "generate.py",
            "validate.py",
            "pattern_catalog.py",
            "this_skill.py",
        ]:
            print(f"  {sn.replace('.py', '')}")
        return 1

    command = sys.argv[1]
    script_name = "inspect_skill" if command == "inspect" else command
    script_path = Path(__file__).parent / "scripts" / f"{script_name}.py"

    if not script_path.exists():
        script_path = Path(__file__).parent / "scripts" / f"{script_name.replace('-', '_')}.py"

    if not script_path.exists():
        print(f"Unknown command: {command}")
        return 1

    exec_globals = {
        "__name__": "__main__",
        "__file__": str(script_path),
        "__package__": None,
    }
    original_argv = sys.argv
    try:
        sys.argv = [str(script_path), *original_argv[2:]]
        exec(script_path.read_text(), exec_globals)
    except SystemExit as exc:
        return int(exc.code or 0)
    finally:
        sys.argv = original_argv
    return 0

if __name__ == "__main__":
    sys.exit(main())
