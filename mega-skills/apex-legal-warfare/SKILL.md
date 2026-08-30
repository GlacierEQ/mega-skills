---
name: apex-legal-warfare
description: 'Mega Skill: apex-legal-warfare. End-to-end sovereign mission system.'
---

# APEX Legal Warfare Mega Skill

## Mission

Run complex multi-front litigation campaigns from discovery intake through forensic validation, Bates stamping, exhibit scheduling, and court-ready pleading compilation.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `court-evidence-compiler` when electronic exhibits require authentication | Manages court docket deadlines, FRE 902(13)/(14) evidentiary phase gates, and Bates stamping. |
| `long-horizon-core` | `automation-control` when court docket monitoring or PACER polling is scheduled | Orchestrates scheduled docket synchronization, filing reminders, and control-plane triggers. |

## Route algorithm

1. Begin the legal warfare campaign with `long-horizon-core` and load court docket rules (e.g. Hawaii Family Court Rule 3, FRCP).
2. Select `court-evidence-compiler` to authenticate and Bates-stamp all relevant discovery files in `LEGAL_DATA`.
3. Verify that 100% of referenced exhibits possess deterministic SHA-256 digests and contiguous Bates serials.
4. Select `automation-control` if ongoing PACER docket polling or notice monitoring is required.
5. Draft and compile formal court motions cross-referencing Bates exhibits with zero unverified factual assertions.
6. Reconcile signed declarations, exhibits, and filing receipts into `EVIDENCE.md` and deliver court-ready package.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` maintain immutable case state across state, federal, and administrative fronts.
