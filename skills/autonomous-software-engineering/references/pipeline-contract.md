# Autonomous Engineering Pipeline Contract

Use this contract to keep a long-running engineering mission resumable and auditable.

## Mission capsule

| Field | Required content |
|---|---|
| Mission ID | Stable identifier for the request and recovery point |
| Objective | Desired outcome and measurable acceptance criteria |
| Repository state | Repository, branch, last verified commit, clean/dirty status |
| Current phase | Frame, inspect, map, plan, implement, test, secure, profile, integrate, gate, review, release, observe |
| Scope | Approved roots, exclusions, non-goals, and mutation boundary |
| Assumptions | Explicit assumptions with confidence and validation plan |
| Evidence | Tests, scans, profiles, graphs, receipts, reviews, and source references |
| Open risks | Severity, owner, mitigation, and expiry where applicable |
| Changed files | Files changed in the current bounded batch |
| Next action | One concrete next step and its close condition |
| Recovery | Command or procedure that resumes safely |

## Handoff contract

Every stage-to-stage handoff must include:

1. Sender and receiving skill or owner.
2. Input artifact and its version or commit.
3. Expected output artifact and schema.
4. Acceptance test or close condition.
5. Known limitations and unresolved risks.
6. Failure route, rollback, or escalation owner.

A handoff is not complete when a file merely exists. It is complete when the receiver can validate the artifact, understand its provenance, and either proceed safely or reject it with evidence.

## Gate states

- **READY:** inputs and authorization are present; stage may begin.
- **ACTIVE:** stage is executing within its bounded scope.
- **VERIFIED:** close condition passes with recorded evidence.
- **BLOCKED:** a required input, safety condition, or quality gate fails; do not proceed silently.
- **ESCALATED:** human or owner decision is required.
- **ROLLED_BACK:** the batch was reverted and failure evidence preserved.

Keep only the current state and decision-relevant evidence in the capsule. Store detailed logs, raw profiles, scan output, and graph data as linked artifacts.
