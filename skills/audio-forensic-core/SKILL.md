---
name: audio-forensic-core
description: "Sovereign evidentiary audio processing, WhisperX phonetic alignment, speaker diarization, Electric Network Frequency (ENF) validation, and 17-point court transcripts."
---


# Audio Forensic Core

## Purpose

Process evidentiary voice memos, court recordings, and witness statements with word-level phonetic alignment, speaker diarization, acoustic ENF tamper verification, and 17-point court-certified transcript generation under FRE 902(13)/(14).

## Procedure

1. Ingest raw evidentiary audio files (`.m4a`, `.wav`, `.mp3`).
2. Extract Electric Network Frequency (ENF) 60Hz acoustic hum to verify recording timestamp and continuity against regional power grid databases.
3. Execute WhisperX word-level forced phonetic alignment for sub-second timestamping.
4. Perform speaker diarization using pyannote acoustic clustering.
5. Compute deterministic SHA-256 digests across raw audio, intermediate features, and final transcripts.
6. Generate 17-point court-certified transcript with line-numbered margins compliant with Hawaii Family Court Rule 3.

## Output contract

Produce `audio-forensic-verification-record.json` and court-certified PDF transcripts with ENF authenticity certificates and SHA-256 signatures.

## Local validation

The procedure passes only when phonetic alignment has zero timeline drift, ENF acoustic hum confirms non-tampering, and speaker turns are verified.

## Non-goals

Do not alter original audio tracks. Do not synthesize or smooth audio waveforms.
