#!/usr/bin/env python3
"""Evidence-aware OMP skill selector (treatment T1).

This module chooses a coalition of canonical registry ids from a task
descriptor and an append-only evidence ledger. It does not install skills,
write profiles, or own OMP activation. Installers keep that job and may
pass the returned coalition as ``selection`` to ``sync_omp_skills``.

B1 is the frozen 30-skill coalition from PR #51 (merge da26fa48). It is the
comparison baseline and the only fallback when a task family has no usable
evidence. The selector never invents a replacement default bundle.

Scoring uses demonstrated task-family benefit only: pass/fail, regressions,
mean wall time, and a cost proxy (canonical contract bytes). Catalog prestige
and raw skill count do not increase a score. Evidence does not transfer
across task families.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

SELECTOR_SCHEMA_VERSION = 1
LEDGER_SCHEMA_VERSION = 1
SELECTOR_ID = "evidence_aware_omp_t1"
BASELINE_ID = "B1"
# Pin B1 to PR #51 merge commit; tests assert B1_COALITION still matches this revision.
B1_FROZEN_GIT_REV = "da26fa48"
READINESS_SELECTOR_MODULE = "scripts/evidence_capability_selector.py"
NO_EVIDENCE = "no evidence"
PASS_POINTS = 100
FAIL_POINTS = 100
REGRESSION_POINTS = 40
WALL_DIVISOR = 1000
BYTE_DIVISOR = 10000

# Frozen PR #51 coalition. Order is part of the baseline contract.
B1_COALITION: dict[str, tuple[str, ...]] = {
    "atomic": (
        "power-skill",
        "skill-connector-router",
        "casey-operator-execution-kernel",
        "genius-mastery",
        "codemaster",
        "capability-admission",
        "strong-smart-routing-kernel",
        "apex-aspen-grove-bootup",
        "unified-memory-connect",
        "agent-memory-systems",
        "apex-meta-skill-kernel",
        "systematic-debugging",
        "test-driven-development",
        "verification-before-completion",
        "spiral-promotion-gate",
        "progressive-pyramid",
        "computer-user-core",
        "apex-universal-mcp-powerhouse",
        "make-it-heavy",
        "mcp-architect",
    ),
    "compound": (
        "genius-epistemic-engineering",
        "apex-mesh-dispatch",
        "strong-smart-execution-stack",
        "cross-cloud-memory-synthesis",
    ),
    "mega": (
        "apex-genius-mastery",
        "apex-strong-smart-execution-engine",
        "apex-dev-fork-orchestrator",
        "apex-orchestrator-mesh",
        "far-away-party",
        "apex-self-healing-forge",
    ),
}

_LAYER_SOURCES = (
    ("atomic", "registry/skills.json", "skills", "SKILL.md"),
    ("compound", "registry/combo-skills.json", "combo-skills", "COMBO.md"),
    ("mega", "registry/mega-skills.json", "mega-skills", "MEGA.md"),
)
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DESCRIPTION = re.compile(r"(?m)^description:[ \t]*\S[^\r\n]*$")


class SkillRecord:
    """One canonical id at one OMP layer. Packet fields mirror capability packets."""

    def __init__(self, id: str, layer: str, contract_ref: str, contract_path: Path | None = None,
                 cost_bytes: int | None = None, native_description: bool | None = None) -> None:
        self.id = id
        self.layer = layer
        self.contract_ref = contract_ref
        self.contract_path = contract_path
        self.cost_bytes = cost_bytes
        self.native_description = native_description

    def as_packet(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.layer,
            "contract_ref": self.contract_ref,
            "cost_bytes": self.cost_bytes,
        }


class AmbiguousSkill:
    def __init__(self, skill_id: str, layers: list[str]) -> None:
        self.id = skill_id
        self.layers = layers


class Registry:
    def __init__(self, records: list[SkillRecord]) -> None:
        seen: set[tuple[str, str]] = set()
        for record in records:
            key = (record.layer, record.id)
            if key in seen:
                raise ValueError(f"duplicate registry id {record.layer}/{record.id}")
            seen.add(key)
        self.records = tuple(records)

    def resolve(self, skill_id: str, layer: str | None = None) -> SkillRecord | AmbiguousSkill | None:
        matches = [record for record in self.records if record.id == skill_id]
        if layer is not None:
            matches = [record for record in matches if record.layer == layer]
        if not matches:
            return None
        if len(matches) > 1:
            return AmbiguousSkill(skill_id, sorted({record.layer for record in matches}))
        return matches[0]


def b1_coalition() -> dict[str, list[str]]:
    """Return a fresh copy of the frozen B1 coalition."""
    return {layer: list(ids) for layer, ids in B1_COALITION.items()}


def b1_ids() -> list[str]:
    return [skill_id for layer in ("atomic", "compound", "mega") for skill_id in B1_COALITION[layer]]


def parse_omp_selection_from_sync_source(source: str) -> dict[str, list[str]]:
    """Parse OMP_POWER_SELECTION from a sync_runtime_skills.py source string."""
    block_match = re.search(r"OMP_POWER_SELECTION\s*=\s*\{(.*?)\n\}", source, re.S)
    if not block_match:
        raise ValueError("OMP_POWER_SELECTION block not found")
    coalition: dict[str, list[str]] = {}
    for layer in ("atomic", "compound", "mega"):
        layer_match = re.search(rf'"{layer}":\s*\((.*?)\)', block_match.group(1), re.S)
        if not layer_match:
            raise ValueError(f"OMP layer missing: {layer}")
        coalition[layer] = [reject_skill_id(part.strip().strip('"').strip("'"))
                           for part in layer_match.group(1).split(",") if part.strip()]
    return coalition


def family_utility(passes: int, fails: int, regressions: int, wall_time_ms: float, cost_bytes: int) -> float:
    """Higher is better. Byte cost and wall time can only reduce the score."""
    return (
        PASS_POINTS * passes
        - FAIL_POINTS * fails
        - REGRESSION_POINTS * regressions
        - (wall_time_ms / WALL_DIVISOR)
        - (cost_bytes / BYTE_DIVISOR)
    )


def reject_skill_id(value: object) -> str:
    """Refuse path escape, absolute paths, and any non-canonical skill id."""
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise ValueError(f"rejected skill id: {value!r}")
    return value


def has_native_omp_description(document: str) -> bool:
    """Same native-description check the OMP installer uses for atomics."""
    if not document.startswith("---\n"):
        return False
    frontmatter, separator, _ = document[4:].partition("\n---\n")
    return bool(separator and _DESCRIPTION.search(frontmatter))


def assert_append_only(previous: list[dict[str, Any]], updated: list[dict[str, Any]]) -> None:
    """Entries may grow at the end. Existing rows may not change or disappear."""
    if len(updated) < len(previous):
        raise ValueError("ledger is append-only; entries were removed")
    for index, prior in enumerate(previous):
        if updated[index] != prior:
            raise ValueError(f"ledger is append-only; entry {index} changed")


def _require_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"ledger field {field} must be a non-negative integer")
    return value


def _check_artifact(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("required artifact must be a non-empty string")
    if value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"required artifact must be repo-relative: {value!r}")
    if any(part == ".." for part in re.split(r"[\\/]", value)):
        raise ValueError(f"required artifact escapes the repository: {value!r}")
    return value


def derive_task_family(tags: list[str]) -> str:
    folded = {tag.casefold() for tag in tags}
    if folded & frozenset({"macos", "ios", "swift", "swiftui"}):
        return "macos-ios"
    if "python" in folded and "lint" in folded:
        return "python-lint"
    if "python" in folded and (folded & frozenset({"repair", "bugfix", "test"})):
        return "python-repair"
    return "unspecified"


def normalize_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping):
        raise ValueError("task descriptor must be an object")
    intent = task.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("task intent is required")
    tags = task.get("domain_tags", task.get("repo_tags", []))
    artifacts = task.get("required_artifacts", [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) and _SLUG.fullmatch(tag) for tag in tags):
        raise ValueError("domain_tags must be canonical slug strings")
    if not isinstance(artifacts, list):
        raise ValueError("required_artifacts must be a list")
    checked_artifacts = [_check_artifact(item) for item in artifacts]
    mentioned = task.get("mentioned_skill_ids", [])
    if not isinstance(mentioned, list):
        raise ValueError("mentioned_skill_ids must be a list")
    for skill_id in mentioned:
        reject_skill_id(skill_id)
    family = task.get("task_family")
    if family is None:
        family = derive_task_family(tags)
    if not isinstance(family, str) or not _SLUG.fullmatch(family):
        raise ValueError(f"rejected task family: {family!r}")
    task_id = task.get("task_id", task.get("id"))
    if task_id is not None and not isinstance(task_id, str):
        raise ValueError("task id must be a string")
    return {
        "task_id": task_id,
        "intent": intent.strip(),
        "domain_tags": list(tags),
        "required_artifacts": checked_artifacts,
        "task_family": family,
        "mentioned_skill_ids": [reject_skill_id(skill_id) for skill_id in mentioned],
    }


def validate_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, Mapping):
        raise ValueError("ledger entry must be an object")
    entry_id = entry.get("entry_id")
    if not isinstance(entry_id, str) or not _SLUG.fullmatch(entry_id):
        raise ValueError(f"rejected ledger entry_id: {entry_id!r}")
    provenance = entry.get("provenance")
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError(f"ledger entry {entry_id} needs provenance")
    production = entry.get("production_outcome")
    if not isinstance(production, bool):
        raise ValueError(f"ledger entry {entry_id} needs boolean production_outcome")
    label = entry.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"ledger entry {entry_id} needs a label")
    if production is True:
        raise ValueError(f"ledger entry {entry_id} refuses production_outcome true; append fixture seeds only")
    if production is False and "not a production outcome" not in label:
        raise ValueError(f"ledger entry {entry_id} must say it is not a production outcome")
    family = entry.get("task_family")
    if not isinstance(family, str) or not _SLUG.fullmatch(family):
        raise ValueError(f"rejected task family on {entry_id}: {family!r}")
    outcome = entry.get("outcome")
    if outcome not in {"pass", "fail"}:
        raise ValueError(f"ledger entry {entry_id} outcome must be pass or fail")
    for flag in ("harmful", "conflicting"):
        if flag in entry and not isinstance(entry[flag], bool):
            raise ValueError(f"ledger entry {entry_id} field {flag} must be boolean")
    return {
        "entry_id": entry_id,
        "task_family": family,
        "skill_id": reject_skill_id(entry.get("skill_id")),
        "outcome": outcome,
        "regressions": _require_int(entry.get("regressions"), "regressions"),
        "wall_time_ms": _require_int(entry.get("wall_time_ms"), "wall_time_ms"),
        "harmful": bool(entry.get("harmful", False)),
        "conflicting": bool(entry.get("conflicting", False)),
        "production_outcome": production,
        "label": label,
        "provenance": provenance,
    }


def validate_ledger(document: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(document, Mapping):
        raise ValueError("ledger must be a JSON object")
    if document.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise ValueError("ledger schema_version must be 1")
    if document.get("append_only") is not True:
        raise ValueError("ledger must set append_only to true")
    if document.get("production_outcomes") is not False:
        raise ValueError("ledger must set production_outcomes to false")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")
    seen: set[str] = set()
    normalized = []
    for entry in entries:
        checked = validate_entry(entry)
        if checked["entry_id"] in seen:
            raise ValueError(f"duplicate ledger entry_id: {checked['entry_id']}")
        seen.add(checked["entry_id"])
        normalized.append(checked)
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "append_only": True,
        "production_outcomes": False,
        "entries": normalized,
    }


def load_ledger(path: Path) -> dict[str, Any]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    validated = validate_ledger(document)
    # Preserve the caller's row objects for append-only comparisons elsewhere.
    validated["entries_raw"] = document["entries"]
    return validated


def load_task(path: Path, task_id: str | None = None) -> dict[str, Any]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(document, dict) and "intent" in document:
        return document
    tasks = document.get("tasks") if isinstance(document, dict) else None
    if not isinstance(tasks, list):
        raise ValueError("task file must be one task or an object with tasks")
    if not task_id:
        raise ValueError("task file contains multiple tasks; pass task_id")
    matches = [task for task in tasks if task.get("id") == task_id or task.get("task_id") == task_id]
    if len(matches) == 0:
        raise ValueError(f"task id not found: {task_id}")
    if len(matches) > 1:
        raise ValueError(f"duplicate task id: {task_id}")
    return matches[0]


def _within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def load_registry(root: Path) -> Registry:
    """Index canonical ids. Directory names come from the id, never from a raw path."""
    root = Path(root)
    records: list[SkillRecord] = []
    for layer, relative, directory_name, document_name in _LAYER_SOURCES:
        path = root / relative
        if not path.is_file():
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        entries = document.get("entries") if isinstance(document, dict) else None
        if not isinstance(entries, list):
            continue
        layer_root = root / directory_name
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            skill_id = entry.get("id")
            if not isinstance(skill_id, str) or not _SLUG.fullmatch(skill_id):
                continue
            source = layer_root / skill_id
            contract = source / document_name
            if not contract.is_file() or not _within(layer_root, source):
                continue
            records.append(SkillRecord(
                id=skill_id,
                layer=layer,
                contract_ref=f"{directory_name}/{skill_id}/{document_name}",
                contract_path=contract,
            ))
    return Registry(records)


def materialize(registry: Registry, skill_ids: set[str]) -> Registry:
    """Fill cost and native-description fields for the ids this decision can see."""
    updated: list[SkillRecord] = []
    for record in registry.records:
        if record.id not in skill_ids:
            updated.append(record)
            continue
        cost = record.cost_bytes
        native = record.native_description
        if record.contract_path is not None and cost is None:
            cost = record.contract_path.stat().st_size
        if record.layer == "atomic":
            if native is None and record.contract_path is not None:
                text = record.contract_path.read_text(encoding="utf-8")
                native = has_native_omp_description(text)
        elif native is None:
            native = True
        updated.append(SkillRecord(
            id=record.id,
            layer=record.layer,
            contract_ref=record.contract_ref,
            contract_path=record.contract_path,
            cost_bytes=cost,
            native_description=native,
        ))
    return Registry(updated)


def _require_b1(registry: Registry) -> list[SkillRecord]:
    chosen: list[SkillRecord] = []
    for layer, skill_ids in B1_COALITION.items():
        for skill_id in skill_ids:
            found = registry.resolve(skill_id, layer)
            if not isinstance(found, SkillRecord):
                raise ValueError(f"B1 skill is not an unambiguous registry id: {layer}/{skill_id}")
            if found.cost_bytes is None or (found.layer == "atomic" and found.native_description is None):
                raise ValueError(f"B1 skill was not materialized: {skill_id}")
            if found.layer == "atomic" and not found.native_description:
                raise ValueError(f"B1 atomic lacks a native description: {skill_id}")
            chosen.append(found)
    return chosen


def _coalition_from(records: list[SkillRecord]) -> dict[str, list[str]]:
    coalition = {layer: [] for layer in B1_COALITION}
    for record in records:
        coalition[record.layer].append(record.id)
    return coalition


def _flatten(coalition: Mapping[str, list[str]]) -> list[str]:
    return [skill_id for layer in ("atomic", "compound", "mega") for skill_id in coalition[layer]]


def select_coalition(task: Mapping[str, Any], ledger: Mapping[str, Any], registry: Registry) -> dict[str, Any]:
    """Return a coalition for one task. No profile writes and no ledger writes."""
    normalized = normalize_task(task)
    checked = validate_ledger(ledger)
    baseline = _require_b1(registry)
    family = normalized["task_family"]
    refused: list[dict[str, str]] = []
    usable: list[tuple[dict[str, Any], SkillRecord]] = []
    for entry in checked["entries"]:
        if entry["task_family"] != family:
            continue
        found = registry.resolve(entry["skill_id"])
        if found is None:
            refused.append({"id": entry["skill_id"], "reason": "not_in_registry"})
            continue
        if isinstance(found, AmbiguousSkill):
            refused.append({"id": entry["skill_id"], "reason": "ambiguous_registry_id"})
            continue
        if found.layer == "atomic" and not found.native_description:
            refused.append({"id": entry["skill_id"], "reason": "invalid_native_description"})
            continue
        if found.cost_bytes is None:
            raise ValueError(f"skill was not materialized: {found.id}")
        usable.append((entry, found))

    b1_keys = {(record.layer, record.id) for record in baseline}
    if not usable:
        coalition = _coalition_from(baseline)
        return _receipt(normalized, coalition, decision=NO_EVIDENCE, added=[], excluded=[],
                        withheld=[], refused=refused, scores=[], rows_used=0, selected=baseline)

    grouped: dict[tuple[str, str], list[tuple[dict[str, Any], SkillRecord]]] = {}
    for entry, record in usable:
        grouped.setdefault((record.layer, record.id), []).append((entry, record))

    scores: list[dict[str, Any]] = []
    harmful_keys: set[tuple[str, str]] = set()
    for key, rows in grouped.items():
        record = rows[0][1]
        passes = sum(1 for entry, _ in rows if entry["outcome"] == "pass")
        fails = sum(1 for entry, _ in rows if entry["outcome"] == "fail")
        regressions = sum(entry["regressions"] for entry, _ in rows)
        wall = sum(entry["wall_time_ms"] for entry, _ in rows) / len(rows)
        harmful = any(entry["harmful"] for entry, _ in rows)
        conflicting = any(entry["conflicting"] for entry, _ in rows)
        utility = family_utility(passes, fails, regressions, wall, record.cost_bytes or 0)
        positive = (not harmful) and (not conflicting) and passes > fails and utility > 0
        if harmful or conflicting:
            harmful_keys.add(key)
        scores.append({
            "id": record.id,
            "layer": record.layer,
            "passes": passes,
            "fails": fails,
            "regressions": regressions,
            "wall_time_ms": wall,
            "cost_bytes": record.cost_bytes,
            "utility": round(utility, 4),
            "harmful": harmful,
            "conflicting": conflicting,
            "positive_benefit": positive,
            "admitted": positive and key not in b1_keys,
            "in_baseline": key in b1_keys,
        })

    excluded: list[dict[str, str]] = []
    selected: list[SkillRecord] = []
    for record in baseline:
        key = (record.layer, record.id)
        if key in harmful_keys:
            reason = "harmful" if any(item["id"] == record.id and item["harmful"] for item in scores) else "conflicting"
            excluded.append({"id": record.id, "layer": record.layer, "reason": reason})
            continue
        selected.append(record)

    withheld: list[dict[str, Any]] = []
    additions: list[tuple[float, int, SkillRecord]] = []
    for item in scores:
        key = (item["layer"], item["id"])
        if key in b1_keys:
            continue
        record = registry.resolve(item["id"], item["layer"])
        if not isinstance(record, SkillRecord):
            continue
        if not item["positive_benefit"]:
            reason = "harmful" if item["harmful"] else "conflicting" if item["conflicting"] else "no positive benefit"
            withheld.append({
                "id": item["id"],
                "layer": item["layer"],
                "reason": reason,
                "utility": item["utility"],
            })
            continue
        additions.append((item["utility"], record.cost_bytes or 0, record))
    additions.sort(key=lambda item: (-item[0], item[1], item[2].id))
    added = []
    for _, _, record in additions:
        selected.append(record)
        added.append(record.id)
    withheld.sort(key=lambda item: (item["layer"], item["id"]))
    scores.sort(key=lambda item: (item["layer"], item["id"]))
    coalition = _coalition_from(selected)
    return _receipt(normalized, coalition, decision="evidence", added=added, excluded=excluded,
                    withheld=withheld, refused=refused, scores=scores, rows_used=len(usable),
                    selected=selected)


def _receipt(task: dict[str, Any], coalition: dict[str, list[str]], *, decision: str,
             added: list[str], excluded: list[dict[str, str]], withheld: list[dict[str, Any]],
             refused: list[dict[str, str]], scores: list[dict[str, Any]], rows_used: int,
             selected: list[SkillRecord]) -> dict[str, Any]:
    cost = sum(record.cost_bytes or 0 for record in selected)
    packets = [record.as_packet() for record in selected]
    return {
        "schema_version": SELECTOR_SCHEMA_VERSION,
        "selector_id": SELECTOR_ID,
        "baseline_id": BASELINE_ID,
        "decision": decision,
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "intent": task["intent"],
        "domain_tags": task["domain_tags"],
        "required_artifacts": task["required_artifacts"],
        "coalition": coalition,
        "skill_ids": _flatten(coalition),
        "added": added,
        "excluded": excluded,
        "withheld": withheld,
        "refused": refused,
        "scores": scores,
        "evidence_rows_used": rows_used,
        "cost_bytes": cost,
        "capability_packets": packets,
        "profile_writes": 0,
    }


def select_from_documents(root: Path, task: Mapping[str, Any], ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Load this checkout's registry, then run the pure selection function."""
    checked = validate_ledger(ledger)
    normalized = normalize_task(task)
    needed = set(b1_ids())
    needed.update(entry["skill_id"] for entry in checked["entries"])
    needed.update(normalized["mentioned_skill_ids"])
    registry = materialize(load_registry(root), needed)
    return select_coalition(task, ledger, registry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview an evidence-aware OMP coalition. Writes nothing.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task-json", type=Path, required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    ledger_path = args.ledger or (root / "evidence" / "skill-selection" / "ledger.json")
    task = load_task(args.task_json, args.task_id)
    ledger = load_ledger(ledger_path)
    receipt = select_from_documents(root, task, ledger)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
