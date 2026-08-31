# APEX Forensic Litigation Sentinel

## Mission

Autonomous legal prosecution and investigative warfare: dissects judicial dockets, aligns minute-by-minute transcripts against official records, detects 39-second impossibilities, and outputs verified impeachment traps for state and federal courts.

## Compounding structure

- Required combos: `long-horizon-core`, `forensic-docket-intelligence`
- Conditional combos: `capability-readiness`, `court-evidence-compiler`, `voice-evidence-authenticator`, `automation-control`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `FORENSIC_LITIGATION_SENTINEL_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `FORENSIC_LITIGATION_SENTINEL_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `FORENSIC_LITIGATION_SENTINEL_RECORD.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
