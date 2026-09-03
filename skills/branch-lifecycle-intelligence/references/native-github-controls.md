# Native GitHub Controls — Defense in Depth

The branch lifecycle skill should cooperate with GitHub's native controls rather than reimplement everything.

## 1. Automatically delete merged head branches

**Preferred baseline:** enable GitHub's repository setting **Automatically delete head branches** wherever the repository's protection/rules policy permits it.

Why:

- GitHub closes the ordinary post-merge lifecycle at the platform layer.
- The reusable Branch Lifecycle workflow remains useful for historical residue, zero-ahead branches, branch families, reused-branch protection, and durable receipts.
- If GitHub already removed the event head, the workflow treats absence as an idempotent resolved state rather than recreating or failing on the ref.

The workflow records `native_delete_branch_on_merge` in its plan and receipt so missing native cleanup is visible.

## 2. Use rulesets selectively for branch creation

GitHub rulesets can restrict branch creation for matching patterns and allow explicit bypass actors.

Use this for **sensitive long-lived namespaces** or tightly controlled automation namespaces, not as a blanket ban on all feature branches.

Recommended posture:

- protect `main`, release, production, and other long-lived refs;
- restrict creation only where the allowed creators are known;
- use an evaluation/observation phase before enforcing broad metadata or creation restrictions when available;
- keep ordinary independent work possible.

The Branch Admission engine remains the semantic layer: exact workstream identity can justify reuse or consolidation; naming similarity alone does not.

## 3. Limit multi-ref push blast radius

Where GitHub's repository push policy is available, configure a low upper bound on the number of branches/tags a single push can update. GitHub currently recommends a default maximum of **5**.

This protects against accidental mirror-style pushes and large multi-ref mutations. It complements—not replaces—the lifecycle workflow.

## 4. Avoid rate-limit self-inflicted failures

The reusable workflow is designed around GitHub's secondary-rate guidance:

- merged PR event: `event_head` scope inspects only that branch;
- scheduled/manual sweep: `full` scope;
- branches already proven by an exact merged-current-head PR skip unnecessary compare calls;
- comparison commit data is reused for head timestamps before a separate commit lookup is attempted;
- API inspection concurrency is bounded;
- apply runs have a configurable deletion budget;
- successful DELETE calls are paced by at least 1.1 seconds;
- deferred candidates remain in the receipt for the next batch.

## 5. No destructive shortcut

Native controls do not weaken the core law:

> **No unique work is deleted because it is old, oddly named, or inconvenient.**

Automatic cleanup requires current evidence that the ref is lifecycle residue. Divergent work is integrated, preserved, or explicitly consolidated first.

## Source anchors

- GitHub Docs — Managing the automatic deletion of branches
- GitHub Docs — Available rules for rulesets / Restrict creations
- GitHub Docs — Managing the push policy for your repository
- GitHub Docs — Best practices for using the REST API / secondary rate limits
