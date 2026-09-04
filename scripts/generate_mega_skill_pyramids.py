#!/usr/bin/env python3
"""Generate and validate recursively composable Mega-Skill pyramid graphs."""

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


def ordered_unique(values):
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def typed_key(kind: str, node_id: str) -> str:
    aliases = {"skill": "atomic", "compound-skill": "compound", "external-skill": "external", "mega": "mega"}
    return f"{aliases[kind]}:{node_id}"


def combo_adjacency(combos: list[dict]) -> dict[str, list[str]]:
    combo_ids = {entry["id"] for entry in combos}
    return {combo["id"]: [member["id"] for member in combo.get("members", []) if member.get("kind") == "compound-skill" and member["id"] in combo_ids] for combo in combos}


def assert_acyclic(graph: dict[str, list[str]]) -> None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        mark = state.get(node, 0)
        if mark == 2:
            return
        if mark == 1:
            start = stack.index(node)
            cycle = stack[start:] + [node]
            raise ValueError("compound-skill cycle: " + " -> ".join(cycle))
        state[node] = 1
        stack.append(node)
        for child in graph.get(node, []):
            visit(child)
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        visit(node)


def catalog_entry(kind: str, entry: dict) -> dict:
    node_id = entry["id"]
    key = typed_key(kind, node_id)
    common = {"key": key, "id": node_id, "skill_kind": key.split(":", 1)[0], "proper_skill": True, "display_name": entry.get("display_name", node_id), "ownership": entry.get("ownership", "external-platform" if kind == "external-skill" else "glaciereq"), "maturity": entry.get("maturity"), "version": entry.get("version"), "source": entry.get("entrypoint") or entry.get("source")}
    if kind == "skill":
        common.update({"purpose": entry.get("purpose"), "input_contract": entry.get("input_contract", []), "output_contract": entry.get("output_contract", []), "artifact_contract": entry.get("output_contract", []), "validation_boundary": entry.get("local_validation", [])})
    elif kind == "compound-skill":
        execution = entry.get("execution", {}).get("ordered_steps", [])
        integration = entry.get("integration", {})
        compounding = entry.get("compounding", {})
        common.update({"selection": entry.get("selection", {}), "artifact_contract": compounding.get("compound_artifact"), "adds": compounding.get("adds"), "validation_boundary": {"ordered_step_validations": [{"member_id": step.get("member_id"), "validation": step.get("validation")} for step in execution], "quality_gates": integration.get("quality_gates", []), "next_layer_ready_when": compounding.get("next_layer_ready_when", [])}})
    elif kind == "mega":
        firewall = entry.get("firewall", {})
        common.update({"mission_output": entry.get("mission_output"), "artifact_contract": entry.get("mission_output"), "durable_state": entry.get("durable_state", []), "adds": entry.get("adds"), "validation_boundary": {"required_evidence": firewall.get("required_evidence", []), "approval_required_for": firewall.get("approval_required_for", []), "human_control": firewall.get("human_control")}})
    else:
        common.update({"role": entry.get("role"), "installed_version_id": entry.get("installed_version_id"), "artifact_contract": "external capability output", "validation_boundary": ["External capability validation remains bound to the referenced platform/version."]})
    return common


