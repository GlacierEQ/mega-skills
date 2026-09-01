# Far Away Party

## Mission

Conditional selection of Compounding Combo Skills, durable state, phase gates, safe resumption, and evidence-backed integration across a long-horizon mission.

## Compounding structure

- Required combos: `long-horizon-core`
- Conditional combos: `capability-readiness`, `signal-to-decision-loop`, `mission-aware-operating-loop`, `guarded-automation-loop`, `evidence-to-evolution-loop`, `recon-and-map`, `skill-forge`, `automation-control`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `evidence-backed-mission-result.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `evidence-backed-mission-result.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `evidence-backed-mission-result.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.

## Source-Preserving Mission Invariants — 2026-08-31

1. **Original sources outrank compaction.** Durable state files summarize mission state; they never supersede original evidence, journal text, prior source assertions, or provenance.
2. **Source state and truth state are separate.** "Not reopened this pass" may be recorded as a source-access state but must not be converted into "false," "weak," "quarantined," or "removed."
3. **Journal preservation.** When chat/export history functions as a regularly kept journal, preserve original wording, timestamp/order, speaker, path, and context; analyses are overlays.
4. **Alias expansion.** Name/OCR variants widen search. Identity resolution uses event/source continuity; same-name unrelated matters remain separate until linkage is proved.
5. **Contradictions become work.** Preserve both sides and create a discriminating-evidence task.
6. **No premature mission close.** A mission does not close while a materially executable route remains, unless the mission boundary expressly excludes it.
7. **Legal lifecycle projection.** For full-case missions, route from evidence recovery through pleadings, exhibits, discovery, hearing, enforcement, and post-ruling preservation while keeping filing/service as separately receipted external acts.
8. **User-authorized durable writes are additive by default.** Prefer new ledgers/overlays/history records to destructive replacement of source-bearing files.
