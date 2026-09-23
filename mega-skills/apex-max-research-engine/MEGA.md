---
id: apex-max-research-engine
display_name: APEX Max Research Engine
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# APEX Max Research Engine (Mega Skill)

## Mission

Turn ordinary questions, strategic investigations, legal/evidentiary analysis, technical reconnaissance, and formal deep-research requests into a source-bound research mission with recursive search, contradiction pressure, epistemic verification, Diamond Agent Topography review, and action-ready delivery.

## Compounding structure

- **Required combos:**
  - `long-horizon-core` — mission contract, roadmap, durable evidence, context capsule, work packet, quality gate, handoff.
  - `recon-and-map` — source discovery, repository/workspace mapping, authority/source-of-truth identification.
  - `cross-cloud-memory-synthesis` — cross-source context recovery from Notion, GitHub, mail, Slack, calendar, drive, and other available systems.
  - `epistemic-verification-chain` — proof-tier classification, evidence registration, and quality authorization.
  - `max-research-spiral` — iterative search/extract/contradict/reframe/re-search loop.
  - `diamond-research-topography` — four-apex pressure review: Evidence, Logic, Counterargument, Action.
  - `signal-to-decision-loop` — convert verified findings into decision-ready options and next moves.

- **Conditional combos:** `capability-readiness`, `multi-agent-orchestration-mesh`, `guarded-automation-loop`, `evidence-to-evolution-loop`, `forensic-docket-intelligence`, `court-evidence-compiler`, `voice-evidence-authenticator`, `runtime-operations`.

## Execution protocol

1. **INTAKE.** Define mandate, decision use, risk class, target depth, proof floor, source scope, forbidden assumptions, and output contract. Emit `MISSION.md` and `intake.json`.
2. **MAP.** Build `SOURCE_MAP.md` across explicit sources, Notion, GitHub/repo roots, connected apps, public primary sources, and secondary sources.
3. **DECOMPOSE.** Emit `QUESTION_GRAPH.json` with primary question, subquestions, source lanes, aliases, adverse probes, and stop conditions.
4. **DISPATCH.** Run independent research lanes in parallel when available. Each lane returns source refs, claims, confidence, and gaps.
5. **SPIRAL.** Apply `max-research-spiral`: seed search -> extract -> register claims -> contradiction probe -> gap detection -> alias expansion -> second-order search -> confidence update -> recurse or stop.
6. **VERIFY.** Apply `epistemic-verification-chain`. Classify every consequential claim as Verified, Corroborated, Likely, Unverified, Conflict, or Unknown. Record `EVIDENCE.md` and `CONTRADICTIONS.md`.
7. **DIAMOND REVIEW.** Apply `diamond-research-topography`: Evidence Apex validates provenance; Logic Apex audits reasoning; Counterargument Apex attacks the thesis; Action Apex checks usefulness and next-step clarity.
8. **FUSE.** Produce `FUSION.md` by deduplicating, ranking proof strength, resolving conflicts where evidence permits, and preserving unresolved disagreements.
9. **DELIVER.** Emit `MAX_RESEARCH_MISSION_RESULT.md` with direct answer, source map, verified facts, analysis, contradictions, gaps, recommendations, confidence, and citation index.
10. **HANDOFF.** Persist `HANDOFF.md` with exact resume point, open gaps, next searches, reusable source IDs, and proposed skill/repo evolution items.

## Durable state files

`MISSION.md`, `intake.json`, `SOURCE_MAP.md`, `QUESTION_GRAPH.json`, `lane-receipts/<lane_id>.json`, `EVIDENCE.md`, `CONTRADICTIONS.md`, `SPIRAL_LOG.jsonl`, `DIAMOND_REVIEW.md`, `FUSION.md`, `MAX_RESEARCH_MISSION_RESULT.md`, `HANDOFF.md`.

## Cognitive firewall

- **Mode:** `read_only` by default.
- **Allowed actions:** `read_repository`, `search_workspace`, `read_connected_sources`, `load_public_sources`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`.
- **Approval required for:** external mutation, network send, filing, publication, deletion, deployment, merge, credential access, legal decision, public accusation, or acting on unverified allegations.
- **Proof floor:** L2 for local/internal research claims; L3+ for cross-system operational conclusions; L5+ for enterprise, legal, forensic, or public-facing assertions.

## Output contract

Produce `MAX_RESEARCH_MISSION_RESULT.md` containing Executive Finding, Research Questions, Source Map, Verified Facts, Timeline when needed, Analysis, Contradictions / Weak Points, Unverified Leads, Recommendations, Evidence Needed Next, Citation Index, and Confidence / Proof Tier.

## Local validation

- Registry contains this Mega Skill and both new Compound Skills.
- `registry/mega-skill-pyramids.json` generation resolves all required/conditional combos with zero owned unresolved references.
- `python scripts/generate_mega_skill_pyramids.py --check` passes after registry materialization.
- Sample research run emits `SPIRAL_LOG.jsonl`, `DIAMOND_REVIEW.md`, and `MAX_RESEARCH_MISSION_RESULT.md`.

## Non-goals

Do not replace child methods by copying them here. Do not pretend inaccessible sources were checked. Do not treat inference as verified fact. Do not produce court/filing-ready conclusions without primary authority and human legal review.
