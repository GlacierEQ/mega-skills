---
id: court-evidence-compiler
display_name: Court Evidence Compiler
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Court Evidence Compiler

## Purpose and selection

Use this Combo Skill when raw electronic records, exhibits, or discovery materials must be authenticated, Bates-stamped, and compiled into a court-certified evidentiary exhibit packet. Do **not** use it when the work is informal note-taking or non-legal document editing.

## Incremental value

This Combo Skill turns loose document files into a court-admissible, self-authenticating evidentiary packet compliant with Federal Rules of Evidence 902(13)/(14). It adds cryptographic SHA-256 hash chaining, anomaly verification, and contiguous Bates stamping.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set litigation matter scope and rules | Target evidence directory | `MISSION.md` | Matter caption and court rules are explicit |
| 2 | `forensic-evidence-chain-core` | Skill | Yes | Scan anomalies, hash SHA-256, and stamp Bates | `MISSION.md` and evidence paths | `court-evidence-packet.md` | Every file has verified SHA-256 and Bates serial |
| 3 | `quality-gate` | Skill | Yes | Verify cryptographic integrity and PII scrub | Manifests and audit logs | Gate record | Zero hash mismatches and air-gapped PII scrub |

## Ordered execution

1. **Matter boundary — `mission-contract`** consumes target evidence paths and court rules, produces `MISSION.md`, and passes when Bates serial conventions and court standards are defined.
2. **Cryptographic audit — `forensic-evidence-chain-core`** consumes `MISSION.md`, produces `BATES_MANIFEST.json` and stamped exhibits, and passes when SHA-256 digests and serials are complete.
3. **Integrity gate — `quality-gate`** consumes manifests and anomaly logs, produces a gate record, and passes when all cryptographic digests and PII scrubs are validated.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `forensic-evidence-chain-core` | Evidence directory path, Bates prefix | Complete exhibit manifest and forensic timeline | litigation owner | Scope and Bates convention are explicit |
| `forensic-evidence-chain-core` | `quality-gate` | Manifests, hash digests, anomaly logs | Verified gate record | forensic owner | 100% SHA-256 verification and zero PII leaks |

## Evidence, risks, and state

The Combo must record all file hashes, Bates serial numbers, file sizes, and timestamps in its evidence register. It must not alter original evidentiary media or include unredacted sensitive PII. Update active state after each exhibit directory completes.

## Quality gates

The Combo is complete only when every exhibit file has a deterministic SHA-256 digest, Bates serials are strictly contiguous, anomaly scans report zero unexplained corruptions, and `court-evidence-packet.md` is emitted.

## Compound output

**Artifact:** `court-evidence-packet.md`

**Ready for Mega Skill integration when:**

1. Every exhibit has a verifiable SHA-256 digest.
2. Bates stamping is contiguous and collision-free.
3. FRE 902(13)/(14) self-authenticating affidavits are signed.

## State-law and journal-source correction — 2026-08-31

This Combo is **not limited to federal FRE 902(13)/(14)**. For a state-court mission, the governing state evidence rules and foundation methods control. Federal self-authentication methods may be useful analogies or separate federal routes but must not be represented as automatically controlling state admissibility.

For chat exports / regularly kept journal material:
- preserve the original journal/export file unchanged;
- assign hashes/source IDs to the original;
- create transcripts, OCR, Bates copies, excerpts, and redactions only as derivatives;
- keep exact pointers from every derivative excerpt to the original entry/context;
- do not let an evidentiary packet rewrite the source wording;
- treat authentication, hearsay, original-record/best-evidence issues, and business/journal-record theories as separate legal questions under the governing jurisdiction.

Bates numbering applies to exhibit **copies/derivatives**, not by altering original media.
