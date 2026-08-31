---
id: mission-aware-operating-loop
display_name: Mission Aware Operating Loop
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Mission-Aware Operating Loop

## Purpose and selection

Use this Combo when a mission needs more than a one-time decision: the route must preserve the operator's purpose, carry context forward, compare meaningful options, forecast impact, record the action, verify the outcome, and convert what was learned into a stronger next state. Use it especially when the work spans sessions, clouds, repositories, tools, or changing evidence.

Do **not** use it to inflate a simple bounded response, to certify a claim merely because it was recorded, or to treat an unsearched source as disproven.

## Incremental value

This Combo adds the connective tissue that existing Skills do not own individually. It makes the decision path recoverable and keeps aspiration, current implementation, observed outcome, and verified result distinct. It does not copy the methods of its member Skills and does not grant autonomous authority.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `mission-contract` | Operator mission and constraints | Mission boundary | Outcome, scope, non-goals, authority, and stop condition are explicit. |
| 2 | `context-capsule` | Mission, prior state, and relevant retrieval map | Working context | Known context, operator report, retrieval status, and unresolved questions remain distinct. |
| 3 | `evidence-register` | Sources, observations, tests, and artifacts | Evidence trace | Observed, derived, assumed, unknown, and contradicted states are separated. |
| 4 | `roadmap-builder` | Mission boundary, context, evidence, and candidate routes | Options and next route | Alternatives, dependencies, impact, and verification conditions are explicit. |
| 5 | `quality-gate` | Proposed action, evidence, and acceptance criteria | Outcome gate | The result is pending, observed, verified, contradicted, blocked, or escalated—never silently upgraded. |
| 6 | `handoff-record` | Gate result, learnings, and next-state changes | Recovery and strengthening record | A future operator can resume from the exact next action and review trigger. |

## Execution loop

```text
MISSION → CONTEXT → OPTIONS → IMPACT → ACTION → OUTCOME
                                      ↓
                         VERIFY → LEARN → STRENGTHEN ↺
```

The loop is a coordination contract. The member Skills own their local artifacts; this Combo owns their ordering, the phase transitions, the explicit impact forecast, and the return of verified learning to the next state.

## Retrieval and evidence law

The following states must remain distinct:

- `known_from_context`
- `operator_reported`
- `retrieval_pending`
- `not_searched`
- `searched_found`
- `searched_not_found`
- `unavailable`
- `contradicted`

`searched_not_found` is a search result, not factual disproof. `contradicted` requires an identified conflict and a source or observation that makes the conflict real. Missing from the active window is not missing from the wider record.

## Handoff contract

The mission contract defines the boundary; the context capsule identifies what is already known and where retrieval should occur; the evidence register binds material observations to sources; the roadmap turns them into options and a bounded action; the quality gate records the actual outcome state; the handoff preserves learning, strengthening, and the next review trigger.

## Compound output

**Artifact:** `MISSION_OPERATING_LOOP_RECORD.md`, containing mission, context, options, impact forecast, action, outcome state, evidence/retrieval state, verification, learnings, strengthening changes, and exact resumption point.

**Ready for Mega Skill integration when:** the record can be resumed without raw conversation history, no material claim outruns its evidence state, and the next route is explicit.
