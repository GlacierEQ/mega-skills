#!/usr/bin/env python3
"""Validate the GlacierEQ Skills → Combo Skills → Mega Skills hierarchy."""

from __future__ import annotations

import json
import re
from pathlib import Path

from firewall import REQUIRED_FORBIDDEN, validate_policy


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
COMBO_SCHEMA = ROOT / "schemas" / "combo-skill.schema.json"
COMBO_TEMPLATE = ROOT / "combo-skills" / "_template" / "COMBO.md"
FIREWALL_SCHEMA = ROOT / "schemas" / "firewall.schema.json"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OWNERSHIP = {"glaciereq", "external-platform", "candidate"}


def load_registry(name: str) -> dict:
    path = REGISTRY / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read registry/{name}: {exc}") from exc


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty_strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate_common(entry: dict, expected_layer: str) -> None:
    for field in ("id", "display_name", "ownership", "maturity", "version", "path", "entrypoint"):
        expect(bool(entry.get(field)), f"{expected_layer}: missing {field}")
    expect(bool(ID_PATTERN.fullmatch(entry["id"])), f"{expected_layer}: invalid ID {entry['id']}")
    expect(entry["ownership"] in OWNERSHIP, f"{entry['id']}: invalid ownership")
    expect(bool(re.fullmatch(r"\d+\.\d+\.\d+", entry["version"])), f"{entry['id']}: invalid semantic version")
    package = ROOT / entry["path"]
    entrypoint = ROOT / entry["entrypoint"]
    expect(package.is_dir(), f"{entry['id']}: missing package directory")
    expect(entrypoint.is_file(), f"{entry['id']}: missing entrypoint")


def unregistered_packages(layer_dir: Path, registered: set[str], manifest: str) -> list[str]:
    return sorted(
        path.parent.name
        for path in layer_dir.glob(f"*/{manifest}")
        if path.parent.name != "_template" and path.parent.name not in registered
    )


def expect_all_registered(layer_dir: Path, registered: set[str], manifest: str, registry_name: str) -> None:
    missing = unregistered_packages(layer_dir, registered, manifest)
    expect(not missing, f"{registry_name}: packages on disk but not registered: {', '.join(missing)}")


def validate_skills(data: dict) -> set[str]:
    expect(data.get("schema_version") == 1, "skills.json: unsupported schema version")
    expect(data.get("layer") == "skills", "skills.json: invalid layer")
    resolved: set[str] = set()
    for entry in data.get("entries", []):
        validate_common(entry, "skill")
        expect(entry["id"] not in resolved, f"duplicate skill ID: {entry['id']}")
        for field in ("purpose", "input_contract", "output_contract", "local_validation", "does_not_own"):
            expect(bool(entry.get(field)), f"{entry['id']}: missing {field}")
        text = (ROOT / entry["entrypoint"]).read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)
        expect(len(frontmatter) >= 3, f"{entry['id']}: SKILL.md lacks frontmatter")
        expect("name:" in frontmatter[1] and "description:" in frontmatter[1], f"{entry['id']}: missing required frontmatter")
        expect(f"name: {entry['id']}" in frontmatter[1], f"{entry['id']}: registry and SKILL.md name differ")
        resolved.add(entry["id"])
    expect(len(resolved) >= 2, "skills.json: the initial graph needs more than one atomic Skill")
    expect_all_registered(ROOT / "skills", resolved, "SKILL.md", "skills.json")
    readiness_path = REGISTRY / "skill-readiness.json"
    if readiness_path.is_file():
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in readiness.get("skills", [])}
        for entry in data.get("entries", []):
            state = by_id.get(entry["id"])
            expect(state is not None, f'{entry["id"]}: missing readiness record')
            if readiness.get("pass") == 2 and entry.get("maturity") == "active":
                expect(state.get("ready") is True, f'{entry["id"]}: active skill lacks readiness evidence')
    return resolved


