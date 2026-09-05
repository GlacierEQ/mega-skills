#!/usr/bin/env python3
"""Build and integrate all workspace skills into mega-skills repository.

Reads canonical skills from /root/.agents/skills, copies them into skills/<id>,
generates typed registry entries in registry/skills.json, adds foundational
combo-skills and mega-skills, and executes validation.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS_DIR = Path("/root/.agents/skills")
SKILLS_DIR = ROOT / "skills"
REGISTRY_DIR = ROOT / "registry"
SKILLS_JSON = REGISTRY_DIR / "skills.json"
COMBOS_JSON = REGISTRY_DIR / "combo-skills.json"
MEGAS_JSON = REGISTRY_DIR / "mega-skills.json"

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def sanitize_id(raw: str) -> str:
    s = raw.lower().replace("_", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def load_canonical_skills() -> list[dict]:
    results = []
    for skill_path in sorted(CANONICAL_SKILLS_DIR.iterdir()):
        skill_md = skill_path / "SKILL.md"
        if not skill_md.is_file():
            continue
        content = skill_md.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except Exception:
            fm = {}
        skill_id = sanitize_id(fm.get("name") or skill_path.name)
        desc = fm.get("description", "").strip() or f"Operating inside {skill_id}"
        body = parts[2].strip()
        results.append({
            "source_dir": skill_path,
            "id": skill_id,
            "display_name": skill_id.replace("-", " ").title(),
            "description": desc,
            "body": body,
            "raw_content": content,
        })
    return results


def sync_skills() -> None:
    skills_registry = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    existing_entries = {e["id"]: e for e in skills_registry.get("entries", [])}

    canonical_skills = load_canonical_skills()
    print(f"Loaded {len(canonical_skills)} canonical skills from {CANONICAL_SKILLS_DIR}")

    for cs in canonical_skills:
        skill_id = cs["id"]
        target_dir = SKILLS_DIR / skill_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_md = target_dir / "SKILL.md"

        # Copy any subdirectories (references, scripts, resources)
        for child in cs["source_dir"].iterdir():
            if child.is_dir() and child.name not in (".git", "__pycache__", ".pytest_cache"):
                dest_child = target_dir / child.name
                if dest_child.exists():
                    shutil.rmtree(dest_child)
                shutil.copytree(child, dest_child)
            elif child.is_file() and child.name != "SKILL.md":
                shutil.copy2(child, target_dir / child.name)

        # Write clean SKILL.md with valid frontmatter matching skill_id
        fm_dict = {
            "name": skill_id,
            "description": cs["description"],
            "version": "0.1.0",
        }
        fm_str = yaml.dump(fm_dict, sort_keys=False, default_flow_style=False).strip()
        final_content = f"---\n{fm_str}\n---\n\n{cs['body']}\n"
        target_md.write_text(final_content, encoding="utf-8")

        # Create or update entry in skills.json
        if skill_id not in existing_entries:
            entry = {
                "id": skill_id,
                "display_name": cs["display_name"],
                "ownership": "candidate",
                "maturity": "candidate",
                "version": "0.1.0",
                "path": f"skills/{skill_id}",
                "entrypoint": f"skills/{skill_id}/SKILL.md",
                "purpose": cs["description"][:120] if cs["description"] else f"Execute {skill_id} workflows.",
                "input_contract": ["Task specification", "Context artifacts"],
                "output_contract": ["Skill-defined output per SKILL.md"],
                "local_validation": ["Readiness not yet established; run scripts/readiness_assay.py before activation."],
                "does_not_own": ["Cross-system mission orchestration", "Unverified external mutations"],
            }
            existing_entries[skill_id] = entry

    # Sort entries by ID
    skills_registry["entries"] = [existing_entries[k] for k in sorted(existing_entries.keys())]
    SKILLS_JSON.write_text(json.dumps(skills_registry, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {SKILLS_JSON} with {len(skills_registry['entries'])} skills")


def main() -> None:
    sync_skills()


if __name__ == "__main__":
    main()
