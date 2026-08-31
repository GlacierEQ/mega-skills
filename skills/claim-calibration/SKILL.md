---
name: claim-calibration
description: "Match a capability’s wording and decision confidence to the evidence actually available. Use when a Skill, Combo, Mega, report, or user-facing artifact makes strong operational, security, legal, scientific, or quality claims."
---


# Claim Calibration

## Purpose

Prevent the system from representing intent, design, or partial evidence as proven outcome. This Skill owns claim scope and uncertainty language; it does not replace domain validation or legal, scientific, security, or operational review.

## Procedure

1. Extract each material claim and label it as observed fact, derived conclusion, tested behavior, design intent, assumption, or open question.
2. For every claim, identify the exact supporting artifact, test, environment, revision, and limitation.
3. Replace absolute or universal wording with scoped language when evidence is partial, conditional, environment-specific, or absent.
4. Escalate any claim that implies legal certification, security guarantee, safety clearance, forensic authenticity, medical result, financial outcome, or external effect without the required qualified evidence.
5. State what the evidence does not establish and name the next validation needed for stronger language.
6. Record the approved wording and review trigger in the evidence register or a dedicated claim-boundaries artifact.

## Output contract

Produce `CLAIM_BOUNDARIES.md` containing original claim, classification, evidence references, approved scoped wording, limitations, owner, and next validation.

## Local validation

The output passes when each material statement can be traced to evidence with a matching scope and a reviewer can distinguish verified behavior from future intent.

## Non-goals

Do not suppress real uncertainty, convert a disclaimer into proof, or provide professional certification outside the required qualified process.
