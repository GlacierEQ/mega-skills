# APEX Adaptive Operations

## Mission

Mission-wide coordination of observed signals, readiness, approved operational responses, guarded run records, feedback proposals, and recoverable state without implying automatic external execution.

## Compounding structure

- Required combos: `long-horizon-core`, `signal-to-decision-loop`
- Conditional combos: `capability-readiness`, `automation-control`, `guarded-automation-loop`, `evidence-to-evolution-loop`, `mission-aware-operating-loop`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. When the mission spans decisions, evidence, or resumption across time, activate `mission-aware-operating-loop` before selecting an operational response.
3. Execute required combos in deterministic dependency order.
4. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
5. Apply the loop's quality gate: observed is not verified, missing retrieval is not disproof, and contradiction remains visible.
6. Synthesize final mission deliverable `ADAPTIVE_OPERATIONS_MISSION_RECORD.md`.

## Mission-aware operating spine

When activated, the execution record carries:

```text
MISSION → CONTEXT → OPTIONS → IMPACT → ACTION → OUTCOME
                                      ↓
                         VERIFY → LEARN → STRENGTHEN ↺
```

The Combo supplies the decision-and-learning spine; this Mega owns adaptive-operations coordination. The resulting mission record must preserve the selected route, impact forecast, outcome state, evidence references, learnings, strengthening changes, and exact resumption point. It never authorizes external mutation by implication.

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
