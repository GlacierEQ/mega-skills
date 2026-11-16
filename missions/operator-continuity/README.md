# Operator Continuity

Chat-handoff packet for Operator Casey Barton / Aspen Grove continuity.

- `HANDOFF.md` — human resume (durable; use this path)
- `resume.json` — machine stub (`handoff_md` is repo-relative; `*_ephemeral` fields are originating-VM only)

Primary durable store: SuperMemory (`containerTag: operator-continuity`). Mem0 declined for the continuity write session that created this packet — do not block resume on Mem0 auth.

Query SuperMemory: `OPERATOR CONTINUITY Aspen Grove Keymaster Iceberg handoff 2026-11-16`
