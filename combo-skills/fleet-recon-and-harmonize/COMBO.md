---
id: fleet-recon-and-harmonize
display_name: Fleet Recon and Harmonize — Harmonious Merge Route
schema: ../../schemas/combo-skill.schema.json
version: 0.2.0
status: active
---

# Fleet Recon and Harmonize — Harmonious Merge Route

## Purpose and selection

Use this Combo Skill when branches across one or more repositories must be converged without discarding the living `main` baseline. It turns raw divergence into a value-preservation plan: identify unique beneficial behavior, selectively integrate it into `main`, verify it there, and retire only refs whose value has been preserved or explicitly rejected.

Do **not** use it for a simple local commit or single-file edit. Do **not** use it to replace `main`, bulk-merge a branch inventory, or preserve known secret-bearing history.

## Incremental value

The member skills provide scope boundaries, branch analysis, and validation. This Combo adds the durable handoff from branch inventory to an evidence-backed **Harmonious Merge Audit**, with explicit safety gates for branch retirement and credential-exposure remediation.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Define repository scope, canonical baseline, approvals, and security constraints | Target repo scope | `MISSION.md` | `main`, ref scope, checks, and non-destructive boundaries are explicit |
| 2 | `fleet-git-harmonizer-core` | Skill | Yes | Analyze branch value, plan selective integration, and create dispositions | `MISSION.md` and repository path | `harmonious-merge-audit.json` | Every branch/tag has an evidence-backed disposition |
| 3 | `quality-gate` | Skill | Yes | Verify accepted changes on `main` and validate retirement receipts | Main test results and audit | Gate record | Required checks pass on `main`; no unapproved ref deletion |

## Ordered execution

1. **Mission boundary — `mission-contract`:** establish `main` as the canonical baseline; enumerate in-scope branches/tags; declare validation commands, security constraints, and approval boundaries.
2. **Harmonious analysis and integration — `fleet-git-harmonizer-core`:** compare each ref semantically to `main`, group overlaps by capability, produce a disposition for every ref, and integrate only approved, minimal, compatible behavior.
3. **Quality gate — `quality-gate`:** confirm all required validation passes on the updated `main`; confirm the audit records preservation or rejection evidence for every retirement candidate.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `fleet-git-harmonizer-core` | Repository scope, baseline SHA, ref inventory, branch-retention and security rules | Verified semantic divergence manifest and disposition plan | Mission owner | Scope, baseline, and safety gates are explicit |
| `fleet-git-harmonizer-core` | `quality-gate` | Updated `main`, integration provenance, test outputs, ref dispositions | Verified gate record and retirement-readiness decision | Execution owner | Tests green on `main`; all candidates accounted for |

## Security and ref-retirement gates

- `main` must remain the verified canonical result. It may not be reset, deleted, or replaced by a candidate branch.
- A branch can be retired only after its distinct value is verified on `main` or explicitly rejected, its dependencies are clear, and the configured human approval is recorded.
- Do not create tags, backup refs, or archive branches that preserve known credential-bearing history.
- If a tracked credential is discovered: rotate/revoke first, finish the disposition plan, then route any all-ref history rewrite through separately authorized administration. This Combo does not authorize force-pushes or history rewrites.

## Evidence, state, and quality gates

Record baseline and final `main` SHAs, complete ref inventory, per-ref dispositions, preserved behavior and source commits, test receipts, required approvals, security findings, and any blocked follow-up in the evidence register. Update active state after every repository batch.

The Combo is complete only when every scoped branch/tag has a disposition, all accepted integrations validate on `main`, and every proposed deletion remains pending the required approval or has a recorded completed receipt.

## Compound output

**Artifact:** `harmonious-merge-audit.json`

**Ready for Mega Skill integration when:**

1. `main` is preserved and has passed required checks after accepted integrations.
2. Every scoped ref has an evidence-backed disposition.
3. No branch is deleted merely to reduce clutter.
4. Any credential exposure is either escalated through the rotation/history-rewrite gate or explicitly confirmed resolved.