def build() -> dict:
    skills = load("skills.json")["entries"]
    combos = load("combo-skills.json")["entries"]
    megas = load("mega-skills.json")["entries"]
    external = load("external-skills.json")["entries"]
    skill_by = {entry["id"]: entry for entry in skills}
    combo_by = {entry["id"]: entry for entry in combos}
    external_by = {entry["id"]: entry for entry in external}
    assert_acyclic(combo_adjacency(combos))
    unresolved: list[dict] = []
    entries: list[dict] = []
    node_catalog: dict[str, dict] = {}
    global_usage: dict[str, set[str]] = defaultdict(set)

    def resolve_member(member: dict, owner_combo: str):
        member_id = member["id"]
        kind = member.get("kind", "skill")
        source = {"skill": skill_by, "compound-skill": combo_by, "external-skill": external_by}.get(kind)
        if source is None or member_id not in source:
            unresolved.append({"compound_skill": owner_combo, "member_id": member_id, "member_kind": kind})
            return kind, None
        return kind, source[member_id]

    def register(kind: str, entry: dict) -> str:
        key = typed_key(kind, entry["id"])
        if key not in node_catalog:
            node_catalog[key] = catalog_entry(kind, entry)
        return key

    for mega in megas:
        root_id = mega["id"]
        root_key = register("mega", mega)
        required = mega.get("required_combos", [])
        conditional = mega.get("conditional_combos", [])
        roots = ordered_unique(required + conditional + mega.get("combos", []))
        depths: dict[str, set[int]] = defaultdict(set)
        paths: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        parents: dict[str, set[str]] = defaultdict(set)
        edges: list[dict] = []
        edge_keys: set[tuple] = set()
        depths[root_key].add(0)
        paths[root_key].add((root_key,))
        global_usage[root_key].add(root_id)

        def add_edge(edge: dict) -> None:
            dedupe = (edge["from_key"], edge["to_key"], edge["relation"], edge.get("role"), edge.get("required"))
            if dedupe not in edge_keys:
                edge_keys.add(dedupe)
                edges.append(edge)

        def descend_combo(combo_id: str, depth: int, path: tuple[str, ...], relation: str, parent_key: str, role: str | None = None, required_flag: bool | None = None) -> None:
            combo = combo_by.get(combo_id)
            if combo is None:
                unresolved.append({"mega": root_id, "missing_compound_skill": combo_id})
                return
            combo_key = register("compound-skill", combo)
            depths[combo_key].add(depth)
            paths[combo_key].add(path + (combo_key,))
            parents[combo_key].add(parent_key)
            global_usage[combo_key].add(root_id)
            add_edge({"from_key": parent_key, "from_id": parent_key.split(":", 1)[1], "to_key": combo_key, "to_id": combo_id, "relation": relation, "required": required_flag if required_flag is not None else relation == "required", "role": role or ("required compound workflow" if relation == "required" else "conditional compound workflow"), "artifact_contract": combo.get("compounding", {}).get("compound_artifact"), "validation_boundary": combo.get("compounding", {}).get("next_layer_ready_when", [])})
            execution_by_member: dict[str, list[dict]] = defaultdict(list)
            for step in combo.get("execution", {}).get("ordered_steps", []):
                execution_by_member[step.get("member_id")].append({"step": step.get("step"), "consumes": step.get("consumes", []), "produces": step.get("produces", []), "validation": step.get("validation")})
            for member in combo.get("members", []):
                member_id = member["id"]
                kind, child = resolve_member(member, combo_id)
                if child is None:
                    continue
                child_key = register(kind, child)
                child_depth = depth + 1
                depths[child_key].add(child_depth)
                paths[child_key].add(path + (combo_key, child_key))
                parents[child_key].add(combo_key)
                global_usage[child_key].add(root_id)
                steps = execution_by_member.get(member_id, [])
                if kind == "compound-skill":
                    descend_combo(member_id, child_depth, path + (combo_key,), "compound-member", combo_key, member.get("role"), member.get("required"))
                else:
                    add_edge({"from_key": combo_key, "from_id": combo_id, "to_key": child_key, "to_id": member_id, "relation": "member", "required": bool(member.get("required", False)), "role": member.get("role"), "member_kind": kind, "execution_steps": steps, "artifact_contract": [artifact for step in steps for artifact in step.get("produces", [])], "validation_boundary": [step.get("validation") for step in steps if step.get("validation")]})

        for combo_id in roots:
            relation = "required" if combo_id in required else "conditional"
            descend_combo(combo_id, 1, (root_key,), relation, root_key)

        node_refs = [{"key": key, "id": key.split(":", 1)[1], "skill_kind": key.split(":", 1)[0], "depths": sorted(depths[key])} for key in sorted(depths, key=lambda key: (min(depths[key]), key.split(":", 1)[0], key.split(":", 1)[1]))]
        lineage = []
        for key in sorted(paths):
            node_paths = sorted(paths[key])
            node_parents = sorted(parents.get(key, set()))
            if len(node_paths) > 1 or len(node_parents) > 1:
                lineage.append({"key": key, "id": key.split(":", 1)[1], "skill_kind": key.split(":", 1)[0], "parent_keys": node_parents, "paths_from_root": [list(item) for item in node_paths]})
        entries.append({"id": root_id, "display_name": mega.get("display_name", root_id), "root_key": root_key, "root_skill_id": root_id, "shape": "hierarchical-pyramid", "machine_shape": "directed-acyclic-graph", "max_depth": max((max(values) for values in depths.values()), default=0), "node_refs": node_refs, "edges": sorted(edges, key=lambda item: (item["from_key"], item["to_key"], item["relation"])), "shared_node_lineage": lineage, "validation": {"unresolved_owned_references": 0, "compound_cycles": 0}})

    if unresolved:
        raise ValueError("unresolved pyramid references: " + json.dumps(unresolved, indent=2))
    global_shared = [{"key": key, "id": key.split(":", 1)[1], "skill_kind": key.split(":", 1)[0], "mega_skill_ids": sorted(mega_ids), "mega_skill_count": len(mega_ids)} for key, mega_ids in sorted(global_usage.items()) if len(mega_ids) > 1]
    external_member_references = sum(1 for combo in combos for member in combo.get("members", []) if member.get("kind") == "external-skill")
    return {"schema_version": 2, "ontology": "recursive-proper-skill-pyramid", "source_registries": {"atomic": "registry/skills.json", "compound": "registry/combo-skills.json", "mega": "registry/mega-skills.json", "external": "registry/external-skills.json"}, "identity_rule": "Exact IDs are preserved; typed node keys disambiguate IDs reused across atomic, compound, mega, or external Skill kinds.", "counts": {"atomic_skills": len(skills), "compound_skills": len(combos), "mega_skills": len(megas), "external_registry_entries": len(external), "external_member_references": external_member_references, "mega_pyramids": len(entries), "catalog_nodes_used_by_megas": len(node_catalog), "unresolved_owned_references": 0, "compound_cycles": 0}, "node_catalog": [node_catalog[key] for key in sorted(node_catalog)], "entries": entries, "global_shared_node_lineage": global_shared}


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
            print(f"invalid registry/mega-skill-pyramids.json: {exc}", file=sys.stderr)
            return 1
        if current != data:
            print("registry/mega-skill-pyramids.json is semantically stale; run scripts/generate_mega_skill_pyramids.py", file=sys.stderr)
            return 1
    else:
        OUT.write_text(render(data), encoding="utf-8")
    print(json.dumps({"ok": True, "counts": data["counts"], "pyramids": len(data["entries"]), "mode": "check" if args.check else "write"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
