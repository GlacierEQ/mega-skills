# Mission 1FDV-23-0001009 — Deep Casebuilding (Live Instance)

Live wiring of the `deep-casebuilding` pipeline to the 1FDV-23-0001009
evidence estate. Pipeline contract: `pipelines/1fdv-deep-casebuilding.json`.
Runner: `python3 scripts/run_pipeline.py pipelines/1fdv-deep-casebuilding.json`.

## What is wired

- **Case intake** — `case-intake.json`: caption Barton v. Barton, Family Court
  of the First Circuit, Bates prefix `1FDV`, source systems (Dropbox
  `/APEX/EVIDENCE/AUDIO/`, iCloud `UNIFIED_FORENSIC_LIBRARY/04_AUDIO`, Notion
  inventory).
- **Exhibit register** — `exhibits.json`: the six EX-AUD recordings with
  actors, priorities, custody status, and source locations, consumed directly
  by the audio exhibit-serial planner stage.
- **Event log** — `events.json`: the seven NEF-verified docket events
  (Dkt 213/215/217/219/221/223/225) for timeline-inversion verification.

## Custody law for this mission

Original media stay in Dropbox/iCloud, untouched. Only working copies dropped
into `intake/` and `audio/` are hashed, anomaly-scanned, PII-scanned,
Bates-planned, and custody-chained. The pipeline is `read_only` over evidence
and fail-closed: any stage that cannot verify exits non-zero and stops the run.

## Open integrity flag (surfaced, not hidden)

`1FDV-23-1009_EX-AUD-001` carries **two conflicting SHA-256 records** in the
workspace (inventory `9086d292…` vs P1 task row `faab712a…`, with different
file descriptions). Re-hash the custodial original and reconcile the register
before any filing use of that exhibit. The pipeline's anomaly philosophy:
surface, never silently resolve.

## Runbook

1. Copy (never move) evidence into `intake/` and audio working copies into `audio/`.
2. `python3 scripts/run_pipeline.py pipelines/1fdv-deep-casebuilding.json`
3. Interrupted runs resume: add `--resume` (completed resume-safe stages skip).
4. Dossier lands at `missions/1fdv-23-0001009/DEEP_CASEBUILDING_DOSSIER.json`
   with the manifest chain root, transcript pagination, alignment and
   diarization verdicts.
