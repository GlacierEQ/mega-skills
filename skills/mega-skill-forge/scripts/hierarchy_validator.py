#!/usr/bin/env python3
"""
Run repository validator + focused regression test
Part of mega-skill-forge skill.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def validate_mega_candidate(
    mega_id: str,
    required_combos: list[str],
    combo_registry_path: Path,
) -> tuple[bool, list[str]]:
    """Validate hierarchy integrity of a candidate Mega Skill."""
    issues = []
    if not mega_id:
        issues.append("Mega ID must not be empty.")

    if len(required_combos) < 2:
        issues.append(f"Mega skill requires >= 2 required combos, got {len(required_combos)}")

    if not combo_registry_path.is_file():
        issues.append(f"Combo registry not found at {combo_registry_path}")
        return False, issues

    try:
        combo_data = json.loads(combo_registry_path.read_text(encoding="utf-8"))
        registered_combos = {c.get("id") for c in combo_data.get("entries", [])}
        for cid in required_combos:
            if cid not in registered_combos:
                issues.append(f"Required combo '{cid}' is not registered in {combo_registry_path.name}")
    except Exception as e:
        issues.append(f"Failed to read combo registry: {e}")

    return len(issues) == 0, issues


def run_repo_hierarchy_validator(repo_root: Path) -> tuple[bool, str]:
    """Execute repository-wide validate_hierarchy.py script."""
    validator = repo_root / "scripts" / "validate_hierarchy.py"
    if not validator.is_file():
        return False, f"Validator script not found at {validator}"

    res = subprocess.run(
        [sys.executable, str(validator)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    return res.returncode == 0, res.stdout + res.stderr


def main():
    parser = argparse.ArgumentParser(description="Validate mega skill candidate hierarchy and repository integrity")
    parser.add_argument("--id", help="Candidate mega ID")
    parser.add_argument("--combos", nargs="*", help="Required combos for candidate")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    combo_reg = repo_root / "registry" / "combo-skills.json"

    if args.id and args.combos:
        valid, issues = validate_mega_candidate(args.id, args.combos, combo_reg)
        if not valid:
            print(f"Candidate validation FAILED:\n" + "\n".join(f" - {i}" for i in issues))
            return 1
        print(f"Candidate '{args.id}' hierarchy validation passed.")

    repo_valid, output = run_repo_hierarchy_validator(repo_root)
    print(output)
    return 0 if repo_valid else 1


if __name__ == "__main__":
    sys.exit(main())
