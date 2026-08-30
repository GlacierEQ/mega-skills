---
name: capability-readiness
description: 'Combo Skill: Capability Readiness. Reusable capability chain.'
---

# Capability Readiness

## Purpose and selection

Use this Combo before choosing an advanced route whose dependency inventory, environment, access, validation evidence, or claim scope is not already verified for the active mission. Do **not** use it as a substitute for the specialist route’s actual domain validation.

## Incremental value

The individual members can admit a capability, check a resource, or calibrate a claim. This Combo adds a single repeatable gate that prevents a Mega Skill from selecting a strongly described but unready route.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `capability-admission` | Mission intent and candidate capability | Admission criteria | Required prerequisites and fallback are explicit. |
| 2 | `resource-preflight` | Admission criteria and environment scope | `RESOURCE_PREFLIGHT.md` | Every required resource has an observed status. |
| 3 | `claim-calibration` | Capability claims and preflight evidence | `CLAIM_BOUNDARIES.md` | Wording matches the verified environment and evidence. |
| 4 | `quality-gate` | Admission, preflight, and claim artifacts | Readiness gate record | A route is accepted only when evidence and scope align. |

## Handoff contract

`capability-admission` passes its named prerequisites to `resource-preflight`. `resource-preflight` passes observed resource status—not configuration assumptions—to `claim-calibration`. `quality-gate` accepts the route only when the admission decision, preflight, and scoped claims agree. A failed resource check returns to the admission owner with a safe fallback.

## Compound output

**Artifact:** `CAPABILITY_READINESS_RECORD.md`, containing the mission-specific admission decision, preflight status, approved capability claims, unresolved gaps, and fallback route.

**Ready for Mega Skill integration when:** the route is either explicitly admitted for the mission or safely blocked; every material claim has evidence-matched scope; and no unverified dependency remains hidden behind an active label.