def external_ids(data: dict) -> set[str]:
    expect(data.get("layer") == "external-skill-references", "external-skills.json: invalid layer")
    expect(data.get("vendored") is False, "external skills must not be vendored by default")
    ids: set[str] = set()
    for entry in data.get("entries", []):
        skill_id = entry.get("id")
        expect(isinstance(skill_id, str) and ID_PATTERN.fullmatch(skill_id), "external-skills.json: invalid external skill ID")
        expect(skill_id not in ids, f"duplicate external skill ID: {skill_id}")
        expect(bool(entry.get("role")) and bool(entry.get("installed_version_id")), f"{skill_id}: incomplete external reference")
        ids.add(skill_id)
    return ids


def validate_combo_document(entry: dict) -> None:
    text = (ROOT / entry["entrypoint"]).read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)
    expect(len(frontmatter) >= 3, f"{entry['id']}: COMBO.md lacks frontmatter")
    metadata = frontmatter[1]
    expect(f"id: {entry['id']}" in metadata, f"{entry['id']}: COMBO.md ID differs from registry")
    expect("schema: ../../schemas/combo-skill.schema.json" in metadata, f"{entry['id']}: COMBO.md must link the canonical schema")
    expect("status: active" in metadata or "status: candidate" in metadata, f"{entry['id']}: COMBO.md lacks a valid status")


def validate_combos(data: dict, skill_ids: set[str], external: set[str]) -> set[str]:
    expect(data.get("schema_version") == 2, "combo-skills.json: unsupported schema version")
    expect(data.get("layer") == "combo-skills", "combo-skills.json: invalid layer")
    expect(data.get("schema") == "../schemas/combo-skill.schema.json", "combo-skills.json: missing canonical schema reference")
    expect(COMBO_SCHEMA.is_file() and COMBO_TEMPLATE.is_file(), "combo schema or template is missing")
    try:
        schema = json.loads(COMBO_SCHEMA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"combo schema is invalid JSON: {exc}") from exc
    expect("integration" in schema.get("required", []), "combo schema must require integration")
    combo_ids: set[str] = set()
    for entry in data.get("entries", []):
        validate_common(entry, "combo skill")
        validate_combo_document(entry)
        expect(entry["id"] not in combo_ids, f"duplicate combo ID: {entry['id']}")
        selection = entry.get("selection")
        expect(isinstance(selection, dict) and nonempty_strings(selection.get("use_when")) and nonempty_strings(selection.get("do_not_use_when")), f"{entry['id']}: selection contract is incomplete")
        members = entry.get("members")
        expect(isinstance(members, list) and len(members) >= 2, f"{entry['id']}: a Combo Skill needs at least two members")
        member_ids: list[str] = []
        for member in members:
            expect(isinstance(member, dict), f"{entry['id']}: member must be an object")
            member_id, kind = member.get("id"), member.get("kind")
            expect(isinstance(member_id, str) and ID_PATTERN.fullmatch(member_id), f"{entry['id']}: invalid member ID")
            expect(kind in {"skill", "external-skill"}, f"{entry['id']}: invalid member kind for {member_id}")
            expect(isinstance(member.get("required"), bool) and bool(member.get("role")), f"{entry['id']}: member {member_id} has an incomplete contract")
            expect(member_id not in member_ids, f"{entry['id']}: duplicate member {member_id}")
            expect(member_id in (skill_ids if kind == "skill" else external), f"{entry['id']}: {member_id} does not resolve as {kind}")
            member_ids.append(member_id)
        steps = entry.get("execution", {}).get("ordered_steps")
        expect(isinstance(steps, list) and len(steps) >= 2, f"{entry['id']}: ordered execution is incomplete")
        expect([step.get("step") for step in steps] == list(range(1, len(steps) + 1)), f"{entry['id']}: steps must be contiguous and ordered")
        for step in steps:
            expect(step.get("member_id") in member_ids, f"{entry['id']}: step has an unresolved member")
            expect(nonempty_strings(step.get("consumes")) and nonempty_strings(step.get("produces")) and bool(step.get("validation")), f"{entry['id']}: step {step.get('step')} lacks integration contract")
        integration = entry.get("integration")
        expect(isinstance(integration, dict), f"{entry['id']}: integration object is missing")
        for field in ("handoffs", "evidence_requirements", "risk_boundaries", "quality_gates", "state_updates"):
            expect(nonempty_strings(integration.get(field)) if field != "handoffs" else isinstance(integration.get(field), list) and bool(integration["handoffs"]), f"{entry['id']}: integration.{field} is missing")
        for handoff in integration["handoffs"]:
            expect(isinstance(handoff, dict), f"{entry['id']}: handoff must be an object")
            expect(handoff.get("from_member") in member_ids and handoff.get("to_member") in member_ids, f"{entry['id']}: handoff references unknown members")
            expect(nonempty_strings(handoff.get("required_inputs")) and nonempty_strings(handoff.get("accepted_outputs")) and bool(handoff.get("failure_owner")), f"{entry['id']}: handoff is incomplete")
        compounding = entry.get("compounding")
        expect(isinstance(compounding, dict), f"{entry['id']}: compounding object is missing")
        expect(nonempty_strings(compounding.get("inherits")) and bool(compounding.get("adds")) and bool(compounding.get("compound_artifact")) and nonempty_strings(compounding.get("next_layer_ready_when")), f"{entry['id']}: compounding contract is incomplete")
        combo_ids.add(entry["id"])
    expect(combo_ids, "combo-skills.json: at least one Combo Skill is required")
    expect_all_registered(ROOT / "combo-skills", combo_ids, "COMBO.md", "combo-skills.json")
    return combo_ids


