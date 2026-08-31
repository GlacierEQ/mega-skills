# APEX Capability Foundry

## Mission

A controlled mission sequence that converts repeated evidence into a reusable, governed capability increment with repository, registry, validation, release, and recovery evidence.

## Compounding structure

- Required combos: `long-horizon-core`, `evidence-to-evolution-loop`, `skill-forge`
- Conditional combos: `capability-readiness`, `recon-and-map`, `signal-to-decision-loop`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `CAPABILITY_FOUNDRY_MISSION_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `CAPABILITY_FOUNDRY_MISSION_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `CAPABILITY_FOUNDRY_MISSION_RECORD.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
