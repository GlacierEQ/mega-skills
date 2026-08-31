---
name: cross-app-pipeline
description: "Master orchestration connecting iCloud Voice Memos, Gmail, Notion, and THE_CATACLYSM evidence vault."
---


# Cross-App Pipeline — GlacierEQ APEX

## Overview
Master orchestration skill connecting iCloud Voice Memos → Gmail → Notion → THE_CATACLYSM evidence vault.

## Architecture
```
iCloud Voice Memos
    │
    ▼
Harvester (browser → icloud.com)
    │
    ▼
WhisperX Transcription (whisperx-audio-processing skill)
    │
    ▼
Classifier
  ├─ LEGAL    → /tasklet/cataclysm/evidence/
  ├─ EMAIL    → /tasklet/gmail/drafts/  (→ Gmail orchestrator)
  └─ PERSONAL → /tasklet/notion/queue/ (→ Notion sync skill)

Gmail Orchestrator (parallel)
  ├─ Forensic mode: Apr 15-18 2025 extraction (Case 1FDV-23-0001009)
  └─ Triage mode:   inbox labeling, archiving
```

## Skills Used
- `icloud-voice-memos/harvester.py`
- `whisperx-audio-processing/`
- `gmail-orchestrator/orchestrator.py`
- `notion-sync-automation/`

## Run Modes
```bash
# Full pipeline
python skills/cross-app-pipeline/pipeline.py

# Skip voice memos, forensic only
python skills/cross-app-pipeline/pipeline.py --no-voice --no-triage

# Skip forensic, voice + triage only
python skills/cross-app-pipeline/pipeline.py --no-forensic
```

## Credentials
All credentials loaded from `~/.apex/connections.json` or env vars.
See `config/connections.example.json` for required keys:
- `apple.apple_id`
- `apple.password`
- `gmail.casey.barton92@gmail.com.password`

## Forensic Output
All forensic extractions deposited to:
```
/tasklet/cataclysm/evidence/     ← LEGAL-classified Voice Memos
/tasklet/gmail/forensic/         ← Gmail forensic extraction JSON
```
Case ref: `1FDV-23-0001009` | THE_CATACLYSM

---
*GlacierEQ APEX | Built: June 2026*

