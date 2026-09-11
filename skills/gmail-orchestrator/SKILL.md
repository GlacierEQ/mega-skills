---
name: gmail-orchestrator
description: "Headless browser-based Gmail control for triage, drafting, and forensic extraction."
---


# Gmail Orchestrator

## Purpose

Headless browser-based Gmail control — no app, no OAuth dance beyond login:
- **Triage** — auto-label, archive, star by rule
- **Draft & Send** — compose emails via browser fill
- **Forensic Mode** — surgical extraction of target date-range emails

## Standard Procedure and Workflow

1. Configure authentication credentials or sessions in `~/.apex/connections.json`.
2. Select operational mode: `forensic` extraction, inbox `triage`, or LLM-guided `draft`.
3. Execute the orchestrator entrypoint with target date parameters or query filters.
4. Capture structured JSON receipts in the designated output path and verify SHA256 integrity.

## Forensic Mode — Case 1FDV-23-0001009
Default window: **April 15–18, 2025** (`casey.barton92@gmail.com`)

Captures: sender, recipient, subject, timestamp, snippet, message_id
Output: `/tasklet/gmail/forensic/CASE_20250415_20250418_1FDV-23-0001009.json`

Context: Coordinated password change (`bkitzcreig`), Google Meet API injection Apr 16 2025, simultaneous `glacier.equilibrium` access — digital surveillance evidence for THE_CATACLYSM / Void Ab Initio motion.

## Run

```bash
# Forensic extraction (default)
python skills/gmail-orchestrator/orchestrator.py forensic

# Triage
python skills/gmail-orchestrator/orchestrator.py triage

# Draft
python skills/gmail-orchestrator/orchestrator.py draft
```

## Setup
```json
// ~/.apex/connections.json
{
  "gmail": {
    "casey.barton92@gmail.com": {
      "password": "your_password"
    }
  }
}
```

*GlacierEQ APEX | June 2026*

