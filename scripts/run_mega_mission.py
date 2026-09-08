#!/usr/bin/env python3
"""Run a support-only Mega Skill contract preflight locally.

This runner validates route contracts and emits local evidence. It does NOT perform
domain mission execution and therefore MUST NOT report mission completion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from firewall import guard, load_policy


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_artifact(policy: dict, path: Path, content: str) -> None:
    guard(policy, "write_run_artifacts")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(root: Path, path: Path) -> dict[str, object]:
    relative = path.relative_to(root).as_posix()
    return {"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size}


def resolve_route(root: Path, mega: dict, combos: list[dict], include_conditional: bool) -> tuple[list[dict], list[str]]:
    combo_by_id = {item["id"]: item for item in combos}
    required = list(mega["required_combos"])
    conditional = list(mega["conditional_combos"]) if include_conditional else []
    route_ids = required + conditional
    missing = sorted(set(route_ids) - set(combo_by_id))
    if missing:
        raise ValueError(f"unresolved route Combo Skills: {missing}")
    route = [combo_by_id[combo_id] for combo_id in route_ids]
    member_ids: list[str] = []
    for combo in route:
        document = root / combo["entrypoint"]
        if not document.is_file():
            raise ValueError(f"missing Combo entrypoint: {combo['id']}")
        for member in combo["members"]:
            if member["kind"] != "skill":
                continue
            skill_id = member["id"]
            if skill_id not in member_ids:
                member_ids.append(skill_id)
            skill_dir = root / "skills" / skill_id
            if not (skill_dir / "SKILL.md").is_file() or not (skill_dir / "skill.py").is_file():
                raise ValueError(f"missing member entrypoint: {skill_id}")
    return route, member_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--mega-id", default="apex-autonomous-agent-foundry")
    parser.add_argument("--include-conditional", action="store_true", help="include all declared conditional Combos for this contract exercise")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    started = datetime.now(timezone.utc).isoformat()
    mission_id = f"FOUNDRY-RUN-{int(time.time())}"
    run_dir = (args.output_dir or root / "runs" / mission_id.lower()).resolve()
    policy: dict | None = None

    try:
        # Policy loading is the bootstrap read; all subsequent repository reads are gated.
        policy = load_policy(root, args.mega_id)
        guard(policy, "read_repository")
        mega_data = load_json(root / "registry" / "mega-skills.json")
        mega = next(item for item in mega_data["entries"] if item["id"] == args.mega_id)
        combos_data = load_json(root / "registry" / "combo-skills.json")
        route, member_ids = resolve_route(root, mega, combos_data["entries"], args.include_conditional)

        if run_dir.exists() and any(run_dir.iterdir()):
            raise ValueError(f"output directory is not empty: {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)

        validator = root / "scripts" / "validate_hierarchy.py"
        guard(policy, "run_local_tests")
        validation = subprocess.run(
            [sys.executable, str(validator)], cwd=root, text=True, capture_output=True, check=False
        )
        if validation.returncode != 0:
            raise RuntimeError(f"hierarchy validation failed: {validation.stdout}{validation.stderr}")

        input_paths = [
            root / "registry" / "mega-skills.json",
            root / "registry" / "combo-skills.json",
            root / "registry" / "skills.json",
            root / "registry" / "external-skills.json",
            root / "scripts" / "firewall.py",
            root / "scripts" / "validate_hierarchy.py",
        ]
        input_paths += [root / combo["entrypoint"] for combo in route]
        input_paths += [root / "skills" / skill_id / name for skill_id in member_ids for name in ("SKILL.md", "skill.py")]
        input_manifest = [input_record(root, path) for path in sorted(set(input_paths))]

        phase_receipts = [
            {"phase": "admission", "status": "VERIFIED", "evidence": "registry firewall contract resolved and validated"},
            {"phase": "route", "status": "VERIFIED", "evidence": f"{len(route)} required/selected Combo contracts resolved; conditional_included={args.include_conditional}"},
            {"phase": "member-preflight", "status": "VERIFIED", "evidence": f"{len(member_ids)} unique member entrypoints present; none executed"},
            {"phase": "hierarchy-validation", "status": "VERIFIED", "evidence": validation.stdout.strip()},
            {"phase": "artifact-emission", "status": "VERIFIED", "evidence": "local run artifacts only"},
        ]
        common = f"Mission ID: {mission_id}\nStarted: {started}\nFirewall: read_only / human_control required\n"
        mission_output_file = mega.get("mission_output", "MISSION_RESULT.md")
        artifacts = {
            "INPUT_MANIFEST.json": json.dumps({"schema_version": 1, "inputs": input_manifest}, indent=2) + "\n",
            "MISSION.md": "# Mission Contract\n\n" + common + f"Mega: {mega['display_name']} ({args.mega_id})\nObjective: exercise the selected contract-backed Mega route without external side effects.\n",
            "ROADMAP.md": "# Mission Roadmap\n\n" + common + f"Phases: admission, route resolution, member preflight, hierarchy validation, artifact emission.\nRoute: {', '.join(c['id'] for c in route)}\n",
            "CONTEXT.md": "# Mission Context\n\n" + common + f"Repository root: {root}\nMega: {args.mega_id}\nAdds: {mega.get('adds', '')}\n",
            "EVIDENCE.md": "# Evidence Register\n\n" + json.dumps(phase_receipts, indent=2) + "\n",
            "HANDOFF.md": "# Durable Handoff\n\nStatus: SUPPORT_VERIFIED_NOT_MISSION_COMPLETE\nMission state changed: false\nThis preflight cannot terminate an execution run.\n",
            "ROUTE.json": json.dumps({"mega_id": args.mega_id, "required_combos": mega["required_combos"], "selected_combos": [c["id"] for c in route], "member_ids": member_ids}, indent=2) + "\n",
            "FAILURE_RECORD.json": json.dumps({"schema_version": 1, "status": "NONE", "failures": []}, indent=2) + "\n",
            mission_output_file: f"# {mega['display_name']} Deliverable\n\nStatus: SUPPORT_VERIFIED_NOT_MISSION_COMPLETE\nMission ID: {mission_id}\nMission state changed: false\nEvidence: member contracts resolved and verified; no domain execution occurred.\n",
        }
        if args.mega_id == "apex-autonomous-agent-foundry":
            artifacts["AGENT_ARCHITECTURE_SPEC.md"] = "# Architecture Contract\n\nStatus: CONTRACT_VERIFIED\nEvidence: registered Combo/member contracts and entrypoints resolved.\n"
            artifacts["AGENT_MEMORY_CONFIGURATION.json"] = json.dumps({"status": "CONTRACT_VERIFIED", "evidence": "member contract resolved", "external_write": False}, indent=2) + "\n"
            artifacts["AGENT_EVALUATION_REPORT.json"] = json.dumps({"status": "NOT_PERFORMED", "reason": "runner proves orchestration contracts, not model accuracy"}, indent=2) + "\n"
            artifacts["AGENT_FOUNDRY_RELEASE_PACKET.md"] = "# Release Packet\n\nStatus: CONTRACT_VERIFIED\nNo production certification is claimed.\n"
        for name, content in artifacts.items():
            write_artifact(policy, run_dir / name, content)

        output_manifest = [
            {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in sorted(run_dir.iterdir()) if path.is_file()
        ]
        receipt = {
            "schema_version": 1,
            "mission_id": mission_id,
            "mega_id": args.mega_id,
            "status": "SUPPORT_VERIFIED",
            "mission_state_changed": False,
            "completion_eligible": False,
            "support_only": True,
            "firewall_mode": policy["mode"],
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "input_manifest_sha256": hashlib.sha256(canonical_json(input_manifest)).hexdigest(),
            "phase_receipts": phase_receipts,
            "output_manifest": output_manifest,
            "output_manifest_sha256": hashlib.sha256(canonical_json(output_manifest)).hexdigest(),
        }
        guard(policy, "emit_receipt")
        write_artifact(policy, run_dir / "RUN_RECEIPT.json", json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"status": receipt["status"], "mission_state_changed": False, "completion_eligible": False, "run_dir": str(run_dir), "artifacts": len(output_manifest) + 1}, indent=2))
        return 0
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        if policy is not None and run_dir.exists() and not any(run_dir.iterdir()):
            write_artifact(policy, run_dir / "FAILURE_RECORD.json", json.dumps({"schema_version": 1, "status": "BLOCKED", "error": str(exc)}, indent=2) + "\n")
        print(f"MISSION_BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
