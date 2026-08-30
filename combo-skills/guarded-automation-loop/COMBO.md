---
id: guarded-automation-loop
display_name: Guarded Automation Loop
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Guarded Automation Loop

## Purpose and selection

Use this Combo after a mission identifies a repeating or event-triggered need and a suitable automation architecture has been assessed. Do **not** use it to create schedules, poll services, call external APIs, or apply changes without the relevant approval and preflight.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `capability-admission` | Automation intent and candidate route | Admission decision | Effects, approval, and fallback are explicit. |
| 2 | `resource-preflight` | Prerequisite inventory | Preflight record | Required access and resources have observed status. |
| 3 | `automation-and-scheduling` | Approved mission facts | Architecture options | Trigger, frequency, determinism, and runtime are assessed. |
| 4 | `work-packet` | Chosen architecture | Guarded execution packet | Idempotency, boundaries, and verification are explicit. |
| 5 | `quality-gate` | Execution evidence or proposal | Run gate | Result is accepted, blocked, or escalated. |
| 6 | `handoff-record` | Gate result and state | Recovery record | Retry and next review conditions are exact. |

## Handoff contract

Automation architecture is not an authorization to act. The preflight passes observed resource status to the architecture assessment; the work packet requires an explicit effect boundary and failure path; the quality gate returns a pass, block, or escalation record. Any missing approval or inaccessible dependency returns to capability admission with a safe fallback.

## Compound output

**Artifact:** `GUARDED_RUN_RECORD.md`, containing trigger class, approved route, preflight status, execution authority, idempotency rule, observed result, failure classification, next review, and handoff.

**Ready for Mega Skill integration when:** the intended effect, approval boundary, recovery path, and verification result are recorded; no external effect is represented as completed without actual evidence.
