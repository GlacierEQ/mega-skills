#!/usr/bin/env python3
"""Generate and validate the canonical recursive Mega-Skill DAG projection."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry"
OUT = REG / "mega-skill-pyramids.json"


def load(name: str) -> dict:
    return json.loads((REG / name).read_text(encoding="utf-8"))


def node_key(kind: str, node_id: str) -> str:
    prefix = {
        "skill": "atomic",
        "compound-skill": "compound",
        "external-skill": "external",
        "mega": "mega",
    }[kind]
    return f"{prefix}:{node_id}"


def find_cycle(adjacency: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        mark = state.get(node, 0)
        if mark == 2:
            return None
        if mark == 1:
            start = stack.index(node)
            return stack[start:] + [node]
        state[node] = 1
        stack.append(node)
        for child in sorted(adjacency.get(node, [])):
            cycle = visit(child)
            if cycle:
                return cycle
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(adjacency):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def build() -> dict:
    skills = load("skills.json")["entries"]
    combos = load("combo-skills.json")["entries"]
    megas = load("mega-skills.json")["entries"]
    external = load("external-skills.json")["entries"]

    skill_ids = {entry["id"] for entry in skills}
    combo_ids = {entry["id"] for entry in combos}
    external_ids = {entry["id"] for entry in external}
    adjacency: dict[str, list[str]] = {entry["id"]: [] for entry in combos}
    unresolved: list[dict] = []
    leaf_keys: set[str] = set()
    parent_keys: dict[str, set[str]] = defaultdict(set)

    compound_nodes = []
    for combo in combos:
        members = []
        for member in combo.get("members", []):
            member_id = member["id"]
            kind = member.get("kind", "skill")
            valid = (
                member_id in skill_ids if kind == "skill"
                else member_id in combo_ids if kind == "compound-skill"
                else member_id in external_ids if kind == "external-skill"
                else False
            )
            if not valid:
                unresolved.append({"compound_skill": combo["id"], "member_id": member_id, "member_kind": kind})
                continue
            key = node_key(kind, member_id)
            members.append({"key": key, "kind": kind, "required": bool(member.get("required", False)), "role": member.get("role")})
            parent_keys[key].add(node_key("compound-skill", combo["id"]))
            if kind == "compound-skill":
                adjacency[combo["id"]].append(member_id)
            else:
                leaf_keys.add(key)
        compound_nodes.append({"key": node_key("compound-skill", combo["id"]), "id": combo["id"], "members": members})

    cycle = find_cycle(adjacency)
    if cycle:
        raise ValueError("compound-skill cycle: " + " -> ".join(cycle))

    mega_roots = []
    for mega in megas:
        required = mega.get("required_combos", [])
        conditional = mega.get("conditional_combos", [])
        missing = sorted((set(required) | set(conditional)) - combo_ids)
        if missing:
            unresolved.append({"mega": mega["id"], "missing_compound_skills": missing})
        root = node_key("mega", mega["id"])
        required_keys = [node_key("compound-skill", item) for item in required]
        conditional_keys = [node_key("compound-skill", item) for item in conditional]
        for key in required_keys + conditional_keys:
            parent_keys[key].add(root)
        mega_roots.append({"key": root, "id": mega["id"], "required_compound_keys": required_keys, "conditional_compound_keys": conditional_keys})

    if unresolved:
        raise ValueError("unresolved recursive Skill references: " + json.dumps(unresolved, indent=2))

    shared = [
        {"key": key, "parent_keys": sorted(parents)}
        for key, parents in sorted(parent_keys.items())
        if len(parents) > 1
    ]
    external_member_refs = sum(
        1 for combo in combos for member in combo.get("members", [])
        if member.get("kind") == "external-skill"
    )

    return {
        "schema_version": 2,
        "ontology": "recursive-proper-skill-pyramid",
        "identity_rule": "Every node is a proper Skill. Exact IDs are preserved; typed keys disambiguate cross-layer identity.",
        "source_registries": {
            "atomic": "registry/skills.json",
            "compound": "registry/combo-skills.json",
            "mega": "registry/mega-skills.json",
            "external": "registry/external-skills.json",
        },
        "contract_paths": {
            "mega": {"artifact": "mission_output", "validation": ["firewall.required_evidence", "firewall.human_control"]},
            "compound": {"artifact": "compounding.compound_artifact", "validation": ["integration.quality_gates", "compounding.next_layer_ready_when"]},
            "atomic": {"artifact": "output_contract", "validation": ["local_validation"]},
            "member_edge": {"role": "members[].role", "artifact": "execution.ordered_steps[].produces", "validation": "execution.ordered_steps[].validation"},
        },
        "expansion_contract": {
            "start": "mega_roots[].required_compound_keys + conditional_compound_keys",
            "recurse": "compound_nodes[].members where kind == compound-skill",
            "stop": "atomic:* or external:*",
            "cycle_policy": "reject",
            "unresolved_owned_reference_policy": "reject",
        },
        "counts": {
            "atomic_skills": len(skills),
            "compound_skills": len(combos),
            "mega_skills": len(megas),
            "external_member_references": external_member_refs,
            "mega_pyramids": len(mega_roots),
            "unresolved_owned_references": 0,
            "compound_cycles": 0,
        },
        "mega_roots": mega_roots,
        "compound_nodes": compound_nodes,
        "leaf_keys": sorted(leaf_keys),
        "shared_node_lineage": shared,
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data = build()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.check:
        if not OUT.exists():
            print("missing registry/mega-skill-pyramids.json", file=sys.stderr)
            return 1
        try:
            current = json.loads(OUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"invalid pyramid registry: {exc}", file=sys.stderr)
            return 1
        if current != data:
            print("registry/mega-skill-pyramids.json is stale; run scripts/generate_mega_skill_pyramids.py", file=sys.stderr)
            return 1
    else:
        OUT.write_text(render(data), encoding="utf-8")

    print(json.dumps({"ok": True, "pyramids": len(data["mega_roots"]), "compound_nodes": len(data["compound_nodes"]), "leaf_nodes": len(data["leaf_keys"]), "counts": data["counts"], "mode": "check" if args.check else "write"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
