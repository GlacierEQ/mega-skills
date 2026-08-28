# APEX Safe Change Orchestrator Mega Skill

## Mission

Coordinate a recoverable code or configuration change from uncertain scope through evidence-backed decision, bounded repair or change execution, verification, and handoff. This Mega Skill does not deploy, force-push, or create external effects; it orchestrates the approved change route and records exactly what occurred.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `recon-and-map` when repository role or change scope is unclear | Sets a verified source-of-truth and non-destructive boundary. |
| `long-horizon-core` | `capability-readiness` before a specialized repair or automation route | Confirms tools, workspace, tests, and authority before selection. |
| `long-horizon-core` | `signal-to-decision-loop` when findings require a change choice | Preserves alternatives, evidence, and decision authority. |
| `long-horizon-core` | `closed-loop-code-repair` when a bounded failing-test repair route is admitted | Integrates repair evidence and quality results into the mission record. |
| `long-horizon-core` | `guarded-automation-loop` only after separate approval for recurring execution | Maintains idempotency, effect, and recovery controls. |

## Route algorithm

1. Start `long-horizon-core` and define repository revision, allowed paths, test command, maximum change boundary, approval state, and rollback/recovery route.
2. Use `recon-and-map` whenever source-of-truth, scope, or ownership is uncertain; do not change an unverified target.
3. Run `capability-readiness` before selecting repair tools, runtime-dependent checks, or any route with unverified prerequisites.
4. Convert findings into `SIGNAL_DECISION_RECORD.md`; select the minimal approved change route and preserve alternatives.
5. If a failing-test repair route is admitted, use `closed-loop-code-repair`; accept only its named execution record and independently gate the result.
6. Use `guarded-automation-loop` only for an approved recurring implementation path; otherwise retain a manual, reviewable work packet.
7. Reconcile change scope, evidence, tests, approval, recovery, and next action into `SAFE_CHANGE_MISSION_RECORD.md` and `HANDOFF.md`.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` remain the source of truth. The final mission artifact is `SAFE_CHANGE_MISSION_RECORD.md`.