def validate_firewall_contract(policy: object, mega_id: str) -> None:
    expect(isinstance(policy, dict), f"{mega_id}: firewall policy is missing")
    validate_policy(policy, mega_id)
    expect(FIREWALL_SCHEMA.is_file(), "firewall schema is missing")
    try:
        schema = json.loads(FIREWALL_SCHEMA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"firewall schema is invalid JSON: {exc}") from exc
    expect(schema.get("properties", {}).get("mode", {}).get("const") == "read_only", "firewall schema must enforce read_only mode")
    expect(set(REQUIRED_FORBIDDEN).issubset(policy["forbidden_actions"]), f"{mega_id}: mandatory firewall denials are incomplete")


def validate_mega(data: dict, combo_ids: set[str]) -> None:
    expect(data.get("schema_version") == 2, "mega-skills.json: unsupported schema version")
    expect(data.get("layer") == "mega-skills", "mega-skills.json: invalid layer")
    entries = data.get("entries", [])
    expect(entries, "mega-skills.json: at least one Mega Skill is required")
    expect(not list((ROOT / "combo-skills").glob("*/SKILL.md")), "combo layer contains copied SKILL.md methods")
    expect(not list((ROOT / "mega-skills").glob("*/SKILL.md")), "mega layer contains copied SKILL.md methods")
    seen: set[str] = set()
    for entry in entries:
        validate_common(entry, "mega skill")
        validate_firewall_contract(entry.get("firewall"), entry["id"])
        expect(entry["id"] not in seen, f"duplicate mega ID: {entry['id']}")
        required = entry.get("required_combos")
        conditional = entry.get("conditional_combos")
        expect(nonempty_strings(required), f"{entry['id']}: at least one required Combo Skill is required")
        expect(isinstance(conditional, list), f"{entry['id']}: conditional_combos must be a list")
        all_combos = set(required) | set(conditional)
        expect(all_combos.issubset(combo_ids), f"{entry['id']}: unresolved Combo Skill reference")
        expect(not set(required).intersection(conditional), f"{entry['id']}: Combo cannot be both required and conditional")
        expect("capability-readiness" in conditional, f"{entry['id']}: must include capability-readiness as a conditional route")
        expect(len(entry.get("durable_state", [])) >= 5, f"{entry['id']}: durable state contract is incomplete")
        expect(bool(entry.get("mission_output")) and bool(entry.get("adds")), f"{entry['id']}: mission integration contract is incomplete")
        seen.add(entry["id"])
    expect_all_registered(ROOT / "mega-skills", seen, "MEGA.md", "mega-skills.json")


def main() -> int:
    try:
        skills = validate_skills(load_registry("skills.json"))
        external = external_ids(load_registry("external-skills.json"))
        combos = validate_combos(load_registry("combo-skills.json"), skills, external)
        validate_mega(load_registry("mega-skills.json"), combos)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    print("Mega Skills hierarchy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
