# Packet 04 — ROUTING-HEURISTICS

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Eight hard rules; each testable as a predicate"
**Layer:** Skill
**Scope:** Rules the operator applies at DECOMPOSE and DISPATCH to choose a lane for each subtask. Rules are ordered; first match wins.

---

## Invariant (L5)

A subtask is routed correctly iff at least one rule in this packet matched, and the chosen lane satisfies that rule's predicate. Routing to a lane that does not satisfy a rule is a **soft violation** and is logged but not blocked; routing to a lane that violates a **gating rule** (G-tag) is a hard fail.

## The 8 Rules (ordered)

| # | Rule ID | Predicate | Route To | Gate? |
|---|---------|-----------|----------|-------|
| 1 | R-MEDICAL | `subtask.domain == "medical" OR subtask.domain == "clinical"` | DOMAIN-MED | YES |
| 2 | R-FINANCE | `subtask.domain == "finance" OR subtask.domain == "quantitative"` | DOMAIN-FIN | YES |
| 3 | R-MULTIMODAL | `subtask.input_modality IN {image, video, audio}` | NANO-PERCEPTION | YES |
| 4 | R-LONGCTX | `subtask.input_tokens > 500_000` | LONG-CTX (fallback: LONG-CTX-ALT) | YES |
| 5 | R-PLAN | `subtask.kind == "plan" OR subtask.invariants > 3 OR subtask.cross_domain` | REASON | YES |
| 6 | R-CODE-EDIT | `subtask.kind == "code_edit" OR subtask.kind == "code_create"` | CODE | NO (default) |
| 7 | R-CODE-FAST | `subtask.subagent == true AND subtask.estimated_lines < 200` | CODE-FAST | NO |
| 8 | R-DEFAULT | always | ROUTER-FREE (smoke) + VERIFY (audit) | NO |

## Gates

- **G1 — Domain hard gate.** R-MEDICAL and R-FINANCE cannot be overridden. A medical question routed to a non-DOMAIN-MED lane is a hard fail.
- **G2 — Multimodal hard gate.** If input is image/video/audio, NANO-PERCEPTION is mandatory.
- **G3 — Long context hard gate.** Inputs over 500k tokens must use LONG-CTX (or its fallback).
- **G4 — Plan hard gate.** Plans, multi-invariant analysis, and cross-domain missions must use REASON.
- **G5 — Quota gate.** If the routed lane reports `unhealthy OR quota_exhausted`, the operator must swap to the next-strongest lane with the same role. Quota-exhausted is a hard BLOCK, not a silent retry.

## Anti-Patterns

- Routing medical questions to generalist lanes to "save tokens."
- Routing 1M-token inputs to non-LONG-CTX lanes.
- Calling REASON for trivial edits.
- Concatenating two rules to pick a single lane (e.g. "this is medical AND code so DOMAIN-MED writes code"). Rules do not compose that way; the FIRST match wins.

## L2 Evidence

Each routing decision logs:
- rule_id that matched
- lane selected
- lane health check (`ok` / `degraded` / `unhealthy` / `quota_exhausted`)
- fallback applied (if any)

`{decision_id, rule_id, lane, health, fallback, ts}` appended to `routing_decisions.jsonl`.

## Versioning

Adding a rule is a minor bump. Changing a predicate or gate is a major bump.

Current version: **1.0.0**
