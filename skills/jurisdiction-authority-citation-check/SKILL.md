---
name: jurisdiction-authority-citation-check
description: "Verify controlling jurisdiction, actual procedure, legal authority, current rules, deadlines and exceptions before a legal email cites them."
---

# Jurisdiction Authority Citation Check

## Purpose

Produce authority-backed correspondence instead of unsupported legal threats or invented response duties.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Identify the exact custodian, request class, forum, administrative process, governing dates, requested remedy and whether this is a court filing, agency records request, employment outreach, police report, IG complaint or hearing.
2. Separate statutory law from regulations, agency rules/manuals, written institutional assurances and internal user checkpoints. Retain pinpoint subsection, authority URL/version/effective date and why it applies.
3. Use controlling primary authority first. For example, Hawaii agency UIPA records disputes may involve HRS chapter 92F and OIP review; federal agency FOIA may involve 5 U.S.C. 552 and agency regulations. These are examples, not presumptive coverage for courts, Navy IG protected records, criminal discovery or employment.
4. Check requested content against privacy, exemption, security-information, witness/record access, identity verification, claim/appeal deadlines and the rule's exceptions. Do not infer that one custodian must produce a different office's records.
5. Distinguish institution-promised response dates from mandatory statutory periods; apply clock start, tolling, holidays and venue only after official-source verification. If authority cannot be verified, omit conclusory citation and request a written basis.
6. Test strongest adverse view and lawful alternatives. Require a specific applicable rule before accusing obstruction, spoliation, misconduct, statutory violation or waiver.

## Negative and regression tests

- Reject: Misapplying FOIA to court audio
- Reject: Treating five-business-day acknowledgment estimate as statute
- Reject: Assuming lawful privacy denial proves wrongdoing
- Reject: Citation to outdated regulation or false pinpoint

## Output and acceptance

AUTHORITY_MATRIX.md with claim-to-authority mapping, jurisdiction, relevant exceptions, actual deadline computation and unresolved legal questions.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
