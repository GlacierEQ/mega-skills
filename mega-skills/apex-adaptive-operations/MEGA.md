# APEX Adaptive Operations

## Mission

Mission-wide coordination of observed signals, readiness, approved operational responses, guarded run records, feedback proposals, and recoverable state without implying automatic external execution.

## Compounding structure

- Required combos: `long-horizon-core`, `signal-to-decision-loop`
- Conditional combos: `capability-readiness`, `automation-control`, `guarded-automation-loop`, `evidence-to-evolution-loop`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `ADAPTIVE_OPERATIONS_MISSION_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `ADAPTIVE_OPERATIONS_MISSION_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `ADAPTIVE_OPERATIONS_MISSION_RECORD.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
