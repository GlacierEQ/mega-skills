# APEX Adaptive Operations Mega Skill

## Mission

Coordinate an evidence-backed operational response when changing signals may require a decision, a guarded recurring route, or a follow-on capability-improvement proposal. This Mega Skill remains bounded: it plans and governs the response; it does not activate an external effect without a separately approved execution route.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `capability-readiness` before any advanced route | Maintains mission-wide readiness, state, and recovery. |
| `long-horizon-core` | `signal-to-decision-loop` when a signal may change the plan | Reconciles decision records with durable mission state. |
| `long-horizon-core` | `automation-control` and `guarded-automation-loop` only after architecture and approval exist | Coordinates guarded run records, evidence, and recovery across repeated cycles. |
| `long-horizon-core` | `evidence-to-evolution-loop` when repeated evidence justifies improvement | Preserves an improvement proposal without silently changing active behavior. |

## Route algorithm

1. Initialize durable state using `long-horizon-core` and define the signal, authority, stop condition, and delivery boundary.
2. Run `capability-readiness` whenever the candidate route has unverified prerequisites, access, runtime, data, or claim scope.
3. Convert each material signal into `SIGNAL_DECISION_RECORD.md`; select no action until the decision record names its authority and evidence.
4. If recurring or event-driven execution is appropriate, assess architecture with `automation-control`, obtain required approval, then produce `GUARDED_RUN_RECORD.md` through `guarded-automation-loop`.
5. Route repeated evidence through `evidence-to-evolution-loop` only as a review-ready proposal; do not self-modify the active mission.
6. Reconcile admitted route artifacts, approvals, results, failure state, and next review into `ADAPTIVE_OPERATIONS_MISSION_RECORD.md` and `HANDOFF.md`.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` record the mission source of truth. The mission artifact is `ADAPTIVE_OPERATIONS_MISSION_RECORD.md`.
