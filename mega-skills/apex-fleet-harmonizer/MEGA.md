# APEX Fleet Harmonizer

## Mission

Long-horizon batch coordination, cross-repository state tracking, regression gating, automated rollbacks, and lossless branch pruning across large GitHub accounts.

## Compounding structure

- Required combos: `long-horizon-core`
- Conditional combos: `capability-readiness`, `recon-and-map`, `fleet-recon-and-harmonize`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `fleet-harmonization-mission-result.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `fleet-harmonization-mission-result.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `fleet-harmonization-mission-result.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
