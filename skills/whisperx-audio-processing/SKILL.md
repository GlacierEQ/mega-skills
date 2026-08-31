---
name: whisperx-audio-processing
description: "Process audio files through WhisperX (3-engine consensus transcription). Generates transcripts with SHA-256 Chain of Custody hashes and timestamps for forensic authentication."
---


# WhisperX Audio Processing Skill

## Overview
Autonomous audio processing pipeline: upload audio → WhisperX consensus → CoC hash → archive. Generates forensically authenticated transcripts with immutable provenance records.

## Architecture

```
Notion Audio Upload (Status="pending")
    ↓
Aspen Grove Trigger (30s poll)
    ↓
WhisperX (port 8008) — 3-engine consensus
  ├─ Engine 1: Whisper-Large
  ├─ Engine 2: Whisper-Medium
  └─ Engine 3: Confidence threshold
    ↓
CoC Hash (SHA-256 + timestamp)
    ↓
Notion WhisperX DB ← Write transcript + hash
```

## Engines
1. **Whisper-Large** — High accuracy, slower
2. **Whisper-Medium** — Balanced
3. **Confidence Threshold** — Consensus voting

**Consensus Rule**: Pass only if 2/3 engines agree; flag conflicts.

## Trigger Configuration

### Notion Setup
- Create column: `Status` (enum: "pending", "processing", "complete")
- Create column: `Transcript` (text)
- Create column: `CoC_Hash` (text — SHA-256)
- Create column: `Processed_At` (date)

### Service
- File: `aspen-grove-operator-v7/services/notion_audio_webhook.py` (PR #18 merged)
- Port: 8008 (WhisperX backend)
- Poll interval: 30 seconds

## Process

### 1. Upload to Notion
```
Audio file → Notion attachment
Status → "pending"
```

### 2. Trigger Poll
```python
# Every 30s: GET /ELYSIUM_AUDIO_DB
# Filter: Status="pending" AND attachment exists
```

### 3. Download & Process
```bash
# Route to WhisperX port 8008
# 3-engine consensus transcription
# Output: transcript.txt
```

### 4. Compute Chain of Custody
```python
coc_hash = SHA256(
  transcript_text + 
  timestamp_iso8601 + 
  original_filename
)
# Result: immutable forensic record
```

### 5. Write Back to Notion
```
Transcript → Notion.Transcript
CoC_Hash → Notion.CoC_Hash
Status → "complete"
Processed_At → now()
```

## Outputs
- **transcript.txt** — Full transcription
- **coc_record.json** — {hash, timestamp, source_file}
- **consensus_report.md** — Engine agreement %
- **forensic_archive/** — Immutable records

## Chain of Custody Fields
```json
{
  "original_audio": "filename",
  "transcript_hash": "SHA-256(transcript)",
  "timestamp_utc": "2026-06-22T10:54:00Z",
  "whisperx_version": "1.4.0",
  "engines_consensus": ["Whisper-Large", "Whisper-Medium"],
  "confidence_threshold": 0.95
}
```

## Use When
- Processing audio evidence for legal cases
- Authenticating oral depositions/interviews
- Building forensic-grade transcripts
- Maintaining Chain of Custody for discovery
