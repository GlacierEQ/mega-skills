---
name: mega-skill-forge
description: Design, validate, and register a Mega Skill that orchestrates multiple Combo Skills into a bounded, evidence-backed end-to-end mission system. Use when a requested workflow needs mission-wide route selection, durable state, recovery, and integration beyond any single Combo Skill.
---

# Mega Skill Forge

## Use this skill when

Use this skill to create a **Mega Skill**, not a broad relabeling of an existing procedure. A candidate Mega Skill must coordinate at least two resolved Combo Skills, add mission-wide sequencing and recovery, and output a compound artifact that none of its Combos can produce independently.

Read `references/mega-contract.md` before drafting. Read `references/release-checklist.md` before committing a repository change. Use `templates/MEGA.md` and `templates/mega-registry-entry.json` instead of starting the contract from scratch.

## Decision gate

Do not create a Mega Skill if any answer is no:

1. Are at least two existing Combo Skills necessary for the requested outcome?
2. Can their selection criteria, inputs, and compound artifacts be made explicit?
3. Does the proposed layer add mission-wide state, cross-Combo sequencing, recovery, or evidence integration that the Combos do not already own?
4. Can `capability-readiness` be selected before any advanced route with unverified dependencies, access, runtime, data, or claim scope?
5. Can consequential external actions remain behind user approval and a guarded route?

If the first three answers are no, improve or create a lower-layer Skill or Combo instead. If the last two are no, mark the candidate blocked and produce the missing-precondition plan; do not write an active Mega contract.

## Creation workflow

1. **Inspect before design.** Pull the target repository; read its Skills, Combo registry, Mega registry, validator, test suite, and any existing related contracts. Record current revision and unresolved gaps.
2. **Write a mission contract.** State the intended user outcome, selection boundary, non-goals, final artifact, durable state, approval boundary, recovery rule, and what the Mega layer adds beyond each selected Combo.
3. **Choose resolved Combos.** Select the smallest set of existing Combo IDs. Never invent a member, silently nest unregistered workflows, or duplicate a Combo procedure inside the Mega contract.
4. **Gate advanced routes.** Add `capability-readiness` as a conditional Combo. For recurring, event-driven, or external-effect work, select a guarded route only after a mission-specific preflight and the applicable approval.
5. **Author the contract.** Copy `templates/MEGA.md`, then describe selection criteria and the route algorithm in terms of named Combo artifacts—not inferred conversation history.
6. **Register the Mega.** Copy `templates/mega-registry-entry.json`; set a unique ID, semantic version, resolved `required_combos`, conditional Combos, mission output, and five durable-state artifacts.
7. **Prove hierarchy integrity.** Run the repository’s validator and regression suite. Add a focused regression test for the new Mega’s required Combos, readiness route, entrypoint, and final artifact.
8. **Release deliberately.** Review the diff, record validation evidence, commit, and push only when the user has authorized repository changes. Deliver the entrypoint and the exact commit.

## Modification workflow

Treat a changed Mega contract as a compatibility change. Inspect dependent registries and routes first. Preserve existing IDs unless an explicit migration is documented. Update the contract, registry, tests, and release evidence together; do not adjust only the prose.

## Quality standard

An acceptable Mega Skill has a **real integration delta**. Its final record lets an uninvolved operator reconstruct the chosen route, readiness decision, inputs, compound artifacts, acceptance gates, residual uncertainty, approval state, and next recoverable action. It never claims execution, safety, certification, or completeness beyond the evidence in its named artifacts.

## Resources

| Resource | Use |
|---|---|
| `references/mega-contract.md` | Define the layer boundary and required contract fields. |
| `references/release-checklist.md` | Run before release to protect graph integrity and provenance. |
| `templates/MEGA.md` | Draft an executable Mega contract with bounded orchestration. |
| `templates/mega-registry-entry.json` | Add the canonical registry representation. |

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Manus for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Manus's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Manus should reference while working.

### templates/
Files not intended to be loaded into context, but rather used within the output Manus produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
