#!/usr/bin/env python3
"""Runtime-amplified wrapper for the control-plane deep-work family.

This wrapper keeps the existing deep_work_stage implementation as the stage owner,
then proves that the requested cognition/runtime amplifiers are resolvable before a
control-plane run can report READY. It performs no network access, deployment,
merge, credential read, or external mutation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import deep_work_stage as base

PROFILE_ID = "control-plane-max-runtime-v1"

REQUIRED_MEGAS = (
    "apex-always-on-core",
    "apex-adaptive-operations",
    "apex-sovereign-runtime",
    "far-away-party",
    "apex-genius-mastery",
)

REQUIRED_COMBOS = (
    "long-horizon-core",
    "capability-readiness",
    "pipeline-orchestration",
    "genius-epistemic-engineering",
    "genius-entity-forge",
    "epistemic-verification-chain",
)

REQUIRED_ATOMICS = (
    "max-token-saver",
    "power-skill",
    "make-it-heavy",
    "epistemic-gate",
    "casey-operator-execution-kernel",
)

REQUIRED_NOTION_ENTRIES = (
    "notion.token-saver",
    "notion.always-on-core",
    "notion.power-skill",
    "notion.epistemic-contract",
    "notion.pipelines",
)

GENIUS_LINEAGE = (
    "Genius-Mastery",
    "Genius-Code",
    "Genius-Verification",
)


def _skill_exists(root: Path, skill_id: str) -> bool:
    return (root / "skills" / skill_id / "SKILL.md").is_file()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def _notion_bridge_state(root: Path) -> dict[str, Any]:
    path = root / "integrations" / "notion-skill-bridge.json"
    data = _read_json(path)
    ids = {
        str(item.get("id"))
        for item in (data or {}).get("entries", [])
        if isinstance(item, dict) and item.get("id")
    }
    missing = [entry for entry in REQUIRED_NOTION_ENTRIES if entry not in ids]
    return {
        "path": path.relative_to(root).as_posix(),
        "present": data is not None,
        "required_entries": list(REQUIRED_NOTION_ENTRIES),
        "missing_entries": missing,
        "status": "READY" if data is not None and not missing else "GAP",
        "claim_boundary": "projection pointers only; live Notion skill use requires provider readback",
    }


def _genius_bridge_state(root: Path) -> dict[str, Any]:
    path = root / "integrations" / "genius-mastery-bridge.json"
    data = _read_json(path)
    return {
        "path": path.relative_to(root).as_posix(),
        "present": data is not None,
        "lineage": list(GENIUS_LINEAGE),
        "status": "READY" if data is not None else "GAP",
        "claim_boundary": "Mega-Skills bridge plus Genius family identity; external runtime proof remains receipt-bound",
    }


def inspect_profile(root: Path) -> dict[str, Any]:
    mega_registry = set(base.load_registry_ids(root, "mega-skills.json"))
    combo_registry = set(base.load_registry_ids(root, "combo-skills.json"))
    atomic_registry = set(base.load_registry_ids(root, "skills.json"))

    mega_checks = []
    for item in REQUIRED_MEGAS:
        present = base.mega_exists(root, item)
        registered = item in mega_registry or not mega_registry
        mega_checks.append(
            {
                "id": item,
                "present": present,
                "registered": registered,
                "status": "READY" if present and registered else "GAP",
            }
        )

    combo_checks = []
    for item in REQUIRED_COMBOS:
        present = base.combo_exists(root, item)
        registered = item in combo_registry or not combo_registry
        combo_checks.append(
            {
                "id": item,
                "present": present,
                "registered": registered,
                "status": "READY" if present and registered else "GAP",
            }
        )

    atomic_checks = []
    for item in REQUIRED_ATOMICS:
        present = _skill_exists(root, item)
        registered = item in atomic_registry or not atomic_registry
        atomic_checks.append(
            {
                "id": item,
                "present": present,
                "registered": registered,
                "status": "READY" if present and registered else "GAP",
            }
        )

    epistemic_path = root / "docs" / "EPISTEMIC_CONTRACT.md"
    epistemic = {
        "path": epistemic_path.relative_to(root).as_posix(),
        "present": epistemic_path.is_file(),
        "proof_floor": "L2 behavior/readback for mutation claims; higher tiers remain claim-specific",
        "status": "READY" if epistemic_path.is_file() else "GAP",
    }
    notion = _notion_bridge_state(root)
    genius = _genius_bridge_state(root)

    sections = mega_checks + combo_checks + atomic_checks + [epistemic, notion, genius]
    gaps = []
    for section in sections:
        if section.get("status") != "READY":
            gaps.append(section.get("id") or section.get("path") or "unknown")

    return {
        "schema_version": 1,
        "profile_id": PROFILE_ID,
        "status": "READY" if not gaps else "DEGRADED",
        "gaps": gaps,
        "mega_roots": mega_checks,
        "required_combos": combo_checks,
        "atomic_amplifiers": atomic_checks,
        "epistemic_contract": epistemic,
        "notion_skill_bridge": notion,
        "genius_lineage": genius,
        "runtime_law": [
            "REUSE",
            "CONTINUE",
            "HYDRATE",
            "COMPOSE",
            "EXECUTE",
            "TEST",
            "VERIFY",
            "PRESERVE",
            "CONTINUE",
        ],
        "truth_law": "GENERATED != EXECUTED != VERIFIED; no readback means no verified mutation",
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _augment_stage(root: Path, args: argparse.Namespace, profile: dict[str, Any]) -> list[Path]:
    out = base.workdir(root, args.pipeline_id)
    produced: list[Path] = []

    if args.stage == "inception":
        path = out / "inception.json"
        data = _read_json(path) or {}
        data["runtime_amplification"] = profile
        _write_json(path, data)
        activation = out / "RUNTIME_ACTIVATION.json"
        _write_json(activation, profile)
        produced.append(activation)

        mission = out / "MISSION.md"
        with mission.open("a", encoding="utf-8") as handle:
            handle.write(
                "\n## Runtime amplification\n\n"
                f"Profile: `{PROFILE_ID}`\n\n"
                "Token economy: `max-token-saver`\n"
                "Execution density: `power-skill` + `make-it-heavy`\n"
                "Epistemology: `docs/EPISTEMIC_CONTRACT.md` + `epistemic-gate`\n"
                "Genius lineage: `Genius-Mastery -> Genius-Code + Genius-Verification`\n"
                "Notion: route through live skill projections; repository pointers alone are not provider readback.\n"
            )

    elif args.stage == "readiness":
        path = out / "READINESS.json"
        data = _read_json(path) or {}
        data["runtime_amplification"] = profile
        if profile["status"] != "READY":
            data["status"] = "DEGRADED"
            merged = list(dict.fromkeys(list(data.get("gaps", [])) + list(profile["gaps"])))
            data["gaps"] = merged
        _write_json(path, data)

    elif args.stage == "design":
        path = out / "ROUTE.json"
        data = _read_json(path) or {}
        data["runtime_profile"] = PROFILE_ID
        data["required_combos"] = list(REQUIRED_COMBOS)
        data["atomic_amplifiers"] = list(REQUIRED_ATOMICS)
        data["genius_lineage"] = list(GENIUS_LINEAGE)
        data["notion_skill_entries"] = list(REQUIRED_NOTION_ENTRIES)
        _write_json(path, data)

    elif args.stage == "verify":
        path = out / "VERIFY.json"
        data = _read_json(path) or {}
        data["runtime_amplification"] = {
            "profile_id": PROFILE_ID,
            "status": profile["status"],
            "gaps": profile["gaps"],
        }
        if profile["status"] != "READY":
            data["status"] = "PARTIAL"
        _write_json(path, data)
        evidence = out / "EVIDENCE.md"
        with evidence.open("a", encoding="utf-8") as handle:
            handle.write("\n## Runtime amplification receipt\n\n")
            handle.write("```json\n" + json.dumps(profile, indent=2, sort_keys=True) + "\n```\n")

    return produced


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--pipeline-id", default="control-plane")
    parser.add_argument("--family", default="control-plane")
    parser.add_argument("--stage", choices=sorted(base.STAGES))
    args = parser.parse_args(argv)

    if args.family != "control-plane":
        raise SystemExit("runtime_amplified_stage.py is reserved for the control-plane family")
    if not args.stage:
        parser.error("--stage is required")

    root = args.root.resolve()
    profile = inspect_profile(root)
    produced = base.STAGES[args.stage](root, args)
    produced.extend(_augment_stage(root, args, profile))

    print(
        json.dumps(
            {
                "status": "COMPLETED" if profile["status"] == "READY" else "DEGRADED",
                "pipeline_id": args.pipeline_id,
                "stage": args.stage,
                "runtime_profile": PROFILE_ID,
                "runtime_readiness": profile["status"],
                "gaps": profile["gaps"],
                "artifacts": [
                    path.relative_to(root).as_posix() if root in path.parents else str(path)
                    for path in produced
                ],
            },
            indent=2,
        )
    )
    return 0 if profile["status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
