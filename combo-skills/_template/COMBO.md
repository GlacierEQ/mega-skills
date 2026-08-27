---
id: <combo-skill-id>
display_name: <Readable Combo Skill Name>
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# <Readable Combo Skill Name>

## Purpose and selection

Use this Combo Skill when <specific recurring mission pattern>. Do **not** use it when <clear counter-condition>; route to <alternative capability or direct execution> instead.

## Incremental value

This Combo Skill does not duplicate the lower-layer methods. It turns their verified outputs into <compound artifact> by adding <ordering, integration, or decision capability that no individual member owns>.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `<skill-or-external-id>` | Skill / external Skill | Yes / No | <bounded responsibility> | <input artifact> | <output artifact> | <test or inspection> |
| 2 | `<skill-or-external-id>` | Skill / external Skill | Yes / No | <bounded responsibility> | <input artifact> | <output artifact> | <test or inspection> |

## Ordered execution

1. **<Step name> — `<member-id>`** consumes <canonical inputs>, produces <named artifact>, and passes when <validation criterion>.
2. **<Step name> — `<member-id>`** accepts only <validated output>, produces <named artifact>, and passes when <validation criterion>.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `<member-id>` | `<member-id>` | <artifact IDs, constraints, decisions> | <format, required fields, quality threshold> | <named role> | <rejection and remediation rule> |

## Evidence, risks, and state

The Combo must record <sources/tests/artifacts> in its evidence register. It must not cross <approval, privacy, external-action, or source-of-truth boundary>. Update <state files or canonical registry> after <each named transition>.

## Quality gates

The Combo is complete only when the member outputs are verified, every handoff is closed or explicitly blocked, the compound artifact meets <quality standard>, and the next layer can consume it without relying on raw conversation history.

## Compound output

**Artifact:** `<compound-artifact>`

**Ready for Mega Skill integration when:**

1. <condition that proves the artifact is trustworthy>.
2. <condition that proves risks and assumptions are explicit>.
3. <condition that identifies the next compatible route>.
