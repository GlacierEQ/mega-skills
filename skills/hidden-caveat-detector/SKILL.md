---
name: hidden-caveat-detector
description: "Detects caveats, disclaimers, qualifiers, verification language, and procedural framing that appear neutral but silently narrow scope, demote source facts, shift burdens, create hidden gates, stop execution, or alter source meaning. Use before durable mutations, legal/evidence summaries, handoffs, mission closure, and any output where caution language could materially change the user's source record or requested objective."
---

# Hidden Caveat Detector

## Purpose

Detect and neutralize **harmful hidden caveats**: language that presents itself as caution, precision, uncertainty, safety, verification, governance, or procedural hygiene while materially changing the source proposition, mission scope, burden of proof, status, priority, remedy, or next action.

This Skill does **not** remove legitimate uncertainty. It prevents uncertainty language from doing hidden substantive work.

## Core distinction

A caveat is **legitimate** when it accurately describes a real evidentiary, legal, safety, tool, jurisdictional, or procedural limit **without changing the underlying source record**.

A caveat is **harmful** when it silently does one or more of the following:

1. **Source dilution** — changes what the source/person actually said.
2. **Status demotion** — converts "not reopened this pass" into weak/speculative/quarantined/removed.
3. **Scope shrinkage** — narrows "build the full case" into a smaller/easier subset without explicit authority.
4. **Burden shifting** — makes the operator re-prove information already preserved or retrievable.
5. **Hidden veto/gate** — turns a checkpoint into a reason execution cannot continue.
6. **Context laundering** — lets a summary/compaction replace original journal/evidence meaning.
7. **Retrieval cutoff** — treats spelling/OCR/name variation or missing current attachment as a stop condition.
8. **Remedy suppression** — quietly removes a lawful theory/remedy because another route appears easier.
9. **Completion sabotage** — calls work complete at the first useful artifact while executable mission lanes remain.
10. **Authority inversion** — gives an opposing or institutional account default precedence without evidentiary reason.
11. **Caveat propagation** — a narrowly valid limitation spreads into unrelated facts, allegations, or work products.
12. **Semantic substitution** — replaces a factual proposition with the model's safer-sounding paraphrase.

## Trigger conditions

Run this Skill:

- before modifying a source-bearing durable record;
- before writing or updating MISSION.md, CONTEXT.md, EVIDENCE.md, HANDOFF.md;
- before major legal/evidence summaries or allegation matrices;
- before pruning, ranking, quarantining, superseding, or closing a proposition;
- before mission closure;
- whenever a proposed sentence contains uncertainty, disclaimer, safety, verification, procedural, or authority language that could affect substantive meaning;
- whenever the user has corrected a prior assistant caveat or minimization.

## Procedure

### 1. Lock the source proposition

Record the exact proposition, source wording, operator instruction, or mission requirement **before** evaluating caveats.

Never audit only the assistant's paraphrase.

### 2. Extract caveat candidates

Identify phrases functioning as:
- uncertainty qualifiers;
- verification qualifiers;
- safety/legal disclaimers;
- procedural gates;
- source-status labels;
- authority/status labels;
- completion conditions;
- scope exclusions;
- "only / merely / just / cannot / must first / pending / subject to" framing.

Keyword presence alone is not enough. Evaluate effect.

### 3. Run the semantic-delta test

For each caveat, ask:

**If this caveat is removed, what proposition/action remains?  
If this caveat is kept, what changed?**

Measure changes in:
- factual meaning;
- source status;
- scope;
- burden;
- priority;
- available theories/remedies;
- required next action;
- ability to continue execution;
- perceived credibility;
- identity/retrieval continuity.

### 4. Require a real justification

If a caveat changes substance, identify the authority for the change:

- stronger contrary evidence;
- current law;
- actual safety rule;
- actual tool/runtime limitation;
- jurisdiction/procedure;
- explicit operator instruction;
- proven identity mismatch;
- duplicate/supersession evidence.

"No current attachment," "I did not personally reopen it," "it sounds aggressive," or "a summary says otherwise" are **not** sufficient substantive justifications.

### 5. Localize legitimate caveats

When a caveat is genuinely necessary:

- attach it to the **analysis/status field**, not the source wording;
- state the exact reason;
- limit it to the exact proposition/effect it governs;
- create a concrete resolution target when resolvable;
- do not let it spread to neighboring facts or allegations.

Example:

**Source proposition:** "Erik has weapons."

