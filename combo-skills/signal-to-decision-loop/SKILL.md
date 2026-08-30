---
name: signal-to-decision-loop
description: 'Combo Skill: Signal to Decision Loop. Reusable capability chain.'
---

# Signal to Decision Loop

## Purpose and selection

Use this Combo when a new signal—monitoring result, review finding, user report, scheduled checkpoint, or failed test—may require a decision. Do **not** use it to automatically make or execute a change; it produces a decision-ready record only.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `mission-contract` | Signal and mission boundary | Decision scope | Authority, impact, and stop condition are explicit. |
| 2 | `evidence-register` | Observations and source context | Evidence trace | Facts, tests, and unknowns are separated. |
| 3 | `claim-calibration` | Candidate conclusion and evidence | Scoped conclusion | Wording matches observed evidence. |
| 4 | `roadmap-builder` | Accepted conclusion | Recommended next route | Dependencies, choices, and verification are explicit. |
| 5 | `quality-gate` | Decision record | Decision gate | A reviewer can reproduce the recommendation. |

## Handoff contract

The evidence register accepts only observed signals and links. Claim calibration may narrow or block a conclusion but cannot invent missing evidence. The roadmap receives only a scoped conclusion and emits options or an exact next chunk. The quality gate accepts a decision only when authority and residual uncertainty are recorded.

## Compound output

**Artifact:** `SIGNAL_DECISION_RECORD.md`, including source signal, classification, evidence, risk/impact, recommended route, alternatives, decision authority, and next review trigger.

**Ready for Mega Skill integration when:** the record distinguishes observation from recommendation, requires no raw history to understand, and names an approved or pending next action.
