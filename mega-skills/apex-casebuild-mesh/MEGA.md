# APEX Casebuild Mesh

## Mission

Continuously organize a legal matter across repositories, cloud evidence stores, review systems, and task surfaces into an evidence-backed, recoverable case mesh while preserving original sources, node plurality, provenance, and attorney decision authority.

## Selection

Use for long-horizon case building that spans multiple systems, repeated evidence acquisition, docket/chronology reconciliation, integrity verification, attorney review, and exhibit or production readiness. For a narrow one-pass organization task, use `casebuild-mesh-organization` directly.

## Compounding structure

- Direct Skill: `casebuild-mesh-organization`
- Required combos: `long-horizon-core`, `forensic-docket-intelligence`, `cross-cloud-memory-synthesis`, `epistemic-verification-chain`
- Conditional combos: `capability-readiness`, `court-evidence-compiler`, `voice-evidence-authenticator`, `guarded-automation-loop`, `evidence-to-evolution-loop`

## Incremental value

This Mega Skill adds mission-wide route selection, durable cross-system state, source/derivative boundaries, reconciliation gates, attorney-review routing, completion scoring, and exact recovery points. It does not copy the procedures owned by its Skills or Combos.

## Execution protocol

1. Initialize `MISSION.md`, `ROADMAP.md`, `EVIDENCE.md`, `CONTEXT.md`, and `HANDOFF.md` in the active matter workspace.
2. Run `casebuild-mesh-organization` to establish the matter graph, evidence identity layer, integrity ledger, and preferred operational route.
3. Execute required Combos in dependency order, passing only verified artifacts and stable IDs between stages.
4. Select conditional Combos from observed evidence type, readiness, automation risk, and review requirements.
5. Reconcile repositories, cloud nodes, indexes, review queues, and task states; preserve contradictions and create owned acquisition targets.
6. Route legal filing, persuasive strategy, privilege waiver, public release, deletion, merge, and other consequential external actions to human control points.
7. Emit `CASEBUILD_MESH_MISSION_RESULT.md` and update the exact resume point after every material run.

## Phase gates

1. **Identity gate:** stable case/evidence IDs and source locators exist.
2. **Integrity gate:** originals and derivatives are distinguished; hashes or explicit exceptions are recorded.
3. **Traceability gate:** material claims and chronology entries map to evidence IDs.
4. **Reconciliation gate:** orphans, broken links, state conflicts, and stale assertions are surfaced.
5. **Review gate:** sensitivity, privilege, attorney decisions, and approval boundaries are visible.
6. **Completion gate:** remaining gaps are satisfied, assigned, or explicitly blocked; a reviewer can traverse issue → fact → evidence → source → integrity receipt.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `CASEBUILD_MESH_REGISTER.md`
- `CASEBUILD_MESH_MISSION_RESULT.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `read_connected_sources`, `run_local_tests`, `hash_local_artifacts`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `legal_filing`, `autonomous_legal_decision`, `privilege_waiver`, `public_release`, `deletion`, `merge`, `credential_access`, `execute_unknown_program`
- Approval required for: `external_mutation`, `network_send`, `file_submission`, `deployment`, and any action changing an authoritative external record

## Human control points

- `approve_case_scope_and_sensitive_access`
- `approve_external_mutation`
- `attorney_decides_strategy_and_filing`
- `approve_production_or_exhibit_release`
- `resolve_critical_integrity_anomaly`

## Output contract

Produce `CASEBUILD_MESH_MISSION_RESULT.md` with verified state, node and evidence coverage, integrity exceptions, contradictions, attorney-review items, ranked next frontier, completion scorecard, and exact resume point.

## Local validation

Validation passes when all phase gates have evidence-backed results, no original source has been altered, every consequential claim has a source or declared limitation, and the mission can resume without reconstructing prior context.

## Non-goals

Do not impose a single architectural authority, silently flatten source differences, make persuasive legal arguments, choose litigation strategy, file with a court, or mutate external systems without the required authorization.
