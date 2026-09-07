#!/usr/bin/env python3
"""Composed entrypoint for mega-agent-memory-systems."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MEGA_DIR = Path(__file__).resolve().parent
SKILLS_DIR = MEGA_DIR.parent
ATOMIC_SKILL = SKILLS_DIR / "agent-memory-systems" / "skill.py"
SCRIPTS_DIR = MEGA_DIR / "scripts"

ATOMIC_COMMANDS = {
    "init",
    "validate",
    "hydrate",
    "add-source",
    "set-next",
    "transition",
    "complete",
}

LOCAL_COMMANDS = {
    "capabilities",
    "memory_type_architecture",
    "patterns",
}


def _run_python(path: Path, args: list[str]) -> int:
    if not path.exists():
        print(f"Required implementation not found: {path}", file=sys.stderr)
        return 2
    result = subprocess.run([sys.executable, str(path), *args], check=False)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: mega-agent-memory-systems <command> [args...]")
        print("Commands:")
        print("  verify")
        for command in sorted(ATOMIC_COMMANDS):
            print(f"  {command}")
        for command in sorted(LOCAL_COMMANDS):
            print(f"  {command}")
        return 1

    command, *rest = args

    if command == "verify":
        return _run_python(SCRIPTS_DIR / "run.py", rest)

    if command in ATOMIC_COMMANDS:
        return _run_python(ATOMIC_SKILL, [command, *rest])

    normalized = command.replace("-", "_")
    if normalized in LOCAL_COMMANDS:
        return _run_python(SCRIPTS_DIR / f"{normalized}.py", rest)

    print(f"Unknown command: {command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
