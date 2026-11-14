#!/usr/bin/env python3
"""Task-conditioned capability selection using readiness-assay evidence.

The lexical baseline remains scripts/capability_runtime.py. This module does
not replace it and does not install skills. It re-ranks that baseline's
candidate pool and drops selections the assay marks as unsafe to inject.

Weights below were locked before the live registry comparison. Do not treat
a green unit run as host activation or as a SWE-bench pass-rate claim.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SELECTOR_ID = "evidence_aware_v1"
BASELINE_ID = "lexical_capability_runtime_v1"
ACTIVATION_FLOOR = 50
LEXICAL_CAP = 30
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.]+)?$")

# Assay layer -> capability_runtime kind -> sync_omp_skills selection key.
LAYER_TO_KIND = {"skill": "atomic", "combo": "combo", "mega": "mega"}
KIND_TO_LAYER = {kind: layer for layer, kind in LAYER_TO_KIND.items()}
KIND_TO_OMP = {"atomic": "atomic", "combo": "compound", "mega": "mega"}

STATE_BENEFIT = {
    "behavior_verified": 80,
    "composition_ready": 55,
    "mission_contract_ready": 55,
    "instruction_ready": 35,
    "implementation_unverified": 8,
    "implementation_partial": 4,
    "composition_candidate": 4,
    "mission_candidate": 4,
    "implementation_missing": 0,
    "contract_incomplete": 0,
}
HARD_EXCLUDE_STATES = frozenset({
    "implementation_missing",
    "contract_incomplete",
    "implementation_partial",
    "unassayed",
})


class EvidenceUnavailable(RuntimeError):
    """Raised when selection would have to guess without assay evidence."""


def _load_capability_runtime():
    path = Path(__file__).with_name("capability_runtime.py")
    spec = importlib.util.spec_from_file_location("capability_runtime", path)
    if spec is None or spec.loader is None:
        raise EvidenceUnavailable(f"capability runtime missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_readiness(root: Path) -> dict[str, Any]:
    path = root / "registry" / "skill-readiness.json"
    if not path.is_file():
        raise EvidenceUnavailable(
            f"readiness assay missing: {path}. Refusing to fall back to catalog activation."
        )
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise EvidenceUnavailable("readiness assay must be a JSON object")
    return document


def index_readiness(document: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for layer, key in (("skill", "skills"), ("combo", "combos"), ("mega", "megas")):
        rows = document.get(key) or []
        if not isinstance(rows, list):
            raise EvidenceUnavailable(f"readiness field {key} must be a list")
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                index[(layer, row["id"])] = row
    return index


def _assay_source_ok(assay: dict[str, Any] | None) -> bool:
    if not assay:
        return False
    state = assay.get("state")
    ready = bool(assay.get("ready"))
    if state == "behavior_verified":
        return bool(assay.get("real_implementation_files")) and bool(assay.get("behavioral_tests"))
    if state == "instruction_ready":
        return bool(assay.get("instruction_ready"))
    if state in {"composition_ready", "mission_contract_ready"}:
        return ready
    return False


def _source_compatible(root: Path, packet: dict[str, Any], assay: dict[str, Any] | None) -> bool:
    if not _assay_source_ok(assay):
        return False
    ref = packet.get("contract_ref")
    if (root / "skills").is_dir() and isinstance(ref, str) and ref:
        return (root / ref).exists()
    return True


def score_candidate(packet: dict[str, Any], assay: dict[str, Any] | None) -> dict[str, Any]:
    lexical = int(packet.get("match_score") or 0)
    exact = lexical >= 100000
    state = assay.get("state") if assay else "unassayed"
    if state not in STATE_BENEFIT and state != "unassayed":
        state = "unassayed"
    ready = bool(assay and assay.get("ready"))
    version = packet.get("version")
    version_ok = isinstance(version, str) and bool(SEMVER.fullmatch(version))
    maturity_conflict = packet.get("maturity") == "active" and assay is not None and not ready
    source_ok = _assay_source_ok(assay)
    lexical_component = LEXICAL_CAP if exact else min(max(lexical, 0), LEXICAL_CAP)
    score = STATE_BENEFIT.get(state, 0) + lexical_component
    if source_ok:
        score += 15
    if version_ok:
        score += 5
    if ready:
        score += 10
    if maturity_conflict:
        score -= 25
    would_exclude = state in HARD_EXCLUDE_STATES or assay is None
    would_floor = score < ACTIVATION_FLOOR
    hard_excluded = (not exact) and would_exclude
    below_floor = (not exact) and would_floor
    return {
        "id": packet["id"],
        "kind": packet.get("kind"),
        "evidence_score": score,
        "lexical_score": lexical,
        "state": state,
        "ready": ready,
        "source_compatible": source_ok,
        "version_present": version_ok,
        "version": version if isinstance(version, str) else None,
        "maturity_conflict": maturity_conflict,
        "hard_excluded": hard_excluded,
        "below_floor": below_floor,
        "operator_exact_override": exact and (would_exclude or would_floor),
        "contract_ref": packet.get("contract_ref"),
    }


def _apply_source_files(root: Path, packet: dict[str, Any], row: dict[str, Any], assay: dict[str, Any] | None) -> dict[str, Any]:
    """Drop filesystem-incompatible rows only when a skill tree is checked out."""
    if not (root / "skills").is_dir():
        return row
    if row["operator_exact_override"]:
        row["source_file_missing"] = not _source_compatible(root, packet, assay) and row["source_compatible"]
        return row
    if row["source_compatible"] and not _source_compatible(root, packet, assay):
        row = dict(row)
        row["source_compatible"] = False
        row["source_file_missing"] = True
        row["evidence_score"] = row["evidence_score"] - 15
        if not row["operator_exact_override"]:
            row["hard_excluded"] = True
        row["below_floor"] = row["evidence_score"] < ACTIVATION_FLOOR
    return row


def select_evidence_aware(
    root: Path,
    query: str,
    *,
    limit: int = 5,
    readiness: dict[str, Any] | None = None,
    kinds: set[str] | None = None,
    runtime: Any | None = None,
) -> dict[str, Any]:
    if not 1 <= limit <= 30:
        raise ValueError("limit must be between 1 and 30")
    runtime = runtime or _load_capability_runtime()
    # Pull the full lexical pool the baseline would rank, then re-rank it.
    baseline = runtime.resolve_capabilities(root, query, kinds=kinds, limit=100)
    document = readiness if readiness is not None else load_readiness(root)
    index = index_readiness(document)
    ranked = []
    for packet in baseline["capability_packets"]:
        layer = KIND_TO_LAYER.get(packet.get("kind"))
        assay = index.get((layer, packet["id"])) if layer else None
        row = score_candidate(packet, assay)
        row = _apply_source_files(root, packet, row, assay)
        ranked.append(row)
    ranked.sort(key=lambda item: (-item["evidence_score"], -item["lexical_score"], item["kind"] or "", item["id"]))
    selected = []
    for row in ranked:
        admit = row["operator_exact_override"] or (not row["hard_excluded"] and not row["below_floor"])
        if admit:
            selected.append(row)
        if len(selected) >= limit:
            break
    return {
        "schema_version": SCHEMA_VERSION,
        "selector": SELECTOR_ID,
        "baseline_selector": BASELINE_ID,
        "query": query,
        "limit": limit,
        "candidate_count": len(ranked),
        "hard_excluded_count": sum(1 for row in ranked if row["hard_excluded"]),
        "below_floor_count": sum(1 for row in ranked if row["below_floor"] and not row["hard_excluded"]),
        "selected": selected,
        "selected_ids": [row["id"] for row in selected],
        "omp_selection": omp_selection(selected),
        "loaded_skill_documents": False,
        "activation_performed": False,
    }


def omp_selection(selected: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped = {"atomic": [], "compound": [], "mega": []}
    for row in selected:
        key = KIND_TO_OMP.get(row.get("kind") or "")
        if key and row["id"] not in grouped[key]:
            grouped[key].append(row["id"])
    return grouped


def coalition_ids(selection: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for key in ("atomic", "compound", "mega", "combo"):
        for name in selection.get(key) or ():
            if name not in found:
                found.append(name)
    return found


def compare_tasks(
    root: Path,
    tasks: list[dict[str, Any]],
    *,
    limit: int = 5,
    readiness: dict[str, Any] | None = None,
    coalition: dict[str, Any] | None = None,
    runtime: Any | None = None,
) -> dict[str, Any]:
    """Compare fixed-coalition, lexical top-k, and evidence selection.

    Each task is {id, query, relevant?: [id], forbidden_ids?: [id]}.
    A forbidden injection is a selected id listed in forbidden_ids, or a
    selected row whose assay state is implementation_unverified,
    contract_incomplete, implementation_missing, or implementation_partial.
    """
    runtime = runtime or _load_capability_runtime()
    document = readiness if readiness is not None else load_readiness(root)
    index = index_readiness(document)
    forbidden_states = HARD_EXCLUDE_STATES | {"implementation_unverified"}
    per_task = []
    for task in tasks:
        query = task["query"]
        relevant = list(task.get("relevant") or [])
        forbidden = set(task.get("forbidden_ids") or [])
        lexical = runtime.resolve_capabilities(root, query, limit=limit)
        evidence = select_evidence_aware(root, query, limit=limit, readiness=document, runtime=runtime)
        lexical_ids = [packet["id"] for packet in lexical["capability_packets"]]
        evidence_ids = evidence["selected_ids"]
        fixed = coalition_ids(coalition) if coalition else []

        def injections(ids: list[str]) -> list[str]:
            bad = []
            for identifier in ids:
                if identifier in forbidden:
                    bad.append(identifier)
                    continue
                assay = index.get(("skill", identifier)) or index.get(("combo", identifier)) or index.get(("mega", identifier))
                if assay and assay.get("state") in forbidden_states:
                    bad.append(identifier)
            return bad

        def hits(ids: list[str]) -> list[str]:
            return [identifier for identifier in relevant if identifier in ids]

        per_task.append({
            "id": task.get("id") or query,
            "query": query,
            "relevant": relevant,
            "lexical_selected": lexical_ids,
            "evidence_selected": evidence_ids,
            "coalition_size": len(fixed),
            "lexical_hits": hits(lexical_ids),
            "evidence_hits": hits(evidence_ids),
            "coalition_hits": hits(fixed),
            "lexical_forbidden": injections(lexical_ids),
            "evidence_forbidden": injections(evidence_ids),
            "coalition_forbidden": injections(fixed),
        })

    def mean(key: str) -> float:
        values = [len(item[key]) for item in per_task]
        return round(sum(values) / len(values), 4) if values else 0.0

    summary = {
        "tasks": len(per_task),
        "limit": limit,
        "activation_floor": ACTIVATION_FLOOR,
        "lexical_cap": LEXICAL_CAP,
        "evidence_gold_hits": sum(1 for item in per_task if not item["relevant"] or item["evidence_hits"]),
        "lexical_gold_hits": sum(1 for item in per_task if not item["relevant"] or item["lexical_hits"]),
        "coalition_gold_hits": sum(1 for item in per_task if not item["relevant"] or item["coalition_hits"]),
        "evidence_mean_selected": mean("evidence_selected"),
        "lexical_mean_selected": mean("lexical_selected"),
        "coalition_selected": len(coalition_ids(coalition)) if coalition else None,
        "evidence_forbidden_total": sum(len(item["evidence_forbidden"]) for item in per_task),
        "lexical_forbidden_total": sum(len(item["lexical_forbidden"]) for item in per_task),
        "coalition_forbidden_total": sum(len(item["coalition_forbidden"]) for item in per_task),
        "weights_locked": True,
    }
    return {"schema_version": SCHEMA_VERSION, "summary": summary, "tasks": per_task}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--compare", type=Path, help="JSON list of fixed tasks")
    parser.add_argument("--coalition-json", type=Path, help="Optional fixed coalition selection")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.compare:
        tasks = json.loads(args.compare.read_text(encoding="utf-8"))
        if not isinstance(tasks, list):
            raise SystemExit("compare file must be a JSON list")
        coalition = json.loads(args.coalition_json.read_text(encoding="utf-8")) if args.coalition_json else None
        print(json.dumps(compare_tasks(root, tasks, limit=args.limit, coalition=coalition), indent=2, sort_keys=True))
        return 0
    if not args.query:
        parser.error("query is required unless --compare is set")
    print(json.dumps(select_evidence_aware(root, args.query, limit=args.limit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
