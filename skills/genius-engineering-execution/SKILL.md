---
name: genius-engineering-execution
description: "Evidence-bound execution kernel from GlacierEQ/Genius-Engineering: compile upgrade work into a dependency graph, execute in parallel waves by maximal ready frontier, map each change to its verification gates, and complete fail-closed — exit 0 only when the mission is genuinely complete."
---

# Genius Engineering Execution

Run multi-repo or multi-stage upgrades so partial completion cannot be mistaken for done: the mission (the terminal engineering outcome) is compiled to a dependency-aware execution graph and driven to verified completion with deterministic receipts.

## Workflow

1. State the mission as a terminal outcome with observable completion conditions.
2. Compile the work into a dependency graph; attach each node's verification gates and evidence requirements.
3. Execute wave by wave at the maximal ready frontier; record a receipt per wave.
4. On any gate failure, halt that branch fail-closed, preserve the counterevidence, and repair via the owning skill before the wave re-runs.
5. At the frontier's end, verify the terminal outcome itself (exact revision + provider readback), not the sum of task completions.
6. Emit the mission receipt chain; anything unverified is reported as incomplete, never rounded up to done.

## The kernel's rules

**Provenance:** `GlacierEQ/Genius-Engineering` README and kernel description (estate source, cloned 2026-10-21). This skill registers the estate's own execution method for large upgrade runs.

- **Prime rule.** *The mission is the terminal engineering outcome, not the smallest task that can be completed.* Every plan is judged against the outcome, never against effort expended.
- **Compile, then execute.** Work is compiled into a dependency graph first; execution proceeds in parallel waves by maximal ready frontier — everything whose dependencies are satisfied runs, nothing runs early.
- **Change → gate mapping.** Each change is mapped to its verification gates before it executes; a change without a gate does not enter the graph.
- **Fail-closed completion.** Exit 0 happens only when the mission is genuinely complete: exact-revision deployment plus provider readback, counterevidence preserved rather than discarded, and deterministic SHA-256 receipts for the whole run.

## Safety gates

- Partial completion is reported as partial — the kernel's exit semantics are the honesty mechanism.
- Counterevidence is preserved with the same care as success evidence; deleting it voids the run's receipts.
- A node without a verification gate never enters the graph.

## Output contract

- Executed mission with per-wave receipts (deterministic SHA-256)
- Completion verdict: exit 0 only on genuine, verified mission completion

## Related skills

- spiral-promotion-gate — the decision gate for candidates inside the mission
- progressive-pyramid — inherited-result construction with independent outcome proof
- verification-before-completion — the assertion discipline at node scale
- quality-gate — per-phase accept/reject criteria

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/genius-engineering-execution/tests -v
git diff --check
```
