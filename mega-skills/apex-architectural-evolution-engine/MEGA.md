# APEX Architectural Evolution Engine

## Mission

Continuous autonomous codebase modernization: diagnoses architectural bottlenecks, designs formal Architecture Decision Records, conducts clean refactoring with AST self-healing, and enforces Google Senior Staff engineering invariants across the estate.

## Compounding structure

- Required combos: `long-horizon-core`, `architectural-refactoring-engine`
- Conditional combos: `capability-readiness`, `closed-loop-code-repair`, `upstream-fork-harmonization`, `recon-and-map`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
