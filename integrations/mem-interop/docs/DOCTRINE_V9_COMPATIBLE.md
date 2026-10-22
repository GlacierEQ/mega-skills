# OMP v9 Glacier lineage — operational contract

This is a **v9-compatible additive integration contract**, not a claim that a historical `OMP v9` executable or deployed host has been recovered. Existing OMP v0.7.x and PRs remain separate. This package neither installs nor replaces their runtime.

## Ownership and anti-regression
- GlacierEQ mission objective and scope: APEX + Aspen Grove.
- Interface / agent orchestration: OMP, native `.omp` skills/rules/extensions.
- External action and ambiguity resolution: Computer User + sigma-glue; explicit authorization and native readback.
- Context: live Mem MCP; SQLite read-only fallback, original UUIDs and versioned owners.
- Evidence: case-specific original provider and official Box bytes/hashes, not Mem narration.
- Skills: `GlacierEQ/mega-skills` canonical library; no forked skill engines.

## Required runtime habit
**PRECHECK → CURRENT-TURN MISSION → CONTEXT RECOVERY → AUTHORITY RECONCILIATION → TOOL REUSE → EXECUTE AUTHORIZED → PROVIDER RECEIPT → INDEPENDENT READBACK → ADVERSARIAL VERIFICATION → LEARN → PRESERVE → CONTINUE.**

The current-turn mission binding is a safety condition: finding `1FDV...` or `HI-...` in a prompt is a candidate, not proof of permission or the only active mission. Never force a historical mission into a new conversation. Session-start OMP extension supplies stable instruction only; recovery via actual MCP calls must still happen.

## Mandatory evidence states
`PREPARED`, `DRAFT`, `ACTION_ATTEMPTED`, `PROVIDER_ACCEPTED`, `PROVIDER_ACKNOWLEDGED`, `INDEPENDENTLY_READ_BACK`, `DECIDED`, `BLOCKED`, `SUPERSEDED`, `UNVERIFIED`.

- No fake sends, court filings, ATS submissions, tool installs, memory writes, or deployment claims.
- `Mem read` is `MEM_SECONDARY`, not `NATIVE_SOURCE`.
- `CODE_TEST_PASS` is not `OMP_RUNTIME_INSTALLED` or `REMOTE_MCP_OAUTH_CONNECTED`.
- `ARCHIVE_OFFLINE_SEARCH` is not `LIVE_MEM_SYNC`.
- A failed or unobserved provider mutation stays `UNVERIFIED`, not silently `DONE`.

## Failure learning contract
Store `failure_id`, source evidence, exact reproduction, intended behavior, actual behavior, repaired owner, red/green tests, provider verification, cross-session continuation, and regression trigger. A workflow that only restates a lesson without changing behavior has not passed the LEARN gate.

## Secrets and child/medical boundaries
This archive is private. `sensitivity_hint` is classification only, not true authorization enforcement. Restrict who can access the database process. Keep MCP body access disabled unless local process owner explicitly enables it. Do not commit the SQLite corpus into GitHub; no tokens, client secrets or case evidence in source patches.