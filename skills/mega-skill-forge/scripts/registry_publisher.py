#!/usr/bin/env python3
"""
Copy templates/mega-registry-entry.json, set unique ID/version
Part of mega-skill-forge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def build_registry_entry(
    mega_id: str,
    display_name: str,
    required_combos: list[str],
    conditional_combos: list[str] | None = None,
    mission_output: str | None = None,
    version: str = "0.1.0",
    adds: str | None = None,
) -> dict:
    """Build canonical mega registry entry conforming to mega-registry-entry schema."""
    if not mega_id:
        raise ValueError("mega_id cannot be empty")
    if len(required_combos) < 2:
        raise ValueError("Mega skill requires at least 2 required combos")

    conds = list(conditional_combos or [])
    if "capability-readiness" not in conds:
        conds.insert(0, "capability-readiness")

    entry = {
        "id": mega_id,
        "display_name": display_name,
        "ownership": "glaciereq",
        "maturity": "candidate",
        "version": version,
        "path": f"mega-skills/{mega_id}",
        "entrypoint": f"mega-skills/{mega_id}/MEGA.md",
        "required_combos": required_combos,
        "conditional_combos": conds,
        "mission_output": mission_output or f"{mega_id.upper().replace('-', '_')}_OUTPUT.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md",
        ],
        "adds": adds or f"Mission-wide coordination across {', '.join(required_combos)}.",
    }
    return entry


def publish_to_registry(entry: dict, registry_path: Path) -> dict:
    """Add or update an entry in the mega-skills registry file."""
    if not registry_path.is_file():
        data = {"version": "1.0.0", "entries": []}
    else:
        data = json.loads(registry_path.read_text(encoding="utf-8"))

    entries = data.get("entries", [])
    updated = False
    for i, e in enumerate(entries):
        if e.get("id") == entry["id"]:
            entries[i] = entry
            updated = True
            break
    if not updated:
        entries.append(entry)

    data["entries"] = entries
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main():
    parser = argparse.ArgumentParser(description="Create and publish mega skill registry entry")
    parser.add_argument("--id", required=True, help="Mega skill ID")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--combos", nargs="+", required=True, help="Required combos (>= 2)")
    parser.add_argument("--registry", type=Path, default=Path("registry/mega-skills.json"), help="Mega skills registry path")
    parser.add_argument("--dry-run", action="store_true", help="Print entry without writing to registry")
    args = parser.parse_args()

    entry = build_registry_entry(args.id, args.name, args.combos)
    if args.dry_run:
        print(json.dumps(entry, indent=2))
        return 0

    publish_to_registry(entry, args.registry)
    print(f"Published '{args.id}' to {args.registry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
