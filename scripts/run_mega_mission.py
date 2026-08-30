#!/usr/bin/env python3
"""Run a safe, contract-backed Mega Skill mission locally.

The runner proves repository admission, route resolution, firewall enforcement,
durable artifact emission, and a hash-linked receipt. It never performs external
mutation, sends data, files anything, merges code, or executes unknown programs.
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_artifact(policy: dict, path: Path, content: str) -> None:
    guard(policy, "write_run_artifacts")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--mega-id", default="apex-autonomous-agent-foundry")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    started = datetime.now(timezone.utc).isoformat()
    run_dir = (args.output_dir or root / "runs" / f"foundry-run-{int(time.time())}").resolve()

    try:
        policy = load_policy(root, args.mega_id)
        mega_data = load_json(root / "registry" / "mega-skills.json")
        mega = next(item for item in mega_data["entries"] if item["id"] == args.mega_id)
        combos = load_json(root / "registry" / "combo-skills.json")["entries"]
        combo_by_id = {item["id"]: item for item in combos}
        route_ids = mega["required_combos"] + mega["conditional_combos"]
        route = [combo_by_id[combo_id] for combo_id in route_ids if combo_id in combo_by_id]
        if len(route) != len(route_ids):
            missing = sorted(set(route_ids) - set(combo_by_id))
            raise ValueError(f"unresolved route Combo Skills: {missing}")
        foundry = combo_by_id.get("autonomous-agent-foundry")
        if foundry is None:
            raise ValueError("autonomous-agent-foundry Combo Skill is missing")
        member_ids = [member["id"] for member in foundry["members"] if member["kind"] == "skill"]
        missing_entrypoints = [
            skill_id for skill_id in member_ids
            if not (root / "skills" / skill_id / "skill.py").is_file()
        ]
        if missing_entrypoints:
            raise ValueError(f"missing member entrypoints: {missing_entrypoints}")

        validator = root / "scripts" / "validate_hierarchy.py"
        validation = subprocess.run(
            [sys.executable, str(validator)], cwd=root, text=True, capture_output=True, check=False
        )
        if validation.returncode != 0:
            raise RuntimeError(f"hierarchy validation failed: {validation.stdout}{validation.stderr}")

        phase_receipts = [
            {"phase": "admission", "status": "VERIFIED", "evidence": "firewall and registry contracts resolved"},
            {"phase": "route", "status": "VERIFIED", "evidence": f"{len(route)} registered Combo Skills resolved"},
            {"phase": "member-preflight", "status": "VERIFIED", "evidence": f"{len(member_ids)} member entrypoints present"},
            {"phase": "hierarchy-validation", "status": "VERIFIED", "evidence": validation.stdout.strip()},
            {"phase": "artifact-emission", "status": "VERIFIED", "evidence": "local run artifacts only"},
        ]
        common = f"Mission ID: FOUNDRY-RUN-{int(time.time())}\nStarted: {started}\nFirewall: read_only / human_control required\n"
        artifacts = {
            "MISSION.md": "# Mission Contract\n\n" + common + "Objective: exercise the contract-backed agent-foundry route without external side effects.\n",
            "ROADMAP.md": "# Mission Roadmap\n\n" + common + "Phases: admission, route resolution, member preflight, hierarchy validation, artifact emission.\n",
            "CONTEXT.md": "# Mission Context\n\n" + common + f"Repository root: {root}\nMega: {args.mega_id}\n",
            "EVIDENCE.md": "# Evidence Register\n\n" + json.dumps(phase_receipts, indent=2) + "\n",
            "HANDOFF.md": "# Durable Handoff\n\nStatus: COMPLETED\nResumption point: none; receipt is complete.\n",
            "AGENT_ARCHITECTURE_SPEC.md": "# Architecture Contract\n\nStatus: VERIFIED\nEvidence: registered member contracts and entrypoints resolved.\n",
            "AGENT_MEMORY_CONFIGURATION.json": json.dumps({"status": "VERIFIED", "evidence": "member contract resolved", "external_write": False}, indent=2) + "\n",
            "AGENT_EVALUATION_REPORT.json": json.dumps({"status": "NOT_PERFORMED", "reason": "runner proves orchestration contracts, not model accuracy"}, indent=2) + "\n",
            "AGENT_FOUNDRY_RELEASE_PACKET.md": "# Release Packet\n\nStatus: CONTRACT_VERIFIED\nNo production certification is claimed.\n",
        }
        for name, content in artifacts.items():
            write_artifact(policy, run_dir / name, content)

        output_manifest = []
        for path in sorted(run_dir.iterdir()):
            if path.is_file():
                output_manifest.append({"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size})
        receipt = {
            "schema_version": 1, "mission_id": f"FOUNDRY-RUN-{int(time.time())}",
            "mega_id": args.mega_id, "status": "COMPLETED", "firewall_mode": policy["mode"],
            "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
            "phase_receipts": phase_receipts, "output_manifest": output_manifest,
        }
        write_artifact(policy, run_dir / "RUN_RECEIPT.json", json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"status": receipt["status"], "run_dir": str(run_dir), "artifacts": len(output_manifest) + 1}, indent=2))
        return 0
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"MISSION_BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
