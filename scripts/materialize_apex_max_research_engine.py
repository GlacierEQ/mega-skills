#!/usr/bin/env python3
"""Idempotently materialize the APEX Max Research Engine registry delta."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
DELTA = json.loads((REGISTRY / "apex-max-research-engine.entries.json").read_text())


def step(member_id, number, consumes, produces, validation):
    return {"step": number, "member_id": member_id, "consumes": consumes, "produces": produces, "validation": validation}


def member(member_id, kind, role, required=True):
    return {"id": member_id, "kind": kind, "role": role, "required": required}


SPIRAL = {
    "id": "max-research-spiral",
    "display_name": "Max Research Spiral",
    "ownership": "glaciereq",
    "maturity": "candidate",
    "version": "0.1.0",
    "path": "combo-skills/max-research-spiral",
    "entrypoint": "combo-skills/max-research-spiral/COMBO.md",
    "selection": {
        "use_when": ["A question requires recursive source discovery, contradiction probing, and confidence updates beyond first-pass search."],
        "do_not_use_when": ["A single authoritative source fully answers a low-risk lookup."],
    },
    "members": [
        member("mission-contract", "skill", "Set mandate, proof floor, source scope, and stop conditions."),
        member("recon-and-map", "compound-skill", "Discover source-of-truth locations, aliases, and reachable research lanes."),
        member("evidence-register", "skill", "Register extracted claims, source IDs, timestamps, and proof state."),
        member("claim-calibration", "skill", "Calibrate each claim against evidence, contradiction, and source limits."),
        member("quality-gate", "skill", "Authorize recurse, stop, block, or deliver based on proof floor."),
    ],
    "execution": {"ordered_steps": [
        step("mission-contract", 1, ["User request", "Risk class", "Output target"], ["MISSION.md"], "Scope, proof floor, and stop conditions are explicit."),
        step("recon-and-map", 2, ["MISSION.md"], ["SOURCE_MAP.md"], "Source lanes, aliases, and access limits are recorded."),
        step("evidence-register", 3, ["Source extracts", "Search results", "Loaded documents"], ["EVIDENCE.md", "SPIRAL_LOG.jsonl"], "Material claims map to evidence or assumptions."),
        step("claim-calibration", 4, ["EVIDENCE.md", "Contradictions", "Open gaps"], ["CLAIM_BOUNDARIES.md"], "Claim wording matches available proof."),
        step("quality-gate", 5, ["Spiral state", "Claim boundaries", "Proof floor"], ["SPIRAL_GATE.md"], "Recurse, stop, or block decision is reproducible."),
    ]},
    "integration": {
        "handoffs": [
            {"from_member": "mission-contract", "to_member": "recon-and-map", "required_inputs": ["Research mandate", "Proof floor", "Source scope"], "accepted_outputs": ["Source map and search lanes"], "failure_owner": "research lead"},
            {"from_member": "recon-and-map", "to_member": "evidence-register", "required_inputs": ["Source IDs", "Aliases", "Access limits"], "accepted_outputs": ["Evidence rows with source references"], "failure_owner": "source mapper"},
            {"from_member": "evidence-register", "to_member": "claim-calibration", "required_inputs": ["Extracted claims", "Provenance"], "accepted_outputs": ["Calibrated claim boundaries"], "failure_owner": "evidence owner"},
            {"from_member": "claim-calibration", "to_member": "quality-gate", "required_inputs": ["Confidence", "Gaps", "Contradictions"], "accepted_outputs": ["Recurse, stop, or block decision"], "failure_owner": "epistemic auditor"},
        ],
        "evidence_requirements": ["Record each spiral cycle, query, source, claim, contradiction, confidence delta, and remaining gap."],
        "risk_boundaries": ["Never claim source exhaustion without naming searched scope and access limits."],
        "quality_gates": ["Contradiction probes are attempted, unresolved gaps are explicit, and claim wording matches proof tier."],
        "state_updates": ["Append every cycle to SPIRAL_LOG.jsonl and preserve the final stop decision."],
    },
    "compounding": {
        "inherits": ["Mission boundary", "Source map", "Evidence register", "Claim calibration", "Quality gate"],
        "adds": "Recursive search intelligence that converts each pass into sharper queries, adverse probes, missing-evidence checks, and confidence updates.",
        "compound_artifact": "MAX_RESEARCH_SPIRAL_RECORD.md",
        "next_layer_ready_when": ["The final cycle has a reproducible stop decision.", "No material claim exceeds its evidence.", "Next searches are complete or intentionally deferred."],
    },
}

DIAMOND = {
    "id": "diamond-research-topography",
    "display_name": "Diamond Research Topography",
    "ownership": "glaciereq",
    "maturity": "candidate",
    "version": "0.1.0",
    "path": "combo-skills/diamond-research-topography",
    "entrypoint": "combo-skills/diamond-research-topography/COMBO.md",
    "selection": {
        "use_when": ["Research findings require adversarial Evidence, Logic, Counterargument, and Action review before delivery."],
        "do_not_use_when": ["A low-risk lookup is fully answered by one authoritative source and no consequential inference is required."],
    },
    "members": [
        member("evidence-register", "skill", "Evidence Apex: verify source identity, provenance, timestamps, and quote fidelity."),
        member("claim-calibration", "skill", "Logic Apex: check inference strength, causation, scope, and proof-tier wording."),
        member("epistemic-gate", "skill", "Counterargument Apex: attack assumptions and find contradictions, adverse authority, and alternatives."),
        member("roadmap-builder", "skill", "Action Apex: convert verified findings into options, risks, next searches, and decisions."),
        member("quality-gate", "skill", "Fusion Core: accept, block, or return for another spiral cycle."),
    ],
    "execution": {"ordered_steps": [
        step("evidence-register", 1, ["Claim graph", "Source extracts"], ["EVIDENCE_APEX.md"], "Every material claim maps to a source or limitation."),
        step("claim-calibration", 2, ["Claim graph", "EVIDENCE_APEX.md"], ["LOGIC_APEX.md"], "Reasoning does not outrun evidence."),
        step("epistemic-gate", 3, ["Claim graph", "Source map"], ["COUNTERARGUMENT_APEX.md"], "The strongest contrary theory is stated or the source gap is named."),
        step("roadmap-builder", 4, ["Accepted facts", "Conflicts", "Unknowns"], ["ACTION_APEX.md"], "Recommendations are evidence-bounded and executable."),
        step("quality-gate", 5, ["Four apex reports"], ["DIAMOND_REVIEW.md"], "Conflicts are preserved and delivery status is justified."),
    ]},
    "integration": {
        "handoffs": [
            {"from_member": "evidence-register", "to_member": "claim-calibration", "required_inputs": ["Source-bound evidence map"], "accepted_outputs": ["Proof-tiered reasoning audit"], "failure_owner": "evidence apex"},
            {"from_member": "claim-calibration", "to_member": "epistemic-gate", "required_inputs": ["Calibrated claims", "Inferred links"], "accepted_outputs": ["Counterargument and contradiction record"], "failure_owner": "logic apex"},
            {"from_member": "epistemic-gate", "to_member": "roadmap-builder", "required_inputs": ["Accepted facts", "Conflicts", "Unknowns"], "accepted_outputs": ["Action options and evidence-needed list"], "failure_owner": "counterargument apex"},
            {"from_member": "roadmap-builder", "to_member": "quality-gate", "required_inputs": ["Action options", "Reviewed risks"], "accepted_outputs": ["Final Diamond review decision"], "failure_owner": "action apex"},
        ],
        "evidence_requirements": ["Record all four apex outputs separately and preserve unresolved conflict."],
        "risk_boundaries": ["Do not merge away conflict or convert inference into verified fact."],
        "quality_gates": ["Evidence, Logic, Counterargument, and Action reports exist and recommendations are bounded by evidence."],
        "state_updates": ["Write the fused ACCEPT, RESEARCH_MORE, BLOCKED, or NEEDS_HUMAN_DECISION result to DIAMOND_REVIEW.md."],
    },
    "compounding": {
        "inherits": ["Evidence provenance", "Claim calibration", "Epistemic challenge", "Action planning", "Quality gating"],
        "adds": "A four-apex adversarial pressure test that preserves disagreements while converting verified findings into bounded action.",
        "compound_artifact": "DIAMOND_REVIEW.md",
        "next_layer_ready_when": ["All four apexes pass or Fusion Core returns an explicit block or research-more decision with named missing evidence."],
    },
}


def upsert(path: Path, additions):
    data = json.loads(path.read_text())
    by_id = {entry["id"]: entry for entry in data["entries"]}
    for entry in additions:
        by_id[entry["id"]] = entry
    data["entries"] = sorted(by_id.values(), key=lambda item: item["id"])
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


upsert(REGISTRY / "mega-skills.json", [DELTA["mega_skill_entry"]])
upsert(REGISTRY / "combo-skills.json", [SPIRAL, DIAMOND])
subprocess.run(["python", "scripts/generate_mega_skill_pyramids.py"], cwd=ROOT, check=True)
subprocess.run(["python", "scripts/generate_mega_skill_pyramids.py", "--check"], cwd=ROOT, check=True)
print("APEX Max Research Engine registries materialized and pyramid validation passed.")
