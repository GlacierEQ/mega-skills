#!/usr/bin/env python3
"""
Inspect target repo: Skills, Combos, Mega, validator, tests
Part of mega-skill-forge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def inspect_repo(repo_root: Path) -> dict:
    """Inspect repository structure and count skills, combos, and megas."""
    root = repo_root.resolve()

    skills_dir = root / "skills"
    combos_dir = root / "combos"
    mega_dir = root / "mega"

    skills = [p.name for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()] if skills_dir.is_dir() else []

    combos = []
    combo_reg = root / "registry" / "combo-skills.json"
    if combo_reg.is_file():
        try:
            data = json.loads(combo_reg.read_text(encoding="utf-8"))
            combos = [e.get("id") for e in data.get("entries", []) if "id" in e]
        except Exception:
            pass
    elif combos_dir.is_dir():
        combos = [p.name for p in combos_dir.iterdir() if p.is_dir()]

    megas = []
    mega_reg = root / "registry" / "mega-skills.json"
    if mega_reg.is_file():
        try:
            data = json.loads(mega_reg.read_text(encoding="utf-8"))
            megas = [e.get("id") for e in data.get("entries", []) if "id" in e]
        except Exception:
            pass
    elif mega_dir.is_dir():
        megas = [p.name for p in mega_dir.iterdir() if p.is_dir()]

    validator_path = root / "scripts" / "validate_hierarchy.py"
    tests_dir = root / "tests"
    readiness_path = root / "registry" / "skill-readiness.json"

    return {
        "repo_root": str(root),
        "skills_count": len(skills),
        "combos_count": len(combos),
        "megas_count": len(megas),
        "has_validator": validator_path.is_file(),
        "has_test_suite": tests_dir.is_dir(),
        "has_readiness_registry": readiness_path.is_file(),
        "sample_skills": sorted(skills)[:5],
        "sample_combos": sorted(combos)[:5],
        "sample_megas": sorted(megas)[:5],
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect target repository for mega skill forge")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Path to repository root")
    args = parser.parse_args()

    report = inspect_repo(args.repo_root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
