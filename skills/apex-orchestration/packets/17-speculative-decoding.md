# Packet 17 — SPECULATIVE-DECODING

**Owner:** apex-orchestration v1.2.0
**Maturity:** 9 / "2-3× latency reduction with verifier-guaranteed quality"
**Layer:** Skill
**Scope:** The mesh may dispatch a single subtask to a fast draft lane (CODE-FAST, ROUTER-FREE) and a slow verifier lane (CODE, REASON) in parallel; the verifier gates the draft's output.

---

## Invariant (L5)

A speculative-decoding dispatch is valid iff:
1. The draft lane and verifier lane are both members of the Packet 04 hard-rule candidate set for the subtask.
2. The verifier has equal-or-higher trust score (Packet 13) than the draft.
3. The output used downstream is the verifier's output if it arrives within `SLA_MS`; otherwise the draft is used with an `unverified: true` flag.
4. The strategy decision is recorded in `runs/<mission_id>/speculation_log.jsonl`.

## The Pattern

```
DISPATCH  (parallel)
├── draft = CODE-FAST (poolside/laguna-xs-2.1:free)   target: 200ms
└── verify = CODE (poolside/laguna-s-2.1:free)        target: 1500ms

FUSE  (wait for first)
  if verify.done < SLA_MS and verify.l2_proof:
    return verify.result
  elif draft.done < SLA_MS and draft.l2_proof:
    return draft.result with unverified: true
  else:
    F-DIS-01 dispatch_timeout BLOCK
```

`SLA_MS` defaults to `2000` (configurable per lane pair in `~/.local/share/apex-orchestration/speculation_config.json`).

## Gates

- **G1 — Trust gate.** `verifier.trust_score >= draft.trust_score + 0.1`. The verifier must be meaningfully better; otherwise speculation is anti-pattern (you pay double the cost for no quality gain).
- **G2 — SLA gate.** A subtask that takes longer than `SLA_MS` is never speculatively decoded; the orchestrator falls back to direct verification.
- **G3 — Equivalence gate.** For arithmetic / code / structured tasks, the verifier must confirm semantic equivalence OR explicitly mark `diverged: true` and the diff is recorded in `runs/<mission_id>/diverged.jsonl`. For creative tasks, the verifier may accept any draft that meets minimum length and content criteria.
- **G4 — Cost gate.** Speculation is enabled only when `cached_draft_count > 10` for the (draft, verifier, task-type) tuple; cold-start overhead is not amortized.
- **G5 — Reproducibility gate.** For the same `task_text` and same lane pair, the speculation decision (use_draft / use_verify / fall_through) is deterministic.

## Anti-Patterns

- Speculating on tasks that require fresh data (e.g. "what time is it in Tokyo?") — drafts may invent plausible but wrong answers.
- Using a higher-cost verifier than the work justifies (e.g. running nemotron-3-ultra to verify a code comment).
- Skipping the equivalence check ("the draft is good enough") — that's a quality regression.
- Caching speculative outputs across unrelated tasks.

## L2 Evidence

- Trust-gate test: pair (ROUTE-FREE, REASON) → 0.95 vs 0.20 trust; speculation enabled. Pair (CODE, CODE) → 0.92 vs 0.92; speculation disabled.
- SLA test: draft at 100ms, verify at 2000ms → draft used. Both at 3000ms → BLOCK.
- Equivalence test: identical outputs → no diverged log. Differing outputs → diverged entry.
- Reproducibility test: same task, two runs → same decision.

## Versioning

- **Major bump:** SLA default change, trust threshold change.
- **Minor bump:** new lane pair added to speculation matrix.
- **Patch:** bug fix in equivalence check.

Current version: **1.0.0** (paired with apex-orchestration v1.2.0).
