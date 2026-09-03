# Branch Lifecycle Decision Model

## Objective

Reduce branch count and future branch accumulation while retaining every branch that still carries unproven unique value.

## Evidence hierarchy

Strongest to weakest:

1. GitHub reports a PR as merged **and that PR's head SHA exactly matches the branch's current head SHA**.
2. Default-vs-branch comparison reports `ahead_by == 0`.
3. Open PR lineage proves active review.
4. Unique commits (`ahead_by > 0`) prove divergence, not value or uselessness.
5. Age is a review signal only.
6. Name similarity is a grouping hint only.

## Why exact merged-head proof beats ancestry

Squash and rebase merges can make an unchanged merged branch tip non-ancestral to the default branch even though its reviewed work has been incorporated. Exact PR head SHA equality solves that: if the current branch head is the same SHA that GitHub records as the merged PR head, the branch lifecycle is complete even when ancestry does not show it.

A historical merged PR is **not** enough when the branch has moved afterward. If the current branch SHA differs from the merged PR head SHA, the system falls back to live default-vs-branch comparison and preserves new divergence.

## Why divergence is preserved

A branch with unique commits can contain abandoned experiments, valuable unfinished work, or conflicting superseded work. The system cannot distinguish those meanings from commit topology alone. It therefore creates a consolidation candidate, never an automatic deletion.

## Family synthesis

The family key strips common automation prefixes and volatile suffixes such as ISO-like dates, YYYYMMDD values, PR/ticket/run numbers, and trailing numeric IDs.

Family ranking is a triage heuristic, not semantic proof:

1. open PR,
2. merged PR,
3. unique commits,
4. newest head timestamp,
5. stable lexical tie-break.

The top-ranked branch is called the **family lead**, not the canonical branch. Siblings remain preserved until a human or higher-level synthesis process proves equivalence or integrates their useful changes.

## Cleanup confidence

- 100: merged PR and no blocking condition.
- 98: ahead_by == 0 and comparison evidence is complete.
- 0: protected, active, divergent, unknown, or evidence error.

The default policy requires >=95 for automatic deletion.

## Root-cause control

A mature deployment combines:

- immediate post-merge cleanup for ephemeral branch families;
- periodic inventory for historical residue;
- family review for divergent siblings;
- branch-creation policy that prefers updating an existing active family branch over spawning a new branch when the work is truly the same stream.

The last rule is advisory because branch reuse must never be inferred solely from naming.
