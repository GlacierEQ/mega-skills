#!/usr/bin/env python3
"""
Deep-extract patterns from one existing skill.
Part of local-skill.
"""

import sys
import json
from pathlib import Path

def read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None

def extract_skill(skill_dir: Path):
    """Return a rich extraction of one skill for use as an exemplar."""
    data = {
        "name": skill_dir.name,
        "path": str(skill_dir),
        "files": {},
        "structure": {},
    }
    for name in ("SKILL.md", "skill.py", "__init__.py", "requirements.txt"):
        p = skill_dir / name
        if p.exists():
            data["files"][name] = read_text(p)

    for sub in ("scripts", "resources", "tests", "templates", "references"):
        d = skill_dir / sub
        if d.is_dir():
            data["structure"][sub] = {}
            for f in sorted(d.iterdir()):
                if f.is_file():
                    data["structure"][sub][f.name] = {
                        "size": f.stat().st_size,
                        "executable": bool(f.stat().st_mode & 0o111),
                        "preview": (read_text(f) or "")[:400],
                    }
    return data

def main():
    if len(sys.argv) < 2:
        print("Usage: extract <skill-name>")
        return 1

    name = sys.argv[1].strip().lower().replace("_", "-")
    here = Path(__file__).resolve()
    repo_root = here.parents[3]
    skill_dir = repo_root / "skills" / name

    if not skill_dir.is_dir():
        # allow absolute or relative path
        skill_dir = Path(sys.argv[1])
        if not skill_dir.is_dir():
            print(f"Skill not found: {name}")
            return 1

    data = extract_skill(skill_dir)
    out_path = Path(__file__).parent.parent / "resources" / f"extract_{skill_dir.name}.json"
    out_path.write_text(json.dumps(data, indent=2))
    print(f"Extracted {skill_dir.name} -> {out_path}")
    print(f"  files: {list(data['files'].keys())}")
    for sub, files in data["structure"].items():
        print(f"  {sub}/: {list(files.keys())}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
