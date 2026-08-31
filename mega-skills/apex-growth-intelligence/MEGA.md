# APEX Growth Intelligence

## Mission

Data-driven growth engineering, automated conversion rate optimization (CRO), competitive positioning extraction, and statistical A/B experimentation.

## Compounding structure

- Required combos: `long-horizon-core`, `growth-analytics-optimization`, `signal-to-decision-loop`
- Conditional combos: `capability-readiness`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `GROWTH_INTELLIGENCE_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `GROWTH_INTELLIGENCE_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `GROWTH_INTELLIGENCE_RECORD.md` upon mission completion.

## Local validation

A/B sample size power calculations verify statistical significance thresholds with zero p-hacking.

## Non-goals

Unauthorized email dispatch, dark patterns, or real ad credit charging
