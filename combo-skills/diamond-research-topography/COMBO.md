---
id: diamond-research-topography
display_name: Diamond Research Topography
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Diamond Research Topography

## Purpose and selection

Use this Combo Skill when research findings need adversarial review before delivery, especially legal/evidentiary matters, strategic decisions, public claims, technical architecture, security incidents, or any investigation where a clean narrative may hide weak proof.

## Incremental value

This Combo turns research synthesis into a four-apex pressure test. Evidence, Logic, Counterargument, and Action each review the same claim graph from a different failure angle, then Fusion preserves conflicts instead of flattening them.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `evidence-register` | Skill | Yes | Evidence Apex: verify source identity, provenance, timestamps, and quote fidelity. | Claim graph and source extracts | `EVIDENCE_APEX.md` | Every material claim maps to source or limitation. |
| 2 | `claim-calibration` | Skill | Yes | Logic Apex: check inference strength, causation, scope, and proof-tier wording. | Claim graph and evidence apex | `LOGIC_APEX.md` | Reasoning does not outrun evidence. |
| 3 | `epistemic-gate` | Skill | Yes | Counterargument Apex: attack assumptions, find contradictions, adverse authority, and alternate explanations. | Claim graph and source map | `COUNTERARGUMENT_APEX.md` | Strongest contrary theory is stated or source gap is named. |
| 4 | `roadmap-builder` | Skill | Yes | Action Apex: convert verified findings into options, risks, next searches, and decisions. | Reviewed claim graph | `ACTION_APEX.md` | Recommendations are evidence-bounded and executable. |
| 5 | `quality-gate` | Skill | Yes | Fusion Core: accept, block, or return for another spiral cycle. | Four apex reports | `DIAMOND_REVIEW.md` | Conflicts are preserved and delivery status is justified. |

## Ordered execution

1. **Evidence Apex.** Audit source identity, provenance, quote fidelity, chronology, metadata, and citation adequacy.
2. **Logic Apex.** Audit reasoning chain, causal attribution, legal/technical scope, and category errors.
3. **Counterargument Apex.** Build the strongest opposing view; search for adverse authority, missing primary sources, stale facts, and alternative explanations.
4. **Action Apex.** Translate findings into decisions, next moves, risks, and follow-up evidence needs without overstating certainty.
5. **Fusion Core.** Decide ACCEPT, RESEARCH_MORE, BLOCKED, or NEEDS_HUMAN_DECISION. Emit `DIAMOND_REVIEW.md`.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `evidence-register` | `claim-calibration` | Source-bound evidence map | Proof-tiered reasoning audit | evidence apex |
| `claim-calibration` | `epistemic-gate` | Calibrated claims and inferred links | Counterargument and contradiction record | logic apex |
| `epistemic-gate` | `roadmap-builder` | Accepted facts, conflicts, unknowns | Action options and evidence-needed list | counterargument apex |
| `roadmap-builder` | `quality-gate` | Action options and reviewed risks | Final Diamond review decision | action apex |

## Evidence, risks, and state

Record the four apex outputs separately. Do not merge away conflict. For legal/evidentiary matters, separate actor attribution, state attribution, transport attribution, and orchestration-layer causation.

## Quality gates

Complete only when Evidence, Logic, Counterargument, and Action reports exist, conflicts are explicit, proof-tier wording is calibrated, and recommendations are bounded by evidence.

## Compound output

**Artifact:** `DIAMOND_REVIEW.md`.

**Ready for Mega Skill integration when:** all four apexes pass or Fusion Core returns an explicit block/research-more decision with named missing evidence.
