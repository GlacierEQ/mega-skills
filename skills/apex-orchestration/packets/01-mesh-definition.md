# Packet 01 — MESH-DEFINITION

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Production-grade canonical mesh contract"
**Layer:** Skill (atomic, source of truth for all derived layers)
**Scope:** Names every lane in the Holographic Mesh. Defines model, dispatch trigger, output artifact, and version lock for each.

---

## Invariant (L5)

A mesh of N lanes is canonical iff:

1. Each lane is mapped to exactly one **model identifier** on the OpenRouter free tier.
2. Each lane has a **dispatch trigger** that is testable as a predicate.
3. Each lane has an **output contract** that is a JSON-Schema.
4. No two lanes share the same (model, role) pair.
5. Adding or removing a lane is a versioned change to this packet, not to the SKILL.md.

Violations: L2 proof is invalid. FUSE step rejects.

## Mesh Table (canonical)

| Lane | Model | Dispatch Trigger (predicate) | Output Contract |
|------|-------|------------------------------|-----------------|
| REASON | `nvidia/nemotron-3-ultra-550b-a55b:free` | `plan_required OR invariants > 3 OR cross_domain` | `plan.md` with sections Invariants, DAG, Risks |
| CODE | `poolside/laguna-s-2.1:free` | `task == code_edit OR task == code_create` | `{files, sha256, tests, l2_proof}` |
| CODE-FAST | `poolside/laguna-xs-2.1:free` | `subagent == true AND scope < 200_lines` | `{files, sha256, l2_proof}` |
| VERIFY | `z-ai/glm-5.2:free` | `verify_required == true OR audit == true` | `{findings: [{severity, file, line, evidence}]}` |
| REVIEW | `cohere/north-mini-code:free` | `refactor == true OR simplify == true` | `{diff, before_complexity, after_complexity}` |
| LONG-CTX | `thinkingmachines/inkling:free` | `input_tokens > 500_000` | `{summary, citations[]}` |
| LONG-CTX-ALT | `minimax/minimax-m3:free` | `input_tokens > 500_000 AND inkling_unavailable` | `{summary, citations[]}` |
| THINK-DEEP | `minimax/minimax-m2.7:free` | `mission.horizon == "long" AND requires_evolution` | `{decomposition, evolution_log[]}` |
| NANO-PERCEPTION | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | `input_modality IN {image, video, audio}` | `{structured_perception}` |
| DOMAIN-MED | `inclusionai/ling-3.0-flash-sante:free` | `domain == "medical" OR domain == "clinical"` | `{answer, caveats, source_ids[]}` |
| DOMAIN-FIN | `inclusionai/ling-3.0-flash-fin:free` | `domain == "finance" OR domain == "quantitative"` | `{answer, caveats, source_ids[]}` |
| ROUTER-FREE | `openrouter/free` | `smoke_test == true OR cost == 0 AND quality < critical` | `{response}` (never trusted without VERIFY) |

## Gates

- **G1 — Registration Gate:** every lane in this packet must be loadable in the running mesh at startup. Failing this gate = no mission.
- **G2 — Substitution Gate:** if a lane is rate-limited or unhealthy, the operator must swap to the lane with the same role from a fallback table. Never silently degrade.
- **G3 — Quota Gate:** if a lane is fully exhausted, mission is **BLOCKED** with cause, not silently retried.
- **G4 — Dispatch-Token Budget Gate:** reasoning-heavy lanes (REASON, THINK-DEEP, VERIFY) require `max_tokens >= 80`. The operator enforces this at dispatch time.

## Anti-Patterns

- Adding a lane without a predicate.
- Adding a lane without a JSON-Schema output contract.
- Mapping two lanes to the same model.
- Treating a domain lane (DOMAIN-MED, DOMAIN-FIN) as a generalist.

## L2 Evidence (required to ship this packet)

| Artifact | Required | SHA-256 |
|----------|----------|---------|
| `packets/01-mesh-definition.md` | yes | recorded at version bump |
| `schemas/lane-output/{lane}.schema.json` | yes for CODE, VERIFY, REVIEW, LONG-CTX | recorded |
| Live dispatch test of each lane | yes | receipt per lane |

## Versioning

- Major bump: lane removed, role changed, contract breaking.
- Minor bump: lane added, contract widened.
- Patch: wording, example, citation.

Current version: **1.0.0**
