# Swarm Protocol

Use a swarm only when distinct, independent workstreams can reduce elapsed time, broaden coverage, or improve review quality. A swarm is a coordination pattern, not a license for unbounded duplication. In a sequential environment, perform the same roles in order and do not represent that as simultaneous execution.

## Role model

| Role | Responsibility | Must return | Must not do |
|---|---|---|---|
| **Integrator** | Own the mission, roadmap, interfaces, conflict resolution, quality gates, and final result. | Updated state, integrated artifact, unresolved decisions. | Delegate accountability or silently blend conflicting findings. |
| **Scout** | Reduce a defined uncertainty through bounded research, inspection, or reconnaissance. | Evidence register entries, conclusion, uncertainty, and recommended next action. | Produce broad unstructured notes or decide outside its authority. |
| **Specialist** | Create or analyze one bounded artifact using a domain skill. | Artifact, acceptance-test result, evidence pointer, and handoff note. | Expand scope or change mission-level decisions. |
| **Verifier** | Independently check a stated claim, artifact, or acceptance criterion. | Pass/fail result, method, evidence, limitations, and remediation request. | Validate its own unreviewed work when independence is material. |
| **Red team** | Seek high-impact omissions, contradictions, safety issues, and failure modes. | Prioritized findings with reproducible basis. | Create speculative objections without an observable trigger. |

The Integrator retains final responsibility for coherence and truthfulness. Combine roles only when the task is low-risk or the environment cannot support separation; record the reduced independence as a limitation.

## Decide whether to split work

Split work only when these conditions hold:

| Check | Split if the answer is yes |
|---|---|
| Independence | Can each workstream proceed from stable shared inputs without waiting for another’s output? |
| Distinct value | Does each workstream cover different sources, artifacts, hypotheses, or competencies? |
| Integration readiness | Can outputs be reconciled through a defined schema or acceptance test? |
| Cost discipline | Is the expected value greater than the coordination and context cost? |
| Authority safety | Can each workstream act without sensitive, irreversible, or mission-changing decisions? |

Do not split tasks that depend on a single evolving design, require shared mutable state without a clear protocol, or would merely create redundant summaries.

## Work packet

Use one packet per role or workstream. Persist the packet in `ROADMAP.md` or as an adjacent task file when it becomes long.

```markdown
# Work packet: <ID>

## Objective
<One bounded result.>

## Context capsule
<Only the constraints, decisions, artifact paths, and source IDs needed for this work.>

## Inputs
- <Canonical input 1>
- <Canonical input 2>

## Method and authority
<Required skill/procedure; allowed decisions; escalation boundaries.>

## Deliverable
<Exact file, decision record, evidence table, or concise finding format.>

## Acceptance test
<Concrete verification method and pass condition.>

## Return format
1. Result.
2. Evidence and artifact paths.
3. Assumptions and limitations.
4. Conflicts, blockers, or escalation needed.
5. State updates required.
```

Never give a worker a raw, unconstrained instruction such as “research everything” or “make it great.” Convert broad intent into a decision question, source scope, artifact boundary, and acceptance test.

## Integration protocol

1. **Register returns.** Add each artifact and claim to `EVIDENCE.md` and record completion status in the roadmap.
2. **Normalize.** Compare terminology, units, versions, assumptions, source quality, formats, and acceptance criteria.
3. **Resolve conflicts.** Prefer authoritative evidence, the mission contract, reproducible tests, and the governing domain skill. If evidence remains balanced, preserve the uncertainty and escalate the decision rather than silently choosing.
4. **Check interfaces.** Verify that one workstream’s output satisfies the next workstream’s input contract.
5. **Run an integration test.** Inspect the combined artifact or execute the end-to-end acceptance test; local success is not enough.
6. **Update durable state.** Record accepted findings, rejected outputs, decision rationale, new risks, and the exact next action.

## Avoid context collapse

Do not merge raw outputs wholesale. Require each role to return a concise result with evidence pointers, then preserve canonical artifacts separately. The Integrator should load only the pieces needed to reconcile a decision or interface.

When a workstream discovers information that changes the mission, constraints, or an upstream decision, pause dependent work, update `CONTEXT.md` and `ROADMAP.md`, and reissue affected packets. Continuing with stale assumptions is a coordination failure.

## Swarm quality controls

| Control | Apply when | Action |
|---|---|---|
| Independent review | Errors would materially affect the user. | Assign a verifier who did not author the artifact. |
| Source triangulation | A conclusion rests on external or disputed facts. | Compare independent authoritative sources and state residual uncertainty. |
| Interface test | Multiple artifacts must interoperate. | Execute or inspect the combined path, not only components. |
| Red-team pass | The work is high-stakes, externally visible, or safety-sensitive. | Search explicitly for omissions, contradictions, misuse, and failure modes. |
| User approval gate | Scope, cost, external action, or sensitivity changes. | Stop at the gate and request the specific decision or confirmation. |

## Handoff contract

A role’s work is not complete until the next role can start without reconstructing the assignment. Require the return format, the artifact location, test outcome, source or version identifiers, unresolved concerns, and the required state updates. If any of those are missing, return the packet for clarification or mark it incomplete.
