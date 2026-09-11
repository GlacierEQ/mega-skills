#!/usr/bin/env python3
"""
Select minimal resolved Combo IDs from registry
Part of mega-skill-forge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def select_combos(combo_registry_path: Path, keywords: list[str]) -> list[str]:
    """Select minimal matching combo IDs from combo-skills registry."""
    path = combo_registry_path.resolve()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    matched = []
    kw_set = {k.lower() for k in keywords}
    for entry in entries:
        cid = entry.get("id", "")
        desc = entry.get("description", "").lower()
        if any(kw in cid.lower() or kw in desc for kw in kw_set):
            matched.append(cid)
    return matched


def main():
    parser = argparse.ArgumentParser(description="Select minimal resolved Combo IDs from registry")
    parser.add_argument("--registry", type=Path, default=Path("registry/combo-skills.json"), help="Combo registry path")
    parser.add_argument("--keywords", nargs="+", default=["code-repair", "testing"], help="Keywords to filter combos")
    args = parser.parse_args()

    results = select_combos(args.registry, args.keywords)
    print(json.dumps({"keywords": args.keywords, "matched_combos": results}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

