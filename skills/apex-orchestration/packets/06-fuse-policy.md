# Packet 06 — FUSE-POLICY

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Deterministic merge with conflict resolution and dedup"
**Layer:** Skill
**Scope:** How verified outputs are combined into one compound artifact. No averaging, no silent overwrite.

---

## Invariant (L5)

FUSE produces a single compound artifact iff:

1. Every input is a verified receipt (L2+ from Packet 03 and 05).
2. Conflicts are resolved by **dominant-verified evidence**, never by majority or by averaging.
3. Dedup is content-hash based, not lane based.
4. The compound artifact is itself a receipt with `l2_proof: true` and a `receipt_chain_sha256` covering every input.

## FUSE Algorithm (canonical)

```
fuse(verified_receipts[]) -> compound_artifact:
    1. filter(verified_receipts, r => r.l2_proof == true)        # drafts dropped
    2. sort(verified_receipts, key = (lane_priority, ts))        # deterministic order
    3. for each pair (a, b): if a.text == b.text: dedup keep first
    4. for each conflict (a, b) on the same fact:
         if both L2: pick the one whose evidence is reproducible (sha256, log, test)
         if only one L2: keep the L2
         if neither L2: BLOCK with cause
    5. chain_hash = sha256( concat(receipts in order) )
    6. compound = { artifacts, dedup_count, conflicts_resolved, chain_hash, l2_proof: true }
    7. write compound to fused.json
    8. return compound
```

## Conflict Resolution Order

1. **Reproducible evidence wins.** sha256 of a file, a test exit code, a log line.
2. **Most recent L2 wins** if evidence ties.
3. **Producer lane wins** over auditor lane if both L2 and same evidence class (auditor only overrides producer when finding is BLOCKER severity).
4. **All other ties BLOCK** with explicit cause. No silent picks.

## Dedup

Two outputs are duplicates iff `sha256(normalize(text))` matches after:
- Stripping leading/trailing whitespace
- Collapsing internal whitespace to single space
- Removing all comments and code-fence markers

## Gates

- **G1 — No averaging.** Never average numeric values across lanes. Pick the one with L2 proof.
- **G2 — No silent overwrite.** Every dedup or conflict decision is logged in `fused.json`.
- **G3 — Draft rejection.** Any input without `l2_proof: true` causes FUSE to fail with `code: DRAFT_REJECTED`.
- **G4 — Chain hash deterministic.** Same inputs in same order produce the same chain hash. Verified by test.

## Anti-Patterns

- "Three models said X, so X is true" (averaging = anti-pattern).
- "The newer output wins" without evidence check.
- Dropping a receipt silently because it disagrees with the majority.
- Re-running FUSE on a different sort order and getting a different artifact.

## L2 Evidence

- `fused.json` itself is a receipt (conforms to Packet 03).
- Determinism test: running FUSE twice on the same input set produces identical chain hash.
- Conflict log: every conflict, decision, evidence cited.

## Versioning

- Major bump: change to dedup normalization, change to conflict resolution order.
- Minor bump: new optional block in `fused.json`.

Current version: **1.0.0**
