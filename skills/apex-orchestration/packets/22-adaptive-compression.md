# Packet 22 — ADAPTIVE-COMPRESSION

**Owner:** apex-orchestration v1.3.0
**Maturity:** 9 / "Right-sized tokens per task type; 30-60% spend reduction"
**Layer:** Skill
**Scope:** Replace the fixed `max_tokens` floor of 80 with a per-task-type adaptive budget learned from receipt history.

---

## Invariant (L5)

A token budget decision is valid iff:
1. The budget is bounded: `min_tokens <= requested <= max_tokens`.
2. The budget is task-type specific (not one-size-fits-all).
3. The budget is adjusted by a learned coefficient (per-domain, per-lane) derived from `lane_stats.json`.
4. A reasoning-heavy lane (REASON, THINK-DEEP, VERIFY) gets at least the reasoning floor (default 80; configurable).
5. The decision is recorded in `runs/<mission_id>/compression_log.jsonl` with the rationale.

## The Adaptive Budget Function

```
budget(task_type, lane, domain) =
    base[task_type]                              # from defaults
  * compression_coef[lane][domain]                # learned, default 1.0
  * difficulty_factor(estimated_difficulty)       # 0.6 (easy) - 1.4 (hard)
  * safety_margin                                # 1.2x
  clamped to [min_floor, max_cap]
```

Default `base` per task_type:

| Task type | base | min_floor | max_cap |
|---|---|---|---|
| `code_edit` | 1024 | 256 | 4096 |
| `code_create` | 2048 | 512 | 8192 |
| `plan` | 2048 | 512 | 8192 |
| `audit` | 2048 | 512 | 8192 |
| `simplify` | 1024 | 256 | 4096 |
| `summarize` | 512 | 128 | 2048 |
| `classify` | 256 | 64 | 1024 |
| `embed` | 64 | 32 | 256 |

## Difficulty Estimation

A simple, fast heuristic:
- Input length in tokens: `< 500` → easy (0.6), `500-2000` → medium (1.0), `> 2000` → hard (1.4).
- If `task_type` is `code_create` or `plan`, +0.2.
- If `invariants > 3`, +0.2.

## Compression Coefficient (learned)

Per `(lane, domain)`, the coefficient is the ratio of median successful output length to the default base. Updated on every successful receipt. Bounded `[0.5, 1.5]`.

## Gates

- **G1 — Floor gate.** Reasoning-heavy lanes always get ≥ 80 tokens (or configurable reasoning_floor). Below = dispatch is force-rejected.
- **G2 — Cap gate.** No lane ever gets > `max_cap` tokens per call. Above = clamped, audit-logged.
- **G3 — Calibration gate.** `compression_coef` updates only on `l2_proof=true` receipts. Failed dispatches don't shrink the budget (they signal under-budget).
- **G4 — Reproducibility gate.** For the same (task_type, lane, domain, input_size) tuple, the budget is deterministic.
- **G5 — Cost-savings gate.** Average budget across last 50 missions must be ≤ 80% of the v1.2.0 fixed-budget baseline. If regression detected, rollback the coefficient update.

## Anti-Patterns

- Setting the budget to 0 (silently truncates output; L2 proof is unverifiable).
- Using a single budget across all lanes (ignores per-lane characteristics).
- Allowing the budget to grow without bound (cost explosion).
- Skipping the cost-savings gate (no regression detection).

## L2 Evidence

- Floor test: VERIFY lane, task=audit → budget ≥ 80. CODE-FAST, task=classify → budget ≥ 64.
- Cap test: any task → budget ≤ max_cap.
- Reproducibility test: same inputs → same budget.
- Cost-savings test: simulate 50 missions, average budget ≤ 80% of v1.2.0 baseline.
- Calibration test: failed dispatches don't update coefficients.

## Versioning

- **Major bump:** floor or cap default change.
- **Minor bump:** new task_type added to defaults.
- **Patch:** bug fix in coefficient update.

Current version: **1.0.0** (paired with apex-orchestration v1.3.0).
