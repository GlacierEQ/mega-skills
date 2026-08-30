---
name: voice-evidence-authenticator
description: 'Combo Skill: Voice Evidence Authenticator. Reusable capability chain.'
---

# Voice Evidence Authenticator

## Purpose and selection

Use this Combo Skill when Apple Voice Memos, court hearings, or witness audio recordings must be authenticated against acoustic grid frequencies (ENF), diarized by speaker, and transcribed with phonetic forced alignment under FRE 902(13)/(14). Do **not** use it for casual non-evidentiary transcription.

## Incremental value

This Combo Skill establishes an airtight evidentiary chain of custody for acoustic recordings. It adds Electric Network Frequency (ENF) grid validation, WhisperX phoneme alignment, pyannote speaker diarization, and 17-point court-certified transcript compilation.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set evidentiary criteria and court rule standards | Audio mandate | `MISSION.md` | Audio paths and court standards are explicit |
| 2 | `audio-forensic-core` | Skill | Yes | Run ENF validation, WhisperX, and diarization | `MISSION.md` and audio files | `audio-forensic-verification-record.json` | Phonetic alignment and ENF hum verified |
| 3 | `quality-gate` | Skill | Yes | Verify non-tampering and transcript formatting | Receipts and transcript | Gate record | Zero timeline drift; 17-point criteria passed |

## Ordered execution

1. **Evidentiary boundary — `mission-contract`** consumes audio file paths and target court rules, produces `MISSION.md`, and passes when court caption and evidence standards are defined.
2. **Acoustic and phonetic analysis — `audio-forensic-core`** consumes `MISSION.md`, produces `audio-forensic-verification-record.json`, and passes when ENF grid matching and word alignment succeed.
3. **Court certification gate — `quality-gate`** consumes transcripts and ENF certificates, produces a gate record, and passes when line numbering, speaker labels, and SHA-256 signatures are validated.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `audio-forensic-core` | Audio file path, recording date/time, court rules | Diarized phonetic transcript and ENF certificate | legal owner | Target audio paths and rules are explicit |
| `audio-forensic-core` | `quality-gate` | Verification record, line-numbered transcript | Verified gate record | forensic owner | ENF matches grid data and SHA-256 is verified |

## Evidence, risks, and state

The Combo must record all raw audio SHA-256 digests, ENF frequency variations, phoneme alignment timestamps, and speaker turn intervals in its evidence register. It must not alter original audio tracks. Update active state after each recording is processed.

## Quality gates

The Combo is complete only when ENF confirms absence of splices or timeline edits, WhisperX timestamps are aligned at word level, and `voice-evidence-record.md` is emitted.

## Compound output

**Artifact:** `voice-evidence-record.md`

**Ready for Mega Skill integration when:**

1. Raw audio SHA-256 digest is cryptographically recorded.
2. ENF acoustic analysis validates recording date and integrity.
3. Word-level phoneme transcript meets court line-numbering rules.
