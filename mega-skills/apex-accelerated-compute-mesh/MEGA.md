# APEX Accelerated Compute Mesh

## Mission

Hardware-accelerated machine learning control plane: coordinates neural network quantization on Apple Neural Engine, latent attention routing on DeepSeek MoE, and compiler graph execution across AWS Trainium and xAI Colossus superclusters.

## Compounding structure

- Required combos: `long-horizon-core`, `hardware-accelerated-inference`
- Conditional combos: `capability-readiness`, `polyglot-systems-verification`, `automation-control`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
4. Synthesize final mission deliverable `ACCELERATED_COMPUTE_MISSION_RESULT.md`.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `ACCELERATED_COMPUTE_MISSION_RESULT.md`

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `escalate_critical_anomalies`

## Output contract

Produce `ACCELERATED_COMPUTE_MISSION_RESULT.md` upon mission completion.

## Local validation

100% test assertions and receipts verify.

## Non-goals

Unbounded external state mutations.
