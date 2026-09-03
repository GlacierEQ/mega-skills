# HANDOFF — Anthropic Applied AI

## Verified durable state

- Generic `pipeline-compositor` runtime is on `main`.
- `scripts/career_evidence_backbone.py` compiles and verifies the career evidence graph.
- `schemas/career-evidence.schema.json` defines the source registry contract.
- `evidence-sources.json` contains the first six inspected source systems.
- `evidence-ledger.json` contains 11 typed evidence records.
- `linkedin-backbone.json` and `LINKEDIN_BACKBONE.md` are the current evidence-bound LinkedIn projection.
- `linkedin-activation.json` tracks recommendations, endorsements, Open-to-Work, identity verification, portfolio gateway, activity topics, and manual profile checks.
- Anthropic pipeline now contains target compile/verify, evidence build/verify, LinkedIn projection/verify, and activation verification stages.

## Current evidence coverage

7 / 10 Anthropic competency domains have evidence.

Open domains:

1. customer discovery and problem decomposition
2. enterprise integration and security
3. ambiguous-environment execution

## Exact next action

Run **gap closure by retrieval first**.

Search existing Job App Helix, public portfolio repositories, Tower of Babel, Mega-Skills, connector/control-plane work, deployment receipts, and verified project history for source artifacts that legitimately support the three open domains.

For every useful artifact, append a typed source/claim to `evidence-sources.json`, rebuild `evidence-ledger.json`, verify it, and regenerate LinkedIn projection.

Only if retrieval leaves a real gap should a new engineering proof build be created.

## LinkedIn operator actions tracked but not fabricated

- request real recommendations
- concentrate endorsements
- set explicit Open-to-Work location/workplace/employment preferences
- complete identity verification if available
- verify photo/banner/contact/custom URL
- publish evidence-linked technical activity

## Do not restart

Continue from this evidence graph. Do not rewrite the profile from scratch and do not create claims outside the ledger.
