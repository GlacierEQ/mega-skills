---
name: evidence-register
description: "Build a traceable register of sources, tests, artifacts, claims, and uncertainty. Use when conclusions, implementation decisions, or deliverables must be verified, cited, audited, or safely resumed."
---


# Evidence Register

## Purpose

Maintain the factual substrate of a mission. This Skill owns traceability: what was observed, how it was checked, what conclusion follows, and what remains unknown.

## Procedure

1. Assign a stable ID to each relevant source, test, artifact, approval, or observed system result.
2. Record origin, retrieval time or revision, scope, reliability limit, and location for every item.
3. Distinguish observation, derived conclusion, assumption, allegation, and open question.
4. Map every material claim to the supporting evidence IDs and the verification method.
5. Preserve failing tests, rejected alternatives, and contradictions rather than overwriting them.
6. Update the register whenever new evidence changes a decision, risk rating, or next action.

## Output contract

Produce `EVIDENCE.md` with an item register, a claims trace, test outcomes, unresolved evidence gaps, and stable links or paths to artifacts.

## Local validation

The register passes when a reviewer can trace every material final claim to evidence or a declared assumption, reproduce the stated test result where applicable, and identify what evidence is missing.

## Non-goals

Do not treat search snippets, documentation claims, model inference, or an unexecuted command as verified behavior.

## Source Preservation Invariant — 2026-08-31

Evidence registration must preserve **source content state** separately from **analytical/verification state**.

For every material historical assertion or journal entry, store when available:
- stable source ID;
- exact source path/location;
- original wording or immutable pointer;
- speaker/creator;
- timestamp/order;
- source type (original, firsthand, journal, official record, derivative, OCR, prior work product);
- current attachment/access state;
- corroborating sources;
- contrary sources;
- unresolved acquisition target.

Rules:
1. `NOT_REOPENED_THIS_PASS` is not a truth downgrade.
2. Never overwrite a source assertion with the model's later paraphrase.
3. Preserve rejected/superseded claims with the evidence and reason for disposition.
4. Duplicate retellings do not automatically become independent corroboration.
5. Contradictions must produce discriminating-evidence targets.
6. A regularly kept journal/chat export retains original wording and sequence as source evidence; legal admissibility is assessed separately.
