# APEX Voice Forensics Mega Skill

## Mission

Execute end-to-end evidentiary audio processing for Apple Voice Memos and court recordings, verifying acoustic authenticity via Electric Network Frequency (ENF), generating word-level phonetic alignment, and producing court-certified 17-point transcripts under FRE 902(13)/(14).

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `voice-evidence-authenticator` when audio recordings require ENF authentication and phonetic alignment | Manages forensic chain of custody, sub-second timestamp alignment, and acoustic tamper verification. |
| `long-horizon-core` | `court-evidence-compiler` when transcripts must be incorporated into court exhibit schedules | Binds certified transcripts and ENF certificates into Bates-stamped legal filing packages. |

## Route algorithm

1. Begin the voice forensics mission with `long-horizon-core` and load evidentiary recording metadata.
2. Select `voice-evidence-authenticator` to extract ENF frequency curves, run WhisperX, and perform speaker diarization.
3. Validate that ENF frequency fluctuations match regional power grid data to prove recording time and non-tampering.
4. Select `court-evidence-compiler` to apply contiguous Bates serials and compile FRE 902(13)/(14) affidavits.
5. Reconcile raw audio SHA-256 digests, ENF certificates, and 17-point line-numbered transcripts into `EVIDENCE.md`.
6. Deliver court-certified evidentiary audio package ready for judicial submission.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` maintain immutable forensic state across evidentiary audio processing phases.
