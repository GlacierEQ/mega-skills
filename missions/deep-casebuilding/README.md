# Deep Casebuilding Mission Scaffold

Durable mission workspace for the `deep-casebuilding` pipeline
(`pipelines/deep-casebuilding.json`). Clone this scaffold per matter: replace
the intake roots, drop evidentiary material into `intake/` and `audio/`, then
run the pipeline stages in dependency order.

## What the pipeline proves

1. **Integrity** — every intake file gets a deterministic SHA-256 digest
   (64KB chunks) and the tree is re-verifiable against its own manifest.
2. **Anomalies** — zero-byte files, magic-mismatched containers, permission
   drift, and byte-identical duplicate families are surfaced, not hidden.
3. **Bates discipline** — serials are assigned as a derivative-stamping plan
   with contiguity and collision verification; original media are never
   modified.
4. **Timeline** — event logs are checked for chronological inversions and
   duplicate-timestamp collisions.
5. **PII boundary** — findings carry match digests and line numbers, never
   copied sensitive values; redactions are written as derivative copies only.
6. **Custody** — audio artifacts are linked raw to transcript through a
   rolling SHA-256 chain.
7. **Court format** — transcripts compile to line-numbered, paginated,
   timestamped form and are verified for numbering, monotonicity, and word
   coverage.
8. **Cluster certification** — the three casebuilding skill suites
   (forensic-evidence-chain-core, audio-forensic-core, epistemic-gate) run as
   pipeline stages before the dossier compiles.

## Layout

| Path | Role |
|---|---|
| `case-intake.json` | Matter boundary: caption, court, roots, Bates prefix |
| `events.json` | Normalized event log for timeline verification |
| `fixtures/alignment.sample.json` | WhisperX-style alignment fixture used by the transcript/alignment stages |
| `fixtures/segments.sample.json` | Diarization fixture used by the diarization stage |
| `intake/` | Drop documentary evidence here (hashed, scanned, Bates-planned) |
| `audio/` | Drop audio evidence here (custody-chained) |
| `transcripts/` | Compiled transcripts land here |
| `pipeline-execution-manifest.json` | Durable resume state for the pipeline |

## Firewall

Execution posture stays `read_only`: the pipeline reads evidence, writes run
artifacts, and emits receipts. Filing, sending, deleting, deploying, and any
external mutation remain human-approval-gated.
