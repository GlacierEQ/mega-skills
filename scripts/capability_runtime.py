#!/usr/bin/env python3
"""Resolve compact capability packets without loading whole skill documents."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

REGISTRIES = (("atomic", "registry/skills.json"), ("combo", "registry/combo-skills.json"), ("mega", "registry/mega-skills.json"))

def _entries(root: Path):
    for kind, relative in REGISTRIES:
        path = root / relative
        if not path.is_file():
            continue
        for entry in json.loads(path.read_text(encoding="utf-8")).get("entries", []):
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                yield kind, entry

def _score(query: str, entry: dict[str, Any]) -> int:
    needle = query.casefold().strip()
    identifier = entry["id"].casefold()
    if needle == identifier:
        return 100000
    values = [str(entry.get(key, "")) for key in ("id", "display_name", "name", "description", "adds", "maturity")]
    values.extend(str(item) for key in ("tags", "capabilities", "domains") for item in entry.get(key, []) if isinstance(entry.get(key), list))
    text = " ".join(values).casefold()
    if needle in identifier:
        return 10000 + len(needle)
    return sum(100 if term in identifier else 10 for term in needle.split() if term in text)

def _packet(kind: str, entry: dict[str, Any], score: int) -> dict[str, Any]:
    dependencies = {key: entry[key] for key in ("required_combos", "conditional_combos", "members", "dependencies") if key in entry}
    return {"id": entry["id"], "kind": kind, "display_name": entry.get("display_name") or entry.get("name") or entry["id"], "maturity": entry.get("maturity", "unspecified"), "version": entry.get("version", "unspecified"), "ownership": entry.get("ownership", "unspecified"), "contract_ref": entry.get("entrypoint") or entry.get("path") or f"skills/{entry['id']}/SKILL.md", "dependencies": dependencies, "match_score": score}

def resolve_capabilities(root: Path, query: str, *, kinds: set[str] | None = None, limit: int = 12) -> dict[str, Any]:
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    allowed = kinds or {"atomic", "combo", "mega"}
    if unknown := allowed - {"atomic", "combo", "mega"}:
        raise ValueError(f"unknown capability kinds: {sorted(unknown)}")
    matches = [_packet(kind, entry, score) for kind, entry in _entries(root) if kind in allowed if (score := _score(query, entry))]
    matches.sort(key=lambda item: (-item["match_score"], item["kind"], item["id"]))
    return {"schema_version": 1, "query": query, "loaded_registry_metadata_only": True, "result_count": min(len(matches), limit), "capability_packets": matches[:limit]}

def make_state_capsule(mission_id: str, selected: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any]:
    if not mission_id.strip():
        raise ValueError("mission_id must not be empty")
    allowed = {"decisions", "blockers", "next_action", "artifact_refs", "checkpoint"}
    if unknown := set(state) - allowed:
        raise ValueError(f"unsupported state fields: {sorted(unknown)}")
    return {"schema_version": 1, "mission_id": mission_id, "selected_capabilities": [{"id": item["id"], "kind": item["kind"], "version": item["version"]} for item in selected], "state": {key: state[key] for key in sorted(state)}, "history_embedded": False}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query"); parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1]); parser.add_argument("--kind", action="append", choices=("atomic", "combo", "mega")); parser.add_argument("--limit", type=int, default=12); parser.add_argument("--mission-id"); parser.add_argument("--state-json", default="{}")
    args = parser.parse_args(argv)
    result = resolve_capabilities(args.root.resolve(), args.query, kinds=set(args.kind) if args.kind else None, limit=args.limit)
    if args.mission_id:
        state = json.loads(args.state_json)
        if not isinstance(state, dict): raise ValueError("state_json must be a JSON object")
        result["state_capsule"] = make_state_capsule(args.mission_id, result["capability_packets"], state)
    print(json.dumps(result, indent=2, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
