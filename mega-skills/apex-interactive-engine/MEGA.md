# APEX Interactive Engine

## Mission

Interactive 2D/3D media engineering, WebGL canvas rendering, procedural generative mathematics, and low-latency interactive experiences.

## Compounding structure

- Required combos: `long-horizon-core`, `interactive-media-3d-pipeline`, `closed-loop-code-repair`
- Conditional combos: `capability-readiness`, `web-build-foundation`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `INTERACTIVE_ENGINE_RECORD.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `INTERACTIVE_ENGINE_RECORD.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `INTERACTIVE_ENGINE_RECORD.md` upon mission completion.

## Local validation

Render loop maintains 60 FPS under simulated load with zero memory leaks.

## Non-goals

Direct native GPU firmware manipulation or audio driver overrides
