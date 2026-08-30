---
name: forensic-docket-intelligence
description: 'Combo Skill: Forensic Docket Intelligence. Reusable capability chain.'
---

# Forensic Docket Intelligence

## Purpose and selection

Analyzing court dockets, judicial minute orders, hearing audio recordings, and Bates exhibits to expose perjury or fraud upon the court.
Do **not** use when informal legal research or general case summaries.

## Incremental value

Comprehensive judicial docket forensics: links court docket timelines directly to phonetically aligned hearing transcripts, cryptographic Bates exhibits, and mathematical contradiction proofs.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `legal-powerhouse` | Skill | Yes | Structure court case matter, pleading taxonomy, and procedural rules. | Court case docket number, Matter filing history | CASE_DOCKET_INDEX.json, Pleading claim matrix | All docket entries and court orders indexed with filing timestamps. |
| 2 | `audio-forensic-core` | Skill | Yes | Perform WhisperX phonetic alignment, speaker diarization, and ENF validation. | CASE_DOCKET_INDEX.json, Hearing audio recordings | AUTHENTICATED_TRANSCRIPT.md, ENF frequency stability log | Audio transcription achieves 100% phonetic alignment with zero tampering. |
| 3 | `forensic-evidence-chain-core` | Skill | Yes | Verify SHA-256 digests, construct timelines, and stamp Bates exhibits. | AUTHENTICATED_TRANSCRIPT.md, Electronic exhibits | 00_FORENSIC_MASTER_TIMELINE.json, Bates manifest | Deterministic SHA-256 digests generated and Bates serials stamped. |
| 4 | `epistemic-gate` | Skill | Yes | Enforce L0-L6 epistemic standards on all legal assertions and claims. | 00_FORENSIC_MASTER_TIMELINE.json, Pleading claim matrix | EPISTEMIC_PROOF_LEDGER.json, Verified contradiction locks | All claims verified >= L2 behavioral / cryptographic truth level. |
| 5 | `quality-gate` | Skill | Yes | Certify evidentiary integrity, FRE 902(13)/(14) compliance, and impeachment proof. | EPISTEMIC_PROOF_LEDGER.json, Bates manifest | FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md, Evidentiary signoff | Dossier contains zero ungrounded assertions and satisfies FRE 902 standards. |

## Ordered execution

1. **Step 1 — `legal-powerhouse`**: Consumes Court case docket number, Matter filing history, produces CASE_DOCKET_INDEX.json, Pleading claim matrix, and satisfies: All docket entries and court orders indexed with filing timestamps.
2. **Step 2 — `audio-forensic-core`**: Consumes CASE_DOCKET_INDEX.json, Hearing audio recordings, produces AUTHENTICATED_TRANSCRIPT.md, ENF frequency stability log, and satisfies: Audio transcription achieves 100% phonetic alignment with zero tampering.
3. **Step 3 — `forensic-evidence-chain-core`**: Consumes AUTHENTICATED_TRANSCRIPT.md, Electronic exhibits, produces 00_FORENSIC_MASTER_TIMELINE.json, Bates manifest, and satisfies: Deterministic SHA-256 digests generated and Bates serials stamped.
4. **Step 4 — `epistemic-gate`**: Consumes 00_FORENSIC_MASTER_TIMELINE.json, Pleading claim matrix, produces EPISTEMIC_PROOF_LEDGER.json, Verified contradiction locks, and satisfies: All claims verified >= L2 behavioral / cryptographic truth level.
5. **Step 5 — `quality-gate`**: Consumes EPISTEMIC_PROOF_LEDGER.json, Bates manifest, produces FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md, Evidentiary signoff, and satisfies: Dossier contains zero ungrounded assertions and satisfies FRE 902 standards.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `legal-powerhouse` | `audio-forensic-core` | CASE_DOCKET_INDEX.json | AUTHENTICATED_TRANSCRIPT.md | legal-analyst |
| `audio-forensic-core` | `forensic-evidence-chain-core` | AUTHENTICATED_TRANSCRIPT.md | 00_FORENSIC_MASTER_TIMELINE.json | audio-forensic-specialist |
| `forensic-evidence-chain-core` | `epistemic-gate` | 00_FORENSIC_MASTER_TIMELINE.json | EPISTEMIC_PROOF_LEDGER.json | forensic-engineer |
| `epistemic-gate` | `quality-gate` | EPISTEMIC_PROOF_LEDGER.json | FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md | epistemic-auditor |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Cryptographic SHA-256 digests for all exhibits.
- Phonetic alignment timestamps with microsecond precision.
- Mathematical contradiction proof (e.g. 39-second timestamp impossibility).

Risk boundaries:
- Zero alteration of original audio or document exhibits.
- Strict PII scrubbing before any external model exposure.

## Quality gates

- All evidentiary assertions backed by Bates citations.
- FRE 902(13)/(14) self-authenticating affidavits completed.

## Compound output

**Artifact:** `FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md`

**Ready for Mega Skill integration when:**

1. Master timeline is locked with 100% cryptographic integrity.
2. Contradiction proofs and Bates manifests are verified by quality-gate.
