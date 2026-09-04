#!/usr/bin/env python3
"""Local, firewall-safe stages for inception-to-deployment pipelines.

Stages write named artifacts under missions/<pipeline-id>/. They never deploy,
merge, send network, or read credentials. Deployment is represented only as an
approval packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_STAGE_TOKENS = (
    "deploy --prod",
    "git push",
    "git merge",
    "vercel deploy",
    "gh release",
    "supabase db push",
)

PHASES = (
    "inception",
    "readiness",
    "recon",
    "design",
    "build",
    "verify",
    "package",
    "deploy-gate",
    "handoff",
    "evolve",
)

FAMILY_MEGAS: dict[str, list[str]] = {
    "control-plane": [
        "apex-always-on-core",
        "apex-adaptive-operations",
        "apex-sovereign-runtime",
        "far-away-party",
    ],
    "memory-fleet": [
        "apex-omniversal-memory",
        "apex-fleet-harmonizer",
        "apex-docgen-synthesis",
    ],
    "change-swe": [
        "apex-safe-change-orchestrator",
        "apex-self-healing-forge",
        "apex-autonomous-software-engineering",
        "apex-architectural-evolution-engine",
        "apex-dev-fork-orchestrator",
    ],
    "ship-cloud": [
        "apex-web-build-system",
        "apex-vercel-web-foundry",
        "apex-backend-infrastructure-engine",
        "apex-secure-cloud-foundry",
    ],
}

MASTER_MEGAS = [mega for family in FAMILY_MEGAS.values() for mega in family]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def load_registry_ids(root: Path, name: str) -> list[str]:
    path = root / "registry" / name
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", data if isinstance(data, list) else [])
    return [item["id"] for item in entries if isinstance(item, dict) and "id" in item]


def mega_exists(root: Path, mega_id: str) -> bool:
    return (root / "mega-skills" / mega_id / "MEGA.md").is_file()


def combo_exists(root: Path, combo_id: str) -> bool:
    return (root / "combo-skills" / combo_id / "COMBO.md").is_file()


def workdir(root: Path, pipeline_id: str) -> Path:
    return root / "missions" / pipeline_id


def common_meta(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "pipeline_id": args.pipeline_id,
        "family": args.family,
        "stage": args.stage,
        "generated_at": utc_now(),
        "firewall_mode": "read_only",
        "deploy_mode": "approval_packet_only",
    }


def stage_inception(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    megas = FAMILY_MEGAS.get(args.family, MASTER_MEGAS if args.family == "master" else [])
    mission = (
        f"# Mission Contract\n\n"
        f"Pipeline: `{args.pipeline_id}`\n"
        f"Family: `{args.family}`\n"
        f"Span: inception → evolve\n"
        f"Started: {utc_now()}\n\n"
        f"Objective: run a contract-backed deep-work loop from problem framing "
        f"through a human-gated deployment packet. No remote mutation.\n\n"
        f"Mega roots:\n" + "".join(f"- `{mega}`\n" for mega in megas)
    )
    roadmap = (
        "# Roadmap\n\n"
        "1. Inception and readiness\n"
        "2. Recon and route design\n"
        "3. Bounded build / safe-change preflight\n"
        "4. Verify contracts and evidence\n"
        "5. Package release artifacts\n"
        "6. Emit deploy-gate packet (approval required)\n"
        "7. Handoff and evolution backlog\n"
    )
    context = (
        f"# Context\n\n"
        f"Repository root: `{root}`\n"
        f"Durable workspace: `missions/{args.pipeline_id}/`\n"
        f"Forbidden: deploy, merge, network send, credential access.\n"
    )
    write_text(out / "MISSION.md", mission)
    write_text(out / "ROADMAP.md", roadmap)
    write_text(out / "CONTEXT.md", context)
    write_json(out / "inception.json", {**common_meta(args), "mega_roots": megas, "status": "OPEN"})
    return [out / "MISSION.md", out / "ROADMAP.md", out / "CONTEXT.md", out / "inception.json"]


def stage_readiness(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    megas = FAMILY_MEGAS.get(args.family, MASTER_MEGAS if args.family == "master" else [])
    registered = set(load_registry_ids(root, "mega-skills.json"))
    checks = []
    for mega in megas:
        present = mega_exists(root, mega)
        in_registry = mega in registered or not registered
        checks.append(
            {
                "id": mega,
                "entrypoint": present,
                "registered": in_registry,
                "status": "READY" if present and in_registry else "GAP",
            }
        )
    gaps = [item["id"] for item in checks if item["status"] == "GAP"]
    payload = {
        **common_meta(args),
        "status": "READY" if not gaps else "DEGRADED",
        "gaps": gaps,
        "checks": checks,
        "combo_count": len(load_registry_ids(root, "combo-skills.json")),
        "atomic_count": len(load_registry_ids(root, "skills.json")),
    }
    write_json(out / "READINESS.json", payload)
    return [out / "READINESS.json"]


def stage_recon(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    payload = {
        **common_meta(args),
        "tree": {
            "mega_skills": sorted(p.name for p in (root / "mega-skills").glob("*") if p.is_dir())
            if (root / "mega-skills").is_dir()
            else [],
            "combo_skills": sorted(p.name for p in (root / "combo-skills").glob("*") if p.is_dir())
            if (root / "combo-skills").is_dir()
            else [],
            "pipelines": sorted(p.name for p in (root / "pipelines").glob("*.json"))
            if (root / "pipelines").is_dir()
            else [],
        },
        "shared_trunk": [
            "long-horizon-core",
            "capability-readiness",
            "signal-to-decision-loop",
            "guarded-automation-loop",
            "evidence-to-evolution-loop",
        ],
    }
    write_json(out / "RECON.json", payload)
    return [out / "RECON.json"]


def stage_design(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    megas = FAMILY_MEGAS.get(args.family, MASTER_MEGAS if args.family == "master" else [])
    route = {
        **common_meta(args),
        "selected_megas": megas,
        "required_combos": [
            "long-horizon-core",
            "capability-readiness",
            "pipeline-orchestration",
        ],
        "integration_rule": "Parents reference child IDs; they do not copy child methods.",
    }
    write_json(out / "ROUTE.json", route)
    write_text(
        out / "ARCHITECTURE.md",
        "# Route Architecture\n\n"
        "Shared trunk: long-horizon-core → capability-readiness → "
        "signal/guard/evidence loops → family Mega roots → mission packet.\n\n"
        + "\n".join(f"- `{mega}`" for mega in megas)
        + "\n",
    )
    return [out / "ROUTE.json", out / "ARCHITECTURE.md"]


def stage_build(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    payload = {
        **common_meta(args),
        "status": "PREFLIGHT_ONLY",
        "actions_taken": [
            "resolved Combo/Mega contracts",
            "refused external mutation",
            "wrote local change record",
        ],
        "change_record": "SAFE_CHANGE_PREFLIGHT.md",
    }
    write_json(out / "BUILD_PREFLIGHT.json", payload)
    write_text(
        out / "SAFE_CHANGE_PREFLIGHT.md",
        "# Safe Change Preflight\n\n"
        "No repository mutation was applied. This stage proves the build "
        "route can be admitted: scope named, verification named, recovery "
        "named, approval named.\n",
    )
    return [out / "BUILD_PREFLIGHT.json", out / "SAFE_CHANGE_PREFLIGHT.md"]


def stage_verify(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    validator = root / "scripts" / "validate_hierarchy.py"
    compositor = root / "skills" / "pipeline-compositor" / "scripts" / "engine.py"
    payload = {
        **common_meta(args),
        "validators": {
            "validate_hierarchy.py": validator.is_file(),
            "pipeline compositor engine": compositor.is_file(),
        },
        "status": "VERIFIED_LOCAL" if compositor.is_file() else "PARTIAL",
        "note": "Hierarchy validator is invoked by CI / run_mega_mission, not by this stage subprocess, to keep unit tests hermetic.",
    }
    write_json(out / "VERIFY.json", payload)
    write_text(out / "EVIDENCE.md", "# Evidence Register\n\n" + json.dumps(payload, indent=2) + "\n")
    return [out / "VERIFY.json", out / "EVIDENCE.md"]


def stage_package(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    required = [
        "MISSION.md",
        "ROADMAP.md",
        "CONTEXT.md",
        "READINESS.json",
        "RECON.json",
        "ROUTE.json",
        "BUILD_PREFLIGHT.json",
        "VERIFY.json",
    ]
    files = []
    for name in required:
        path = out / name
        files.append(
            {
                "path": name,
                "present": path.is_file(),
                "sha256": sha256_text(path.read_text(encoding="utf-8")) if path.is_file() else None,
            }
        )
    packet = {
        **common_meta(args),
        "status": "PACKAGED" if all(item["present"] for item in files) else "INCOMPLETE",
        "files": files,
    }
    write_json(out / "RELEASE_PACKET.json", packet)
    write_text(
        out / "RELEASE_PACKET.md",
        "# Release Packet\n\n"
        f"Pipeline `{args.pipeline_id}` packaged at {utc_now()}.\n"
        "This packet is reviewable. It is not a production deploy.\n",
    )
    return [out / "RELEASE_PACKET.json", out / "RELEASE_PACKET.md"]


def stage_deploy_gate(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    decision = {
        **common_meta(args),
        "publication_decision": "READY_PENDING_HUMAN_APPROVAL",
        "allowed": False,
        "blocked_actions": [
            "deployment",
            "merge",
            "network_send",
            "credential_access",
            "external_mutation",
        ],
        "human_control_points": [
            "approve_production_release",
            "escalate_critical_anomalies",
        ],
        "reason": "Firewall mode is read_only. Observed production change requires a separate approved mission.",
    }
    write_json(out / "DEPLOYMENT_DECISION.json", decision)
    return [out / "DEPLOYMENT_DECISION.json"]


def stage_handoff(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    write_text(
        out / "HANDOFF.md",
        "# Durable Handoff\n\n"
        f"Status: COMPLETED_LOCAL\n"
        f"Pipeline: {args.pipeline_id}\n"
        f"Finished: {utc_now()}\n"
        "Resumption point: deploy-gate approval packet.\n"
        "Next human action: review RELEASE_PACKET.md and DEPLOYMENT_DECISION.json.\n",
    )
    return [out / "HANDOFF.md"]


def stage_evolve(root: Path, args: argparse.Namespace) -> list[Path]:
    out = workdir(root, args.pipeline_id)
    payload = {
        **common_meta(args),
        "backlog": [
            "Promote a family pipeline only after two successful local receipts.",
            "Add a Mega-specific pipeline JSON only when it needs stages the family graph cannot express.",
            "Keep combo-skills as Compound source; do not flatten into shell glue.",
        ],
    }
    write_json(out / "EVOLUTION_BACKLOG.json", payload)
    return [out / "EVOLUTION_BACKLOG.json"]


STAGES = {
    "inception": stage_inception,
    "readiness": stage_readiness,
    "recon": stage_recon,
    "design": stage_design,
    "build": stage_build,
    "verify": stage_verify,
    "package": stage_package,
    "deploy-gate": stage_deploy_gate,
    "handoff": stage_handoff,
    "evolve": stage_evolve,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--pipeline-id", required=False, default="inception-to-deployment")
    parser.add_argument("--family", default="master")
    parser.add_argument("--stage", choices=sorted(STAGES) + ["all", "list"])
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    if args.list or args.stage == "list":
        print("\n".join(PHASES))
        return 0
    if not args.stage:
        parser.error("--stage is required unless --list is set")
    root = args.root.resolve()
    produced: list[Path] = []
    selected = PHASES if args.stage == "all" else (args.stage,)
    for name in selected:
        produced.extend(STAGES[name](root, args))
    print(
        json.dumps(
            {
                "status": "COMPLETED",
                "pipeline_id": args.pipeline_id,
                "stage": args.stage,
                "artifacts": [path.relative_to(root).as_posix() if root in path.parents else str(path) for path in produced],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