Allowed analysis overlay:
> Source-access state: underlying weapon exhibit not reopened in this pass. Retrieval target: Flamingo audio/media.

Not allowed:
> Weapons allegation is unverified and quarantined.

### 6. Convert hidden caveats into explicit work

If the caveat represents a missing proof or unresolved question, create:

**CAVEAT → MISSING FACT → SOURCE/CUSTODIAN → ACQUISITION ROUTE → OWNER → NEXT ACTION**

Do not leave vague caution language where a retrieval task can replace it.

### 7. Preserve both source and analysis

Never overwrite the source layer. If a prior assistant-generated caveat already harmed the record:

- preserve the old artifact for provenance;
- mark its harmful effect;
- add the correction/supersession;
- restore the source proposition in the active case graph.

### 8. Audit completion language

Before declaring a mission complete, ask:

- Did "complete" secretly become "I produced one useful artifact"?
- Are there still materially executable lanes?
- Are remaining items actual blocked dependencies with named acquisition routes?
- Did a caveat hide unfinished work?

## Harm classes

| Code | Class | Example hidden effect |
|---|---|---|
| HC-01 | Source dilution | "She said X" → "She may have perceived X" |
| HC-02 | Status demotion | "Not reopened" → "unsupported/quarantined" |
| HC-03 | Scope shrink | "full lifecycle" → "draft one complaint" |
| HC-04 | Burden shift | asks user to reconstruct retrievable history |
| HC-05 | Hidden gate | "needs verification" → stop all work |
| HC-06 | Context laundering | compact summary replaces journal wording |
| HC-07 | Retrieval cutoff | alias/OCR variation ends search |
| HC-08 | Remedy suppression | easier claim silently replaces stronger parallel theory |
| HC-09 | Premature completion | first deliverable treated as mission finish |
| HC-10 | Authority inversion | official/opposing account gets unexplained default weight |
| HC-11 | Caveat propagation | one uncertain element weakens entire case |
| HC-12 | Semantic substitution | model rewrites source into "safer" meaning |

## Regression examples

### FAIL — harmful
Source:
> Operator firsthand fact: Erik had weapons.

Assistant mutation:
> Weapons allegation is speculative pending independent verification.

Why it fails:
Current-pass verification state was converted into a truth/status downgrade.

### PASS — localized
> Operator firsthand fact: Erik had weapons.  
> Current source-access state: native weapon exhibit has not yet been reopened in this pass. P0 retrieval target remains active.

### FAIL — hidden scope reduction
Mission:
> Build the full case through motions, exhibits, discovery, hearing, enforcement, and appeal preservation.

Assistant:
> I prepared the TRO, so the case build is complete.

### PASS
> TRO draft complete. Civil recovery, discovery, HPD record attack, exhibit compiler, and post-ruling routes remain active in the roadmap.

### FAIL — alias stop
> "Breisscher" differs from "Breisacher," so stop until identity is confirmed.

### PASS
> Search both variants and resolve identity through the event fingerprint; keep unrelated same-name matters separate.

### FAIL — journal laundering
> Replace historical journal wording with a cleaner synthesized version.

### PASS
> Preserve journal wording verbatim; create a separately labeled synthesis linked to the exact entry.

## Output contract

Produce `HIDDEN_CAVEAT_AUDIT.md` containing:

1. source proposition / mission requirement;
2. candidate caveat;
3. semantic delta;
4. harm class;
5. justification claimed;
6. justification actually established;
7. disposition: KEEP / LOCALIZE / REMOVE FROM ANALYSIS / SUPERSEDE;
8. resolution target;
9. affected durable artifacts;
10. post-audit wording/action.

For machine use, optionally emit `HIDDEN_CAVEAT_AUDIT.json`.

## Local validation

The Skill passes when:

- no caveat silently changes source meaning;
- every substantive limitation has an explicit basis;
- legitimate limitations are localized;
- unresolved caveats become executable evidence/work targets;
- source wording remains preserved;
- mission scope is unchanged unless explicit authority supports the change;
- no open executable lane is hidden behind completion language.

## Non-goals

- Do not suppress real uncertainty.
- Do not fabricate support.
- Do not hide contrary evidence.
- Do not bypass actual safety, legal, jurisdictional, or tool constraints.
- Do not force stronger external legal wording than the evidence supports.
- Do not treat the user's preferred framing as authority to make false factual or legal claims.

The goal is **precision without hidden surrender**.
