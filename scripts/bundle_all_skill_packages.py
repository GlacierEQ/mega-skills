#!/usr/bin/env python3
"""
Bundle all skills in GlacierEQ mega-skills into packaged zip archives in dist/packages/.
Each skill directory is packaged into a clean, standalone .zip archive with manifest.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist" / "packages"

def bundle_skills():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    skills = sorted([p for p in SKILLS_DIR.iterdir() if p.is_dir()])
    print(f"Packaging {len(skills)} skills into {DIST_DIR}...")
    
    manifest = []
    for skill_path in skills:
        skill_id = skill_path.name
        zip_file = DIST_DIR / f"{skill_id}.zip"
        
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(skill_path.rglob("*")):
                if file_path.is_file() and not any(part in file_path.parts for part in ["__pycache__", ".pytest_cache"]):
                    arcname = f"{skill_id}/{file_path.relative_to(skill_path)}"
                    zf.write(file_path, arcname)
        
        manifest.append({
            "skill_id": skill_id,
            "archive": zip_file.name,
            "size_bytes": zip_file.stat().st_size,
        })
    
    manifest_file = DIST_DIR / "packages_manifest.json"
    manifest_file.write_text(json.dumps({"total_packaged": len(manifest), "packages": manifest}, indent=2) + "\n")
    print(f"Successfully created {len(manifest)} packaged zip archives in {DIST_DIR}.")

if __name__ == "__main__":
    bundle_skills()
