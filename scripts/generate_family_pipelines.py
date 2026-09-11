#!/usr/bin/env python3
"""Generate family deep-work pipeline JSON from the shared span contract."""

from __future__ import annotations

import json
from pathlib import Path

SPAN = (
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

PRODUCES = {
    "inception": ["MISSION.md", "ROADMAP.md", "CONTEXT.md", "inception.json"],
    "readiness": ["READINESS.json"],
    "recon": ["RECON.json"],
    "design": ["ROUTE.json", "ARCHITECTURE.md"],
    "build": ["BUILD_PREFLIGHT.json", "SAFE_CHANGE_PREFLIGHT.md"],
    "verify": ["VERIFY.json", "EVIDENCE.md"],
    "package": ["RELEASE_PACKET.json", "RELEASE_PACKET.md"],
    "deploy-gate": ["DEPLOYMENT_DECISION.json"],
    "handoff": ["HANDOFF.md"],
    "evolve": ["EVOLUTION_BACKLOG.json"],
}

CONSUMES = {
    "readiness": "inception.json",
    "recon": "READINESS.json",
    "design": "RECON.json",
    "build": "ROUTE.json",
    "verify": "BUILD_PREFLIGHT.json",
    "package": "VERIFY.json",
    "deploy-gate": "RELEASE_PACKET.json",
    "handoff": "DEPLOYMENT_DECISION.json",
    "evolve": "HANDOFF.md",
}

DEFAULT_COMBOS = [
    "long-horizon-core",
    "capability-readiness",
    "pipeline-orchestration",
]

FAMILIES = {
    "telecommunications-evolution": {
        "display_name": "APEX Telecommunications Evolution",
        "family": "telecommunications",
        "description": "Evolve provider-neutral telecommunications around clean upstream cores with Genius Mastery, source-bearing receipts, semantic evals and human-gated release packets.",
        "mega_roots": [
            "apex-telecommunications",
            "apex-genius-mastery",
            "apex-safe-change-orchestrator",
            "apex-architectural-evolution-engine",
        ],
        "required_combos": [
            "long-horizon-core",
            "capability-readiness",
            "pipeline-orchestration",
            "telecommunications-mission-orchestration",
            "genius-epistemic-engineering",
            "epistemic-verification-chain",
            "polyglot-systems-verification",
        ],
        "stage_runner": "scripts/deep_work_stage.py",
    },
    "inception-to-deployment": {
        "display_name": "Inception to Deployment",
        "family": "master",
        "description": "Master deep-work pipeline from mission intake through a human-gated deployment packet.",
        "mega_roots": [
            "apex-always-on-core",
            "apex-adaptive-operations",
            "apex-sovereign-runtime",
            "far-away-party",
            "apex-omniversal-memory",
            "apex-fleet-harmonizer",
            "apex-docgen-synthesis",
            "apex-safe-change-orchestrator",
            "apex-self-healing-forge",
            "apex-autonomous-software-engineering",
            "apex-architectural-evolution-engine",
            "apex-dev-fork-orchestrator",
            "apex-web-build-system",
            "apex-vercel-web-foundry",
            "apex-backend-infrastructure-engine",
            "apex-secure-cloud-foundry",
        ],
        "required_combos": DEFAULT_COMBOS,
        "stage_runner": "scripts/deep_work_stage.py",
    },
    "control-plane": {
        "display_name": "Control Plane",
        "family": "control-plane",
        "description": "Session continuity, adaptive operations, guarded always-on execution, and proof-bound runtime amplification.",
        "mega_roots": [
            "apex-always-on-core",
            "apex-adaptive-operations",
            "apex-sovereign-runtime",
            "far-away-party",
            "apex-genius-mastery",
        ],
        "required_combos": [
            "long-horizon-core",
            "capability-readiness",
            "pipeline-orchestration",
            "genius-epistemic-engineering",
            "genius-entity-forge",
            "epistemic-verification-chain",
        ],
        "stage_runner": "scripts/runtime_amplified_stage.py",
        "runtime_profile": "control-plane-max-runtime-v1",
    },
    "memory-fleet": {
        "display_name": "Memory and Fleet",
        "family": "memory-fleet",
        "description": "Recon, cross-cloud memory synthesis, and fleet harmonization.",
        "mega_roots": [
            "apex-omniversal-memory",
            "apex-fleet-harmonizer",
            "apex-docgen-synthesis",
        ],
        "required_combos": DEFAULT_COMBOS,
        "stage_runner": "scripts/deep_work_stage.py",
    },
    "change-swe": {
        "display_name": "Change and Software Engineering",
        "family": "change-swe",
        "description": "Bounded repair, architectural evolution, and fork control without autonomous merge.",
        "mega_roots": [
            "apex-safe-change-orchestrator",
            "apex-self-healing-forge",
            "apex-autonomous-software-engineering",
            "apex-architectural-evolution-engine",
            "apex-dev-fork-orchestrator",
        ],
        "required_combos": DEFAULT_COMBOS,
        "stage_runner": "scripts/deep_work_stage.py",
    },
    "ship-cloud": {
        "display_name": "Ship and Cloud",
        "family": "ship-cloud",
        "description": "Web/backend/cloud packaging that stops at a deployment approval packet.",
        "mega_roots": [
            "apex-web-build-system",
            "apex-vercel-web-foundry",
            "apex-backend-infrastructure-engine",
            "apex-secure-cloud-foundry",
        ],
        "required_combos": DEFAULT_COMBOS,
        "stage_runner": "scripts/deep_work_stage.py",
    },
}


def make_stage(
    pipeline_id: str,
    family: str,
    phase: str,
    previous: str | None,
    runner: str,
) -> dict:
    produces = [f"missions/{pipeline_id}/{name}" for name in PRODUCES[phase]]
    consumes = [f"missions/{pipeline_id}/{CONSUMES[phase]}"] if phase in CONSUMES else []
    return {
        "id": phase,
        "phase": phase,
        "needs": [previous] if previous else [],
        "command": [
            "{python}",
            runner,
            "--root",
            "{workspace}",
            "--pipeline-id",
            pipeline_id,
            "--family",
            family,
            "--stage",
            phase,
        ],
        "consumes": consumes,
        "produces": produces,
        "resume_safe": phase not in {"deploy-gate", "verify"},
        "approval_required": phase == "deploy-gate",
        "timeout_seconds": 120,
    }


def make_pipeline(pipeline_id: str, meta: dict) -> dict:
    stages = []
    previous = None
    runner = str(meta.get("stage_runner") or "scripts/deep_work_stage.py")
    for phase in SPAN:
        stages.append(make_stage(pipeline_id, meta["family"], phase, previous, runner))
        previous = phase
    return {
        "schema_version": 1,
        "id": pipeline_id,
        "display_name": meta["display_name"],
        "description": meta["description"],
        "family": meta["family"],
        "span": list(SPAN),
        "mega_roots": meta["mega_roots"],
        "required_combos": list(meta.get("required_combos") or DEFAULT_COMBOS),
        "deploy_mode": "approval_packet_only",
        "max_parallel": 1,
        "manifest": f"missions/{pipeline_id}/pipeline-execution-manifest.json",
        "stages": stages,
    }


def make_registry() -> dict:
    entries = []
    for pipeline_id, meta in FAMILIES.items():
        entry = {
            "id": pipeline_id,
            "display_name": meta["display_name"],
            "ownership": "glaciereq",
            "maturity": "active",
            "version": "1.1.0" if pipeline_id == "control-plane" else "1.0.0",
            "path": f"pipelines/{pipeline_id}.json",
            "family": meta["family"],
            "span": list(SPAN),
            "mega_roots": meta["mega_roots"],
            "required_combos": list(meta.get("required_combos") or DEFAULT_COMBOS),
            "deploy_mode": "approval_packet_only",
            "runner": "scripts/run_deep_work_pipeline.py",
        }
        stage_runner = str(meta.get("stage_runner") or "scripts/deep_work_stage.py")
        if stage_runner != "scripts/deep_work_stage.py":
            entry["stage_runner"] = stage_runner
        if meta.get("runtime_profile"):
            entry["runtime_profile"] = meta["runtime_profile"]
        entries.append(entry)
    entries.append(
        {
            "id": "anthropic-applied-ai-readiness",
            "display_name": "Anthropic Applied AI Readiness",
            "ownership": "glaciereq",
            "maturity": "active",
            "version": "1.0.0",
            "path": "pipelines/anthropic-applied-ai-readiness.json",
            "family": "mission",
            "span": ["verify", "package"],
            "mega_roots": [],
            "deploy_mode": "approval_packet_only",
            "runner": "skills/pipeline-compositor/scripts/engine.py",
        }
    )
    entries.append(
        {
            "id": "cultivate-main",
            "display_name": "Cultivate Main",
            "ownership": "glaciereq",
            "maturity": "active",
            "version": "1.0.0",
            "path": "pipelines/cultivate-main.json",
            "family": "change-swe",
            "span": ["recon", "design", "verify", "package", "deploy-gate", "handoff"],
            "mega_roots": ["apex-safe-change-orchestrator", "apex-always-on-core"],
            "deploy_mode": "approval_packet_only",
            "runner": "scripts/cultivate_main.py",
        }
    )
    return {"schema_version": 1, "entries": entries}


def write_all(root: Path) -> list[str]:
    written = []
    pipelines = root / "pipelines"
    pipelines.mkdir(parents=True, exist_ok=True)
    for pipeline_id, meta in FAMILIES.items():
        path = pipelines / f"{pipeline_id}.json"
        path.write_text(json.dumps(make_pipeline(pipeline_id, meta), indent=2) + "\n", encoding="utf-8")
        written.append(path.as_posix())
    registry = root / "registry" / "pipelines.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    generated = make_registry()
    if registry.is_file():
        existing = json.loads(registry.read_text(encoding="utf-8"))
        known = {entry["id"] for entry in generated["entries"]}
        extras = [entry for entry in existing.get("entries", []) if entry.get("id") not in known]
        generated["entries"].extend(extras)
    registry.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
    written.append(registry.as_posix())
    return written


def main() -> int:
    written = write_all(Path(__file__).resolve().parents[1])
    print(json.dumps({"status": "GENERATED", "files": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
