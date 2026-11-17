# Job score rubric (legal-ops / agent-builder)

Derived from vendored **career-ops** `modes/_shared.md` @ `8831748b952bbe96752b7f0319d46c66069fc544`.

## Dimensions (holistic global 1–5)

| Dimension | What it measures |
|-----------|------------------|
| CV match | Skills, experience, proof points |
| North Star alignment | Fit vs target archetypes |
| Compensation | Salary vs market (5 = top quartile) |
| Cultural signals | Culture, growth, remote policy |
| Red flags | Blockers and warnings |

Global score is a single holistic judgment across dimensions — not a numeric average of A–H report blocks.

## Bands

| Band | Score | Action |
|------|-------|--------|
| Strong apply | 4.5–5.0 | Apply |
| Apply | 4.0–4.4 | Apply |
| Maybe | 3.0–3.9 | Consider (user must name reason to apply) |
| Skip | < 3.0 | Skip |

Triage PASS default: 3.5 (`pipeline.triage_threshold` may override).

## Helix overlay gates

- Score ≥ 4.0 before full tailor + apply prep for legal-ops targeting.
- `sent_state_requires_external_receipt`: human submit + receipt before SENT.
- Pair IRAC tailoring (`legal/irac-prompt-builder`) on JD for compliance/legal-ops narratives.

## Upstream

- https://github.com/career-ops-hq/career-ops — MIT
