#!/usr/bin/env python3
"""
Inspect the mega-skills repository and summarize structural patterns.
Part of local-skill.
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

def walk_skills(root: Path):
    """Yield skill directories under skills/."""
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            yield child

def summarize_skill(skill_dir: Path):
    """Return a compact structural summary of one skill."""
    summary = {
        "name": skill_dir.name,
        "has_skill_py": (skill_dir / "skill.py").exists(),
        "has_init": (skill_dir / "__init__.py").exists(),
        "has_requirements": (skill_dir / "requirements.txt").exists(),
        "scripts": [],
        "resources": [],
        "tests": [],
        "templates": [],
        "references": [],
    }
    for sub in ("scripts", "resources", "tests", "templates", "references"):
        d = skill_dir / sub
        if d.is_dir():
            summary[sub] = sorted(p.name for p in d.iterdir() if p.is_file())
    return summary

def main():
    # Default to the repository root that contains this skill
    here = Path(__file__).resolve()
    repo_root = here.parents[3]  # skills/local-skill/scripts -> repo root
    if not (repo_root / "skills").is_dir():
        # Fallback for when the skill is run from a checkout copy
        repo_root = Path.cwd()

    skills = list(walk_skills(repo_root))
    print(f"Found {len(skills)} skills under {repo_root / 'skills'}")

    script_counts = Counter()
    resource_exts = Counter()
    has_skill_py = 0
    has_tests = 0

    samples = []
    for s in skills:
        summary = summarize_skill(s)
        samples.append(summary)
        if summary["has_skill_py"]:
            has_skill_py += 1
        if summary["tests"]:
            has_tests += 1
        for scr in summary["scripts"]:
            script_counts[scr] += 1
        for res in summary["resources"]:
            resource_exts[Path(res).suffix or "(none)"] += 1

    print(f"Skills with skill.py: {has_skill_py}/{len(skills)}")
    print(f"Skills with tests/:   {has_tests}/{len(skills)}")
    print("Top script names:")
    for name, cnt in script_counts.most_common(12):
        print(f"  {name}: {cnt}")
    print("Resource extensions:")
    for ext, cnt in resource_exts.most_common():
        print(f"  {ext}: {cnt}")

    # Emit machine-readable summary for downstream generate/extract
    out = {
        "repo_root": str(repo_root),
        "skill_count": len(skills),
        "has_skill_py_ratio": has_skill_py / max(len(skills), 1),
        "has_tests_ratio": has_tests / max(len(skills), 1),
        "top_scripts": script_counts.most_common(20),
        "resource_extensions": dict(resource_exts),
        "sample_skills": samples[:8],
    }
    out_path = Path(__file__).parent.parent / "resources" / "last_inspect.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
