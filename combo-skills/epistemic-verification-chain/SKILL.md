---
name: epistemic-verification-chain
description: 'Combo Skill: Epistemic Verification Chain. Reusable capability chain.'
---

# Epistemic Verification Chain

## Purpose and selection

Use this Combo Skill when facts, forensic artifacts, production code, or legal pleadings require rigorous validation across the 6-Tier Epistemic Ladder ($\mathcal{L}_0 \to \mathcal{L}_6$). Do **not** use it for casual conversational queries that lack operational impact.

## Incremental value

This Combo Skill binds evidentiary observation directly to formal quality gates, ensuring that zero actions are taken on unproven assumptions ($\mathcal{L}_0/\mathcal{L}_1$) and that enterprise deliverables satisfy $\mathcal{L}_5$ dialectic consensus.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `epistemic-gate` | Skill | Yes | Classify claim and evaluate against L0-L6 spectrum | Proposed claim, action, or code artifact | `epistemic-verification-receipt.json` | Epistemic tier verified with cryptographic evidence |
| 2 | `evidence-register` | Skill | Yes | Catalog SHA-256 hashes, provenance sources, and claims trace | Verification receipt and raw source data | `EVIDENCE.md` | All evidence entries have immutable hashes |
| 3 | `quality-gate` | Skill | Yes | Enforce the Epistemic Law of Action (L2+ local, L5+ enterprise) | Evidence register and epistemic tier | Gate record | Action authorized only when tier requirements are met |

## Ordered execution

1. **Epistemic triage — `epistemic-gate`** consumes operational claims, evaluates against $\mathcal{L}_0-\mathcal{L}_6$ criteria, produces `epistemic-verification-receipt.json`, and passes when evidence tier is mathematically grounded.
2. **Evidence registration — `evidence-register`** consumes the epistemic receipt, hashes all supporting artifacts with SHA-256, produces `EVIDENCE.md`, and passes when provenance is immutable.
3. **Authorization gate — `quality-gate`** consumes `EVIDENCE.md`, validates against execution thresholds ($\ge \mathcal{L}_2$ for local operations, $\ge \mathcal{L}_5$ for enterprise deliverables), produces a gate record, and passes when proof is complete.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `epistemic-gate` | `evidence-register` | Assigned epistemic tier, verification receipt | Cataloged evidence entries with SHA-256 | epistemic auditor | Epistemic tier is formally grounded |
| `evidence-register` | `quality-gate` | Complete EVIDENCE.md register | Verified authorization gate record | quality lead | All hashes verify and threshold is met |

## Evidence, risks, and state

The Combo must record all SHA-256 hashes, epistemic tier ratings, timestamp receipts, and peer review logs in its evidence register. It must strictly reject stubs, assumptions, or marketing statements.

## Quality gates

The Combo is complete only when all claims achieve $\ge \mathcal{L}_2$ proof, SHA-256 provenance is recorded in `EVIDENCE.md`, and `epistemic-verification-record.md` is emitted.

## Compound output

**Artifact:** `epistemic-verification-record.md`

**Ready for Mega Skill integration when:**

1. Every operational claim is classified and verified against the 6-Tier Epistemic Spectrum.
2. 100% of underlying files and data sources possess deterministic SHA-256 digests.
3. Quality gate issues formal authorization based on verified empirical or consensus proof.
