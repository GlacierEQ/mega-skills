---
name: legal-issue-assessment-matrix
description: "Reusable legal orientation layer: represent each potentially material issue beside the Operator's own assessment of what actually happened before deeper element, evidence, authority, remedy, or strategy analysis."
---

# Legal Issue / My Assessment Matrix

## Mission

Use a compact two-column **Issue / My assessment** matrix as an orientation layer for legal scenarios whenever it improves clarity.

The matrix is designed to keep the system anchored to what the Operator says actually happened while contrasting that reality with the more serious condition, deprivation, failure, intent, duration, prejudice, or evidentiary state that a legal issue would require.

This layer does **not** replace chronology, evidence, source provenance, contracts, statutes, cases, actor attribution, element mapping, damages, remedies, or adversarial testing. It gives those deeper layers a clean factual orientation.

## Core Form

| Issue | My assessment |
|---|---|
| Potentially material condition, event, omission, deprivation, allegation, or element | Operator-authored assessment of what actually happened, including presence, absence, degree, duration, cure, mitigation, uncertainty, or lack of support |

The right-hand column is the **Operator's assessment**, not an assistant-generated conclusion. Preserve the Operator's wording and meaning. Assistant legal analysis belongs in a separate analysis layer.

## Why This Exists

Use the matrix to make distinctions that legal analysis commonly blurs, including:

- inconvenience vs. deprivation;
- allegation vs. evidence;
- temporary defect vs. continuing failure;
- defect vs. habitability or functionality failure;
- delay vs. denial;
- adverse outcome vs. bad faith;
- presence vs. prevention of use;
- remediated condition vs. ongoing condition;
- technical violation vs. material prejudice;
- asserted damage vs. documented expense or loss;
- firsthand fact vs. reported third-party statement;
- source conflict vs. Operator instruction conflict.

## Operator Authority

1. The Operator's own firsthand statements are the primary factual authority for the Operator's experiences, observations, chronology, intentions, decisions, corrections, and positions inside the Operator's system.
2. Do not downgrade an Operator firsthand statement merely because independent corroboration has not yet been retrieved. Lack of corroboration is not evidence against the Operator.
3. External evidentiary burdens are separate. Court, agency, publication, or third-party proof may require documentary corroboration without changing the internal Operator record.
4. Assistant or agent wording is analysis only. Do not populate `My assessment` from assistant prose unless the Operator later carries that position forward in the Operator's own words.
5. Silence, non-response, or exposure to assistant analysis is not adoption.

## Required Workflow

### 1. Recover source-bearing facts

Load the materially relevant Operator-authored chronology, corrections, source documents, evidence pointers, and governing agreement or authority before composing the matrix.

### 2. Build the orientation matrix

For each materially relevant issue, state the issue neutrally enough to test it and place the Operator's actual assessment beside it.

Do not inflate an incidental fact into a grievance. Do not minimize a condition the Operator treats as serious. Preserve qualifiers such as `apparently`, `about`, `none described`, `I don't see it`, `I don't care`, or similar language when they carry meaning.

### 3. Pointer-link; do not duplicate

Facts and evidence should be stored once under stable identity and provenance. Matrix rows point to them.

A row may link across multiple dimensions:

```json
{
  "issue_id": "ISSUE-0001",
  "matter_ids": ["MATTER-..."],
  "actor_ids": ["ACTOR-..."],
  "fact_pointers": ["FACT-..."],
  "event_pointers": ["EVENT-..."],
  "evidence_pointers": ["EVIDENCE-..."],
  "operator_assessment": "...",
  "operator_assessment_source": "SOURCE-SPAN-...",
  "legal_element_pointers": ["ELEMENT-..."],
  "authority_pointers": ["AUTHORITY-..."],
  "remedy_pointers": ["REMEDY-..."]
}
```

The same fact may legitimately feed multiple cases, actors, issues, or theories through explicit pointers. Do not physically copy or relocate the fact merely for organizational convenience.

### 4. Resolve material gaps actively

`Unresolved` is not a parking state. If a row exposes a material ambiguity, contradiction, missing linkage, attribution gap, or source conflict:

1. search materially relevant Operator history and source-bearing records;
2. inspect files, provider-native records, timelines, metadata, memory/context, and authoritative external records where relevant;
3. route around individual failed lookup paths;
4. determine whether the question materially matters;
5. if it does not matter, stop amplifying it;
6. if only the Operator can answer it, ask the narrow question;
7. if the answer belongs to an opposing party, custodian, institution, agency, or provider, convert it to an external resolution/acquisition target.

A failed lookup is a route failure, not a factual conclusion.

### 5. Keep deeper legal analysis separate

After the matrix is stable enough to orient the matter, separately map:

- controlling contract or policy text;
- statutory/regulatory elements;
- case authority;
- evidence supporting or weakening each element;
- actor/action/authority/causation;
- defenses and rebuttals;
- damages and prejudice;
- remedies;
- discovery and acquisition targets;
- procedural posture and deadlines.

Do not silently rewrite the Operator's assessment merely because the legal analysis becomes more detailed.

## Contradictory Operator Instructions or Positions

When the Operator's current instruction, position, priority, scope, strategy, or authority statement materially contradicts an earlier Operator-authored one, do not average or reconcile them internally.

Surface:

```text
BEFORE: "<verbatim earlier Operator words>"
NOW: "<verbatim current Operator words>"
CONFLICT: <exact point that cannot simultaneously control>
```

The Operator then determines whether the current statement overrides the prior one, the prior still controls, the position changed over time, or both apply under different scopes or conditions. Once clarified, remove the superseded instruction from the active execution path while retaining historical lineage.

This protocol is different from a factual conflict between sources, which should be investigated through evidence and provenance.

## Suggested Matrix Dimensions

Not every matter needs every row. Consider issues involving:

- access / possession / use;
- notice / opportunity to cure;
- duration;
- remediation;
- functionality;
- sanitation / safety;
- interference;
- causation;
- expense / economic loss;
- physical or emotional harm where actually asserted;
- intent / knowledge / bad faith;
- reliance;
- mitigation;
- documentation;
- prejudice;
- procedural compliance;
- evidentiary support;
- continuing vs. cured condition.

## Storage and Retrieval Model

Prefer typed coordinates over free-form tag proliferation:

- `matter:`
- `actor:`
- `entity:`
- `role:`
- `event:`
- `issue:`
- `claim:`
- `evidence:`
- `source:`
- `document:`
- `financial:`
- `damage:`
- `remedy:`
- `date:`
- `status:`
- `authority:`

Store once. Identify once. Link many. Retrieve hierarchically.

## Do Not

- Do not turn assistant analysis into the Operator's assessment.
- Do not infer bad faith, motive, illegality, damages, or severity merely to fill a row.
- Do not erase qualifiers in the Operator's wording.
- Do not treat absence of independent corroboration as a reason to distrust the Operator.
- Do not let an open question become an excuse to stop when a tool/source path can resolve it.
- Do not duplicate facts across case folders when pointers can represent the relationship.
- Do not keep superseded Operator instructions active after the Operator resolves their authority.
- Do not use this matrix as a substitute for legal authority or evidence analysis.

## Completion Check

A strong legal scenario review should be able to answer, at a glance:

1. What are the potentially material issues?
2. What does the Operator say actually happened for each one?
3. Which facts and evidence objects support each row?
4. Which allegedly more serious conditions are absent, present, temporary, cured, disputed, or unsupported according to the Operator's account?
5. What deeper legal/evidentiary work remains after the orientation layer?

The matrix succeeds when it makes the matter easier to reason about **without changing the Operator's reality into the agent's narrative**.
