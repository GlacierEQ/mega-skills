---
id: max-research-spiral
display_name: Max Research Spiral
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Max Research Spiral

## Purpose and selection

Use this Combo Skill when a question requires deeper-than-first-pass research, contested facts, source triangulation, contradiction discovery, or high-confidence synthesis. Do not use it to inflate a simple lookup where one authoritative source fully answers the question.

## Incremental value

This Combo adds recursive search intelligence: every pass converts findings into sharper queries, adverse probes, missing-evidence checks, and confidence updates until the answer is earned or source limits are explicit.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set mandate, proof floor, source scope, and stop conditions. | User request, constraints, risk class | `MISSION.md` | Scope and stop conditions are explicit. |
| 2 | `recon-and-map` | Compound Skill | Yes | Discover source-of-truth locations, aliases, and reachable source lanes. | `MISSION.md` | `SOURCE_MAP.md` | Source candidates and access limits are recorded. |
| 3 | `evidence-register` | Skill | Yes | Register extracted claims, source IDs, timestamps, and proof state. | Source extracts and citations | `EVIDENCE.md` | Material claims map to evidence or assumptions. |
| 4 | `claim-calibration` | Skill | Yes | Calibrate each claim to Verified/Corroborated/Likely/Unverified/Conflict/Unknown. | `EVIDENCE.md`, contradictions, gaps | `CLAIM_BOUNDARIES.md` | Claim wording does not exceed evidence. |
| 5 | `quality-gate` | Skill | Yes | Decide recurse, stop, block, or deliver. | Spiral state and claim boundaries | `SPIRAL_GATE.md` | Stop/recurse decision is reproducible. |

## Ordered execution

1. **Seed.** `mission-contract` defines primary question, subquestions, proof floor, source scope, risk, output contract, and stopping rules.
2. **Map.** `recon-and-map` builds a source/alias map and identifies primary, workspace, connected, and public source lanes.
3. **Extract.** `evidence-register` records source extracts as claim rows with source IDs, dates, provenance, and gaps.
4. **Contradict.** `claim-calibration` searches for contrary evidence, stale-source risk, alternate interpretations, and proof-level downgrades.
5. **Reframe.** Generate next-pass queries from aliases, contradictions, missing dates, missing actors, adverse authority, and unexplained transitions.
6. **Gate.** `quality-gate` decides whether to recurse, stop, or block. Record every cycle in `SPIRAL_LOG.jsonl`.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `mission-contract` | `recon-and-map` | Research mandate, proof floor, source scope | Source map and search lanes | research lead |
| `recon-and-map` | `evidence-register` | Source IDs, search results, access limits | Evidence rows with source references | source mapper |
| `evidence-register` | `claim-calibration` | Extracted claims and provenance | Calibrated claim boundaries | evidence owner |
| `claim-calibration` | `quality-gate` | Confidence, gaps, contradictions | Recurse/stop/block decision | epistemic auditor |

## Evidence, risks, and state

Record every spiral cycle with queries run, sources loaded, new claims, contradictions, confidence delta, gaps closed, gaps opened, and next searches. Never claim exhaustion unless the searched source scope and limits are named.

## Quality gates

Complete only when the answer is supported enough for the declared risk class, contradiction probes were attempted, unresolved gaps are explicit, and claim wording matches proof tier.

## Compound output

**Artifact:** `MAX_RESEARCH_SPIRAL_RECORD.md` plus `SPIRAL_LOG.jsonl`.

**Ready for Mega Skill integration when:** final cycle has a reproducible stop decision, no material claim exceeds evidence, and next searches are complete or intentionally deferred.
