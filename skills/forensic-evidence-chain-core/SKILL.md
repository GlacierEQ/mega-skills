---
name: forensic-evidence-chain-core
description: "FRE 902(13)/(14) self-authenticating electronic record verification, cryptographic Bates numbering, and forensic anomaly detection."
---


# Forensic Evidence Chain Core

## Purpose

Audit, authenticate, and catalog electronic evidence, exhibits, and discovery records for federal and state court proceedings in strict compliance with Federal Rules of Evidence 902(13) and 902(14).

## Procedure

1. Scan candidate directory for zero-byte files, corrupted headers, and directory permission drift.
2. Verify timestamp continuity and detect chronological inversions against external event logs.
3. Compute deterministic NIST-standard SHA-256 digests across all target files in 64KB chunks.
4. Apply monotonic sequential Bates serials (`<PREFIX>-<SERIAL_NUMBER>`) to exhibits.
5. Pass metadata through air-gapped PII scrubber (`apex_scrubber.py`).
6. Emit tamper-proof `BATES_MANIFEST.json` and forensic timeline records.

## Output contract

Produce `BATES_MANIFEST.json` and `00_FORENSIC_MASTER_TIMELINE.json` with exhibit schedules, Bates serial ranges, deterministic SHA-256 digests, and digital certification receipts.

## Local validation

The procedure passes only when 100% of candidate files have verified SHA-256 digests, zero undocumented anomalies exist, and Bates serials are strictly contiguous.

## Non-goals

Do not alter original evidentiary media. Do not include unredacted sensitive PII. Do not fabricate exhibit provenance.
