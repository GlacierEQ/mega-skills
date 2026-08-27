#!/usr/bin/env python3
"""Validate the GlacierEQ Skills → Combo Skills → Mega Skills hierarchy."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OWNERSHIP = {"glaciereq", "external-platform", "candidate"}


def load(name: str) -> dict:
    path = REGISTRY / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read registry/{name}: {exc}") from exc


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_common(entry: dict, expected_layer: str) -> None:
    for field in ("id", "display_name", "ownership", "maturity", "version", "path", "entrypoint"):
        expect(bool(entry.get(field)), f"{expected_layer}: missing {field}")
    expect(bool(ID_PATTERN.fullmatch(entry["id"])), f"{expected_layer}: invalid ID {entry['id']}")
    expect(entry["ownership"] in OWNERSHIP, f"{entry['id']}: invalid ownership")
    package = ROOT / entry["path"]
    entrypoint = ROOT / entry["entrypoint"]
    expect(package.is_dir(), f"{entry['id']}: missing package directory")
    expect(entrypoint.is_file(), f"{entry['id']}: missing entrypoint")


def validate_skills(data: dict) -> set[str]:
    expect(data.get("layer") == "skills", "skills.json: invalid layer")
    resolved: set[str] = set()
    for entry in data.get("entries", []):
        validate_common(entry, "skill")
        expect(entry["id"] not in resolved, f"duplicate skill ID: {entry['id']}")
        text = (ROOT / entry["entrypoint"]).read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)
        expect(len(frontmatter) >= 3, f"{entry['id']}: SKILL.md lacks frontmatter")
        expect("name:" in frontmatter[1] and "description:" in frontmatter[1], f"{entry['id']}: missing required frontmatter")
        resolved.add(entry["id"])
    expect(resolved, "skills.json: at least one atomic Skill is required")
    return resolved


def external_ids(data: dict) -> set[str]:
    expect(data.get("layer") == "external-skill-references", "external-skills.json: invalid layer")
    expect(data.get("vendored") is False, "external skills must not be vendored by default")
    ids = {entry.get("id") for entry in data.get("entries", [])}
    expect(None not in ids, "external-skills.json: missing external skill ID")
    return ids


def validate_combos(data: dict, permitted_members: set[str]) -> set[str]:
    expect(data.get("layer") == "combo-skills", "combo-skills.json: invalid layer")
    combo_ids: set[str] = set()
    for entry in data.get("entries", []):
        validate_common(entry, "combo skill")
        expect(entry["id"] not in combo_ids, f"duplicate combo ID: {entry['id']}")
        members = entry.get("members", [])
        order = entry.get("order", [])
        expect(len(members) >= 2, f"{entry['id']}: a Combo Skill needs at least two members")
        expect(members == order, f"{entry['id']}: members and order must be explicit and identical")
        expect(set(members).issubset(permitted_members), f"{entry['id']}: Combo Skills may reference only atomic or external skills")
        expect(bool(entry.get("compound_artifact")), f"{entry['id']}: compound artifact is required")
        expect(bool(entry.get("adds")), f"{entry['id']}: incremental value statement is required")
        combo_ids.add(entry["id"])
    expect(combo_ids, "combo-skills.json: at least one Combo Skill is required")
    return combo_ids


def validate_mega(data: dict, skill_ids: set[str], combo_ids: set[str]) -> None:
    expect(data.get("layer") == "mega-skills", "mega-skills.json: invalid layer")
    entries = data.get("entries", [])
    expect(entries, "mega-skills.json: at least one Mega Skill is required")
    seen: set[str] = set()
    for entry in entries:
        validate_common(entry, "mega skill")
        expect(entry["id"] not in seen, f"duplicate mega ID: {entry['id']}")
        expect(entry.get("core_skill") in skill_ids, f"{entry['id']}: core_skill must be an atomic Skill")
        combos = entry.get("conditional_combos", [])
        expect(combos, f"{entry['id']}: at least one conditional Combo Skill is required")
        expect(set(combos).issubset(combo_ids), f"{entry['id']}: unresolved Combo Skill reference")
        expect(len(entry.get("durable_state", [])) >= 5, f"{entry['id']}: durable state contract is incomplete")
        expect(bool(entry.get("mission_output")), f"{entry['id']}: mission output is required")
        expect(bool(entry.get("adds")), f"{entry['id']}: incremental value statement is required")
        seen.add(entry["id"])


def main() -> int:
    try:
        skills = validate_skills(load("skills.json"))
        external = external_ids(load("external-skills.json"))
        combos = validate_combos(load("combo-skills.json"), skills | external)
        validate_mega(load("mega-skills.json"), skills, combos)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    print("Mega Skills hierarchy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
