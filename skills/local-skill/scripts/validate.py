#!/usr/bin/env python3
"""
Validate a skill directory against mega-skills conventions.
Part of local-skill.
"""

import sys
from pathlib import Path

def validate(skill_dir: Path):
    errors = []
    warnings = []

    if not skill_dir.is_dir():
        return [f"Not a directory: {skill_dir}"], []

    # Required files
    for req in ("SKILL.md", "skill.py"):
        if not (skill_dir / req).exists():
            errors.append(f"Missing required file: {req}")

    skill_py = skill_dir / "skill.py"
    if skill_py.exists() and not (skill_py.stat().st_mode & 0o111):
        warnings.append("skill.py is not executable")

    # Front-matter sanity
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.lstrip().startswith("---"):
            errors.append("SKILL.md missing YAML front-matter")
        if "name:" not in text.split("---")[1] if text.count("---") >= 2 else "":
            errors.append("SKILL.md front-matter missing name:")

    # Scripts
    scripts = skill_dir / "scripts"
    if scripts.is_dir():
        for p in scripts.iterdir():
            if p.suffix == ".py" and not (p.stat().st_mode & 0o111):
                warnings.append(f"Script not executable: {p.name}")
    else:
        warnings.append("No scripts/ directory")

    # Tests
    tests = skill_dir / "tests"
    if not tests.is_dir() or not any(tests.glob("test_*.py")):
        warnings.append("No tests/test_*.py found")

    # Requirements
    if not (skill_dir / "requirements.txt").exists():
        warnings.append("No requirements.txt")

    return errors, warnings

def main():
    if len(sys.argv) < 2:
        # default: validate self
        skill_dir = Path(__file__).resolve().parents[1]
    else:
        skill_dir = Path(sys.argv[1])

    errors, warnings = validate(skill_dir)
    print(f"Validating: {skill_dir}")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  WARN:  {w}")
    if not errors and not warnings:
        print("  OK (no issues)")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
