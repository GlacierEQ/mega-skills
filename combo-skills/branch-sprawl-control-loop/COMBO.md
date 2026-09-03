---
id: branch-sprawl-control-loop
display_name: Branch Sprawl Control Loop
schema: ../../schemas/combo-skill.schema.json
version: 0.1.1
status: candidate
---

# Branch Sprawl Control Loop

## Purpose and selection

Use this Combo when branch count is growing faster than useful work is integrating, when automation leaves merged refs behind, or when several related branches need to be reduced into a smaller set without throwing away divergent commits.

Do **not** use it as a blanket stale-branch deleter. Age and naming are routing signals only. Unique commits, open pull requests, missing comparison evidence, protected refs, and explicit long-lived branches remain preserved unless a separate evidence-backed integration decision resolves them.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `branch-lifecycle-intelligence` | Repository branch/PR state and lifecycle policy | Inventory, lifecycle classifications, branch families, cleanup candidates | Only merged or zero-ahead refs may be automatic delete candidates; incomplete evidence fails closed. |
| 2 | `pr-babysit` | ACTIVE branches and open PR lineage | PR health/blocker record | Live review work is distinguished from lifecycle residue. |
| 3 | `finishing-a-development-branch` | Verified completion state and healthy PR/integration evidence | Merge/PR/keep/cleanup integration decision | Development work receives an explicit closure route rather than spawning another unbound branch. |
| 4 | `branch-lifecycle-intelligence` | Post-integration repository state | Final cleanup plan and hashed lifecycle receipt | Every deletion is re-proven immediately before mutation; divergent siblings remain preserved or routed to consolidation review. |

## Dynamic control law

No member may treat an earlier classification, branch-family lead, preservation decision, or cleanup candidate as permanently valid. Each handoff must reassess the current repository state and downstream impact.

The loop optimizes dynamically for the best current outcome:

1. preserve and harvest useful divergence,
2. integrate stronger capabilities into the surviving system,
3. deny destructive action when evidence or impact is uncertain,
4. retire only work that remains redundant after fresh re-evaluation,
5. reverse or block a prior recommendation whenever new evidence changes the result.

## Handoff contract

The first lifecycle pass is an evidence map, not permission to delete. ACTIVE branches pass to `pr-babysit`; verified completion passes to `finishing-a-development-branch`; the integration result returns to `branch-lifecycle-intelligence` for a fresh post-merge classification.

The second lifecycle pass must not reuse a stale pre-merge decision. It re-reads branch SHA, protection, open PR state, and merged/reachability evidence before any deletion.

## Branch-spread prevention law

New branch creation is a lifecycle decision, not a default side effect.

- Continue an existing branch only when the workstream is explicitly bound to that branch.
- Do not infer "same workstream" merely from similar branch names.
- If several branches are explicitly bound to the same workstream, stop creating more refs and route the family to consolidation.
- A merged workstream should close its branch lifecycle immediately.
- A new branch is justified when the workstream is genuinely independent, isolation is required, or the prior branch lifecycle is already closed.

## Compound output

**Artifact:** `BRANCH_SPRAWL_CONTROL_RECORD.json`, containing the initial inventory, active-PR health, integration closure decisions, family consolidation candidates, final lifecycle plan, deleted refs, preserved divergent refs, blocked refs, before/after branch counts, and integrity hashes.

**Ready for Mega integration when:** every automatic deletion has strong redundancy proof, every active/divergent branch has an explicit preservation or consolidation route, and future workstreams have an admission rule that prevents reflexive branch multiplication.
