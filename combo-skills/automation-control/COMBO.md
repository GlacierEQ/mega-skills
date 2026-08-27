# Automation Control

## Purpose

Convert an automation request into an approved execution architecture with an explicit trigger, data boundary, control-plane configuration, reliability plan, and runtime suitability assessment.

## Members and order

1. **`far-away-party-core`** frames the mission, constraints, approvals, acceptance criteria, and evidence requirements.
2. **`automation-and-scheduling`** assesses trigger, frequency, decision complexity, and growth risk.
3. **`manus-config`** inspects or changes only the necessary connector, project, or schedule controls after scope is clear.
4. **`persistent-computing`** determines whether persistent runtime conditions are necessary and viable.

## Handoff contract

| Boundary | Required input | Output | Validation |
|---|---|---|---|
| Mission → automation assessment | Trigger intent, latency expectation, inputs, outputs, user control needs | Architecture decision | At least two viable approaches and their tradeoffs are stated when architecture is not obvious. |
| Architecture → configuration | Chosen route, approved integrations, actor boundary | Configuration change plan | Only necessary controls are in scope; no secrets are copied into records. |
| Configuration → runtime assessment | Expected frequency, state needs, tooling, resource needs | Runtime suitability record | Persistent hosting is proposed only when the workload requires it. |

## Compound artifact

`automation-control-record.md` contains the trigger map, idempotency behavior, failure path, monitoring evidence plan, approval boundary, and first verification run.

## Non-goals

Do not treat a scheduled job as an excuse to avoid architecture analysis. Do not activate external effects without the required user approval.
