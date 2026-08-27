# Operating Protocol

Use this reference to turn a broad mission into verifiable, low-drift work. The objective is not maximal ceremony; it is to make the next useful action obvious, bounded, evidenced, and recoverable.

## Phase model

| Phase | Objective | Gate to pass before advancing | Typical evidence |
|---|---|---|---|
| 0. Intake and safety | Understand the request, authority, sensitivity, and constraints. | Mission is actionable; required clarification or approval is obtained or explicitly pending. | Mission contract; approval record; risk note. |
| 1. Discovery | Reduce material uncertainty and collect canonical inputs. | Key unknowns are answered, bounded, or registered as risks. | Source register; inspected files; assumptions. |
| 2. Strategy | Choose approach, specialist skills, architecture, and success tests. | Approach is feasible, constraints are honored, and acceptance tests are testable. | Decision records; roadmap; implementation or research plan. |
| 3. Production | Create the requested artifacts in dependency order. | Each artifact meets its local acceptance test. | Source files; drafts; generated assets; analyses. |
| 4. Integration | Reconcile artifacts, claims, formats, and interfaces into one coherent result. | No unresolved material contradiction or incompatible handoff remains. | Integrated deliverable; reconciliation notes. |
| 5. Verification | Independently test, inspect, or review the result against the mission. | All acceptance criteria pass or exceptions are explicit and approved. | Test results; QA checklist; review notes. |
| 6. Delivery and recovery | Deliver clearly and preserve a truthful closing or resume state. | Requested output is accessible, limits are stated, and recovery instructions are accurate. | Delivery package; final handoff; evidence trace. |

Use phases in order unless the roadmap records why an exception is safe. In a short Expedition run, phases may be compacted but their gates must remain visible.

## Atomic chunk standard

An atomic chunk produces one meaningful result that can be reviewed without retaining the whole task in active context.

| Attribute | Standard |
|---|---|
| Objective | One verb–object statement, such as “validate the dataset schema” or “draft the executive summary.” |
| Boundary | A defined start state and stopping point; no uncontrolled exploration. |
| Inputs | Canonical artifact paths, source IDs, constraints, and settled decisions only. |
| Output | A named file, tested change, decision record, or verified conclusion. |
| Acceptance test | A concrete inspection, test, comparison, source check, or approval. |
| Authority | What may be decided inside the chunk and what must be escalated. |
| Evidence | Artifact path, source ID, test output, or reviewer result recorded on completion. |
| Follow-through | Required updates to roadmap, evidence, context, and handoff. |

Split a chunk when it would require unrelated skills, has more than one independent output, cannot be verified locally, needs too many raw inputs, or carries an irreversible action mixed with exploratory work.

## Risk-first ordering

Order work by dependency and expected value of information, not by superficial convenience. Test or research first when it could invalidate an architecture, key assumption, data source, budget, safety premise, or user outcome. Defer low-risk polish until the core path works.

Use this lightweight risk register in `ROADMAP.md`:

| Risk | Probability | Impact | Early signal | Mitigation | Contingency | Owner |
|---|---|---|---|---|---|---|

Escalate to the user when a decision changes the agreed scope, cost, confidentiality, external impact, or feasibility; when a critical source or approval is missing; or when more work cannot meaningfully reduce a material uncertainty.

## Decision record format

Record a decision when it meaningfully constrains later work or prevents repeated deliberation. Avoid recording routine choices.

| Field | Content |
|---|---|
| ID and date | Stable identifier and time-sensitive context. |
| Decision | The selected course of action. |
| Trigger | The question or event requiring a choice. |
| Evidence | Canonical source IDs, tests, or artifact references. |
| Alternatives | Viable options considered, with concise rejection reason. |
| Confidence | High, medium, or low, plus the source of uncertainty. |
| Consequences | Dependencies, risks, or work that changes because of the choice. |
| Review trigger | The event or date that requires reconsideration. |

## Verification ladder

Choose the strongest practical verification method suited to the claim. Do not substitute a weaker check without recording the limitation.

| Claim type | Preferred verification |
|---|---|
| Factual statement | Read a primary or authoritative source; cross-check material claims. |
| Data transformation | Reproducible calculation, schema check, reconciliation, and spot audit. |
| Code or system behavior | Automated tests, build or lint checks, then relevant runtime or visual inspection. |
| Written deliverable | Requirements trace, factual review, coherence edit, and format inspection. |
| Design or media artifact | Inspect the actual rendered output against stated criteria. |
| Operational action | Confirm target, authority, exact parameters, successful execution, and post-condition. |

## Quality gate questions

At every phase boundary, answer these questions in writing if the work is Frontier-scale:

1. **Complete:** Are all planned outputs and dependencies for this phase present?
2. **Correct:** Did the stated test or evidence support the important claims?
3. **Consistent:** Do artifacts, decisions, and terminology agree across workstreams?
4. **Traceable:** Can a reviewer map requirements and claims to sources or test outputs?
5. **Usable:** Is the result in the requested format, location, and level of clarity?
6. **Safe:** Were authority, privacy, approval, policy, and irreversible-action constraints respected?
7. **Recoverable:** Can a fresh operator identify the exact next action from the state files?

Do not mark a phase complete if a material answer is “no.” Convert the deficiency into a planned chunk, blocker, or user escalation.

## Stop conditions

Stop discovery when the mission’s decision threshold is met, not when every possible source has been read. Stop production when acceptance criteria have passed, not when additional embellishment only marginally improves the work. Stop and escalate when required authority is absent, evidence cannot support a key claim, a constraint conflicts with the desired outcome, or the next action is sensitive or irreversible and approval is required.
