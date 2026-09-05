---
name: fleet-git-harmonizer-core
description: "Use for disciplined repository branch convergence: preserve main as the living baseline, selectively integrate unique beneficial behavior, validate it, and retire branches only after their value is accounted for."
---

# Fleet Git Harmonizer Core — Harmonious Merge Protocol

## Purpose

Converge a repository’s branch set without treating `main` as disposable. `main` is the living canonical baseline: it grows through verified, intentional integration. A branch is evidence to examine—not an instruction to merge wholesale, copy blindly, or delete casually.

Use this skill when branch sprawl, overlapping implementations, security remediation, or long-running development has made it unclear which branch behavior should survive.

## Inputs

- Repository scope and canonical baseline (default: `main`)
- Included branches and tags; any excluded refs must be named and justified
- Project validation commands and required checks
- Security constraints, including known exposed paths, credentials, and prohibited history-preservation actions
- Approval boundary for integration, branch retirement, and any irreversible history rewrite

## Invariants

1. **Preserve `main`.** Never replace, reset, delete, or treat `main` as a throwaway integration artifact.
2. **Preserve useful behavior, not branch shape.** Carry forward compatible, unique value in the smallest coherent form; a merge commit is optional, not the goal.
3. **No blind bulk operations.** Do not merge or retire branches solely because they are old, numerous, or superficially similar.
4. **Prove every decision.** Every retained, integrated, rejected, or retired branch needs an evidence-backed disposition.
5. **Security outranks convenience.** Never create a tag, backup ref, archive, release artifact, or copied branch that keeps known credential-bearing history reachable.
6. **Irreversible operations stay separate.** Force-pushes, tag deletion, branch deletion, and history rewrites require the stated approval boundary and a recovery/verification plan.

## Procedure

### 1. Establish the canonical baseline

- Read `main` first and record its immutable commit SHA, current checks, and protection status.
- Treat current `main` behavior as the comparison point. Do not choose a branch as a replacement merely because it has more commits or files.
- Fetch all reachable branch and tag refs before analysis. Record the ref inventory and its capture time.

### 2. Map each branch against `main`

For every non-baseline branch, analyze both commit divergence and semantic behavior. Build a disposition record containing:

- branch/ref and tip SHA;
- relationship to `main` (merged, redundant, divergent, or conflicting);
- unique beneficial behavior, if any, with affected components and tests;
- risks: regressions, duplicated capability, policy violations, generated noise, or secret exposure;
- one decision: `integrate`, `retain`, `retire-after-integration`, `retire-as-redundant`, or `hold-for-review`;
- evidence supporting that decision.

Do not infer value from branch names, commit count, novelty claims, or generated files. Inspect the actual behavior and tests.

### 3. Build a value-preservation plan

- Group overlapping branches by capability rather than processing them in arbitrary creation order.
- Identify the minimum changes needed to bring each approved benefit to `main`.
- Reconcile conflicts deliberately against the baseline design. Prefer a new small implementation when it preserves the useful behavior more safely than copying historical code.
- Record provenance: source branch, source commit(s), preserved behavior, intentional deviations, and validation planned.
- Mark branches with no remaining distinct benefit as retirement candidates—never delete them yet.

### 4. Integrate incrementally into `main`

- Apply one coherent capability group at a time through the repository’s approved integration path.
- Run focused tests after each group and the complete validation suite before accepting the resulting `main` state.
- Verify the resulting behavior on `main`; passing a branch’s old tests alone is insufficient.
- If validation fails, revert or repair the current integration unit. Do not conceal failures by accepting a broader merge.

### 5. Retire only after accounting for value

A branch may be retired only when all are true:

- its unique beneficial behavior is present on verified `main`, or is explicitly rejected with a reason;
- no open review, release, deployment, or dependent ref still requires it;
- its disposition and evidence are recorded in the final receipt;
- the configured human approval for branch deletion has been obtained.

Delete only the approved refs. Never delete `main`.

### 6. Credential-exposure gate

When a tracked secret or private credential file is discovered:

1. Revoke/rotate the exposed values first; history cleanup does not invalidate prior copies.
2. Do not create archive tags or backup refs pointing to contaminated history.
3. Finish the value-preserving convergence so only intended refs remain.
4. Use an authorized, separately approved history-rewrite procedure across every remaining branch and tag.
5. Verify after rewriting that the sensitive path and known secret identifiers are absent from all reachable refs, and document the checks.

This gate does not authorize a force-push or rewrite on its own.

## Output contract

Produce `harmonious-merge-audit.json` containing:

- baseline SHA and ref inventory;
- one evidence-backed disposition per branch/tag;
- capability groups and provenance for each integrated behavior;
- integration commit SHAs and validation receipts;
- approved retirement actions and deleted refs;
- security findings, credential-exposure gates, and any required follow-up;
- final `main` SHA and an explicit statement that `main` was preserved.

## Local validation

The protocol passes only when:

- every discovered branch/tag has a recorded disposition;
- all integrations pass the required validation on `main`;
- every retired ref has a preservation-or-rejection record and approval receipt;
- `main` remains present and is the verified canonical result;
- when secrets were involved, no new ref preserves contaminated history and the credential gate is explicitly resolved or escalated.

## Non-goals

- Replacing `main` with a favored branch
- Blindly merging every branch or copying files verbatim
- Deleting branches before their useful behavior is accounted for
- Creating archive tags that preserve known secrets
- Treating a branch-count reduction as proof of successful integration
- Performing force-pushes, protected-branch bypasses, or credential rotation without explicit authorization
