---
name: spiral-promotion-gate
description: "The estate's upgrade decision method from GlacierEQ/spiral-engine: promote a candidate only when evidence shows it is executable, behaviorally equivalent-or-better, behind an explicit interface, rollback-ready, measurably better than its interface cost, and free of critical regressions."
---

# Spiral Promotion Gate

Decide upgrade promotions with the Spiral Engine's evidence-bound gate: measure before/after quality states, emit a CONTINUE / REVISE / PROMOTE / COMPLETE / CONSTRAINED signal, and bind any promotion to a short-lived HMAC grant and a SHA-256-chained receipt.

## Workflow

1. Name the candidate and the decision precisely: what replaces what, in which repository, at which source SHA.
2. Capture the before QualityState with the estate's measurement route; record dimensions that are critical for this candidate.
3. Execute or stage the candidate change (via the transform skills) and capture the after QualityState the same way.
4. Assemble PromotionEvidence: execution readiness, behavioral parity evidence, rollback readiness, explicit interface, benchmark gain vs interface cost.
5. Run the gate: record the revolution and read the signal. REVISE sends the candidate back with named regressions; CONSTRAINED ends the attempt with the stagnation on record.
6. On PROMOTE, issue the HMAC-bound grant and hand it to release; archive the chained receipt with the upgrade record.

## The gate, from source

**Provenance:** `GlacierEQ/spiral-engine` — `src/revolution_controller.py` (`decide_revolution`, `PromotionEvidence`, `SpiralPolicy`) and `src/promotion_authority.py`. This skill registers the estate's own proven method; it teaches the method, it does not reimplement the engine.

- **The promotion rule.** A candidate is promoted only when the evidence shows it is: executable; behaviorally equivalent or better; behind an explicit interface; rollback-ready; measurably better; worth more than its interface cost; and free of critical regressions. Missing any one, there is no promotion.
- **Measured states, not impressions.** The gate consumes a before and after `QualityState` (overall, critical floor, per-dimension scores). Default policy: overall target ≥ 9.0, critical floor ≥ 8.5, regression tolerance 0.5, stagnation limit 2.
- **Signals.** CONTINUE (measured progress), REVISE (a critical dimension regressed beyond tolerance — this overrides local gains), PROMOTE (promotion evidence satisfied), COMPLETE (balanced target reached), CONSTRAINED (stagnation across the limit — non-progress is named, never looped forever).
- **Receipts and grants.** Every revolution emits a SHA-256-chained receipt (each receipt hashes the previous). Promotion itself requires a bound, short-lived HMAC `PromotionGrant` tied to repository + source SHA + proof-receipt digest — an unbound verbal yes is not a promotion.

## Safety gates

- No evidence, no promotion — a candidate without parity and rollback evidence is REVISE by default.
- A critical-dimension regression vetoes local score gains; never average it away.
- Grants are short-lived and bound to one repo + SHA + proof digest; a stale grant is void, not reusable.

## Output contract

- Revolution receipt with the decision signal and its reasons
- Promotion grant (when PROMOTE) bound to repo, source SHA, and proof-receipt digest

## Related skills

- dependency-update-operator — feeds update candidates into this gate
- genius-engineering-execution — the execution kernel whose stage completions this gate can judge
- verification-before-completion — the assertion discipline the gate's evidence standard extends
- release — executes the promotion the gate grants

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/spiral-promotion-gate/tests -v
git diff --check
```
