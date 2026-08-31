# APEX Legal Warfare

## Mission

End-to-end litigation campaign orchestration, durable case evidence tracking, court filing deadlines, exhibit tethering, and cross-jurisdictional state synchronization.

## Compounding structure

- Required combos: `long-horizon-core`
- Conditional combos: `capability-readiness`, `court-evidence-compiler`, `automation-control`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `court-admissible-litigation-packet.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `court-admissible-litigation-packet.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `court-admissible-litigation-packet.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
