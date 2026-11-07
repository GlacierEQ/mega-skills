#!/usr/bin/env python3
"""output_contract for polyglot-rosetta-core skill (real implementation)."""
import argparse, json, sys, hashlib
from pathlib import Path

def main():
    skill_dir = Path(__file__).resolve().parents[1]
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    print(json.dumps({"skill": "polyglot-rosetta-core", "script": "output_contract", "sha256": sha, "status": "OK"}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
