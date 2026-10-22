---
name: glacier-memory-learn
description: Turn a failed GlacierEQ agent or connector operation into a tested behavioral correction and preserved cross-session continuation.
---
# Glacier Memory Learn — causal repair not cosmetic cleanup

1. Recover the exact failed execution, user-defined intended outcome and native provider state. Capture time, tool/result, code revision, and false-success risk.
2. Reproduce the failure with a red test or a safe provider readback that demonstrably fails the acceptance contract.
3. Trace the missing handoff: admission, recovery, permission, actual action, receipt, readback, durable preservation or subsequent boot.
4. Implement the correction at the existing owner, not in a parallel framework. Retain source/fingerprint, regression tests, rollback path and constraints.
5. Run the focused and broader relevant checks, including failure/missing-credential/ambiguous-outcome cases. Verify actual runtime when accessible.
6. Preserve one durable repair receipt with exact branch/commit/tests/readback and action frontier. `CI_GREEN` is not `PROVIDER_EXECUTED`; report separately.
7. Test a subsequent run/clean session against the original failure when runtime access exists. Without that, mark behavior unverified.