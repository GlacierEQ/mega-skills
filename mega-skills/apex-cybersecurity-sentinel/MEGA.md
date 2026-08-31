# APEX Cybersecurity Sentinel

## Mission

Autonomous enterprise cybersecurity defense, red-team penetration modeling, privilege escalation detection, and zero-trust perimeter auditing.

## Compounding structure

- Required combos: `long-horizon-core`, `cybersecurity-threat-analysis`, `secure-service-deployment`
- Conditional combos: `capability-readiness`, `epistemic-verification-chain`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `CYBERSECURITY_SENTINEL_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `CYBERSECURITY_SENTINEL_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `CYBERSECURITY_SENTINEL_RECORD.md` upon mission completion.

## Local validation

Full threat simulation verifies zero privilege escalation vulnerabilities and produces cryptographically hashed audit receipts.

## Non-goals

Live destructive intrusion against unowned infrastructure or unapproved production mutations
