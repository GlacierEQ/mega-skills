---
id: apex-orchestrator-mesh
display_name: Apex Orchestrator Mesh
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Apex Orchestrator Mesh (Mega Skill)

## Mission

End-to-end mission system for the Holographic Mesh Orchestrator. Routes user mandates through the six-stage lifecycle (INTAKE -> DECOMPOSE -> DISPATCH -> VERIFY -> FUSE -> DELIVER) across 12 specialist lanes, enforces the 12 production-grade logic packets of `apex-orchestration`, and produces a verifiable `delivery.json` with reproducible receipt chain and queryable memory write.

## Compounding structure

- **Required combo:** `apex-mesh-dispatch` (ordered REASON -> CODE -> VERIFY -> REVIEW -> DELIVER)
- **Conditional combos:**
  - `multi-agent-orchestration-mesh` — when the mission is cross-domain and needs multi-agent topology design
  - `capability-readiness` — when the mission is the first use of a new lane or model
  - `closed-loop-code-repair` — when VERIFY lane rejects and re-dispatch is needed
  - `runtime-operations` — when the mission spans live systems (DB, RPC, cloud)

## Execution protocol

1. **Boot.** Load `apex-orchestration` skill and all 12 packets. Verify all 12 lanes are reachable via the OpenRouter free gateway. Initialize `runs/<mission_id>/` directory.
2. **INTAKE.** Apply Packet 02. Produce `intake.json` with scope, budget, blast-radius, classification. If F-INT-01 or F-INT-02 fires, BLOCK with cause.
3. **DECOMPOSE.** Apply Packets 01, 04. Produce `dag.json` with nodes naming lane, gate, and receipt. If F-DEC-01 or F-DEC-02 fires, BLOCK with cause.
4. **DISPATCH.** Apply Packets 03, 04, 11. Fan out subtasks in parallel. Each subtask returns a receipt. If F-DIS-01 or F-DIS-02 fires, BLOCK.
5. **VERIFY.** Apply Packet 05. Audit with VERIFY lane. Refine with REVIEW lane. Three signatures required for code. If F-VER-01 or F-VER-02 fires, re-dispatch.
6. **FUSE.** Apply Packet 06. Deduplicate, resolve conflicts by dominant-verified evidence. Produce `fused.json` with `receipt_chain_sha256`. If F-FUSE-01 or F-FUSE-02 fires, BLOCK.
7. **DELIVER.** Apply Packets 07, 08, 12. Produce `delivery.json` with closed-set status, three signatures, `memory_write_id`. If F-DEL-01 or F-DEL-02 fires, BLOCK then REFUSE.
8. **Handoff.** Persist mission state to memory (Packet 08). Write `HANDOFF.md` for the next mission or session.

## Durable state files

All under `runs/<mission_id>/`:

- `MISSION.md` — original mandate + scope
- `intake.json` — INTAKE stage evidence
- `dag.json` — DECOMPOSE stage evidence
- `receipts/<mission_id>-{INTAKE,DECOMPOSE,DISPATCH,VERIFY,FUSE,DELIVER}.json` — per-stage receipts
- `subtask-receipts/<node_id>.json` — one per dispatched subtask
- `fused.json` — FUSE result with chain hash
- `delivery.json` — final delivery with status, signatures, memory_write_id
- `audit.jsonl` — every action, append-only
- `token_log.jsonl` — every `gateway_chat` call
- `routing_decisions.jsonl` — every DECOMPOSE decision
- `HANDOFF.md` — handoff to next session

## Cognitive firewall

- **Mode:** `read_only` by default; `mutating` only when the mission's blast-radius explicitly allows.
- **Fail closed:** `true` for security (Packet 10) and memory (Packet 08).
- **Allowed actions:** `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`, `dispatch_to_mesh_lane`.
- **Forbidden actions:** `external_mutation`, `network_send` (unless in `blast_radius.external`), `file_submission`, `deletion` (without explicit checkpoint), `deployment` (without human approval), `merge` (without human approval), `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`.

## Human control points

- `approve_production_release` — required before any deployment or merge
- `escalate_critical_anomalies` — required on F-VER BLOCKER, F-DEL-02 chain_hash_drift, or security boundary violation
- `raise_budget` — required to recover from F-INT-02
- `resolve_conflict` — required to recover from F-FUSE-02

## Output contract

Produce `delivery.json` conforming to `apex-orchestration/schemas/delivery.schema.json`. Status MUST be one of `SHIPPED`, `BLOCKED`, `REFUSED`. `receipt_chain_sha256` MUST be reproducible from staged receipts. `memory_write_id` MUST be present and queryable.

## Local validation

- 100% of unit tests in `apex-orchestration/tests/test_apex_orchestration.py` pass.
- 12 packets present at version 1.0.0.
- 3 JSON-Schema files validate.
- `skill.py mesh` returns 12 lanes.
- `skill.py routes` returns 8 rules.
- `skill.py failures` returns 13 codes.
- Receipt chain hash reproducible.
- `delivery.json` validates against delivery schema.

## Non-goals

- Unbounded external state mutations.
- Cross-cloud autonomous deployment without human approval.
- Production writes without L2 proof.
- Memory writes without provenance.

## Routing for derived layers

The Mega Skill is the source of truth for **how** missions execute. The Combo Skill (`apex-mesh-dispatch`) is a specific ordered route. The Skill (`apex-orchestration`) is the source of truth for **what** the mesh is. Do not duplicate; reference.
