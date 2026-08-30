---
name: automation-control
description: 'Combo Skill: Automation Control. Reusable capability chain.'
---

# Automation Control

Use this Combo when a mission includes a trigger, recurrence, background process, or external integration. It composes GlacierEQ’s contract, plan, evidence, and quality Skills with the appropriate external architecture, configuration, and runtime procedures.

| Order | Member | Compound contribution |
|---:|---|---|
| 1 | `mission-contract` | States desired effects, user controls, approvals, and stop conditions. |
| 2 | `automation-and-scheduling` | Assesses trigger, frequency, architecture, and scaling constraints. |
| 3 | `roadmap-builder` | Orders implementation, configuration, failure-path, and verification work. |
| 4 | `manus-config` / `persistent-computing` | Applies only necessary controls or runtime assessment after route choice. |
| 5 | `evidence-register` + `quality-gate` | Records proof and accepts the automation only when safety and failure conditions are explicit. |

The output is `automation-control-record.md`: trigger map, idempotency rule, effect/approval boundary, configuration status, monitoring plan, and verification result. Do not activate external effects until the gate passes.
