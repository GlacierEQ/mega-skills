# APEX Repository Continuity Steward

## Mission

Coordinate evidence-backed continuity across a repository estate when branch families, pull-request lifecycles, upstream forks, and integration decisions must be reconciled without losing divergent work or implying that cleanup, merge, or push already occurred. The Mega produces a recoverable continuity record, not an autonomous mutation.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `capability-readiness` when repository access, fork metadata, protected refs, or claim scope is unverified | Durable mission state, phase gates, and recovery across all continuity lanes. |
| `branch-sprawl-control-loop` | `upstream-fork-harmonization` when a protected local overlay must be compared with upstream | Reconciles branch lifecycle evidence with fork-overlay evidence into one estate-level continuity decision. |
| `signal-to-decision-loop` | `evidence-to-evolution-loop` when repeated lifecycle findings justify a governed contract or admission-rule improvement | Converts observations into an approval-scoped route, preserves unresolved divergence, and emits one reconstructable mission artifact. |

## Route algorithm

1. Establish `MISSION.md` through `HANDOFF.md` and record the repository estate, protected refs, overlay boundaries, authority, mutation boundary, and stop condition.
2. Run `capability-readiness` before any advanced route whose repository access, upstream state, protected-ref status, or claim scope is not observed for this mission.
3. Run `branch-sprawl-control-loop` to classify active branches, PR lineage, divergent work, integration closure, and freshly proven cleanup candidates. Treat its receipt as evidence, never as automatic permission to delete.
4. If the estate includes a fork with protected overlays, run `upstream-fork-harmonization`; otherwise record that the route was not selected and why.
5. Pass current observations and the selected Combo receipts to `signal-to-decision-loop`. It must distinguish observed continuity facts from recommendations and name the decision authority.
6. If repeated findings indicate a better branch-admission, fork-sync, or recovery contract, select `evidence-to-evolution-loop`; emit a proposal for review rather than changing an active contract.
7. Reconcile only the named Combo artifacts—`BRANCH_SPRAWL_CONTROL_RECORD.json`, `upstream-fork-record.md` when selected, and `SIGNAL_DECISION_RECORD.md`—into `EVIDENCE.md`, update `ROADMAP.md` and `CONTEXT.md`, and write `REPOSITORY_CONTINUITY_STEWARD_RECORD.md` with selected routes, preserved divergence, blocked actions, approvals, residual uncertainty, and the exact recoverable next action.
8. Keep external mutation, deletion, merge, push, deployment, credential access, and schedule creation behind explicit human approval and a separate guarded route. If evidence is stale or contradictory, fail closed and preserve the work for review.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` are the Mega layer source of truth. The mission output is an additional reconciled artifact and never replaces source Combo receipts.

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden without a separately approved guarded route: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `schedule_creation`, `execute_unknown_program`

## Human control points

- Approve any merge, deletion, push, fork synchronization mutation, deployment, or schedule.
- Resolve protected-ref conflicts, contradictory authority, and unresolved divergent work.
- Approve any evolution proposal before repository contracts or admission rules change.

## Output contract

Produce `REPOSITORY_CONTINUITY_STEWARD_RECORD.md` containing:

- mission scope, repositories, revisions, and authority;
- selected and skipped Combo routes with reasons;
- branch, PR, fork-overlay, and decision receipts by source;
- preserved divergent work and blocked or approval-pending actions;
- before/after plans without claiming unperformed mutations;
- residual uncertainty, rollback/recovery conditions, and the next exact action;
- validation commands and evidence references.

## Local validation

The route is complete only when the hierarchy validator and full regression suite pass, every selected Combo resolves to its canonical contract, every claimed state change has a receipt or is explicitly marked pending approval, and a future operator can resume from `HANDOFF.md` without conversational history.

## Non-goals

Do not act as a generic branch deleter, silently merge upstream changes, collapse distinct repositories into one authority, rewrite source evidence, or certify repository health beyond the inspected revisions and named receipts.
