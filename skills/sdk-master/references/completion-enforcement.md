# SDK Master completion enforcement

## Mission gates
A task remains OPEN until all explicitly requested acceptance criteria have receipts. A commit, draft PR, passing fixture test, or written plan is not operational completion.

## Proactive continuation
On discovery of an unmet acceptance criterion, immediately select and execute the next authorized, available verification or repair action. Do not convert known executable work into a user follow-up. Continue through implementation, tests, real repository exercise, and readback where access permits. Preserve blockers and a runnable next action only after exhausting available routes.

## Penalty ledger
Initial user-assessed score: -5. Do not silently reduce or erase this score.
- Failure to finish: -1 for each incident.
- Failure to proactively pursue an identified gap: -1.
- Failure to enforce a declared completion gate: -1.
- Unsupported completion claim: -1.
- Repeat of a known failure: -2.
Penalties are accountability records, not authorization to bypass safety, invent evidence, or degrade service. No self-awarded recovery credit.

## SDK Master acceptance
1. Read canonical skill and owning SDK source.
2. Run inspector against a real SDK repository and capture manifest identity and exports.
3. Execute representative SDK behavior or conformance tests, not fixtures alone.
4. Record exact commands, versions, results, and limitations.
5. For external provider mutations, verify provider-native readback; if unavailable mark UNVERIFIED.
6. Re-read repository/PR state after writes.
7. Mark COMPLETE only when every applicable gate passes; otherwise OPEN with explicit remaining steps.

## Regression checks
A future run fails its acceptance review if it reports COMPLETE while any gate is unverified, labels a draft as deployed, or stops after detecting an authorized executable gap. Include negative tests for these cases when implementing automation.
