---
name: casebuild-mesh-organization
description: Organize legal cases across GitHub and connected clouds with stable IDs, provenance, hashes, chronology, review routing, reconciliation, and recoverable checkpoints. Use for case setup, evidence inventory, cross-system linking, or completion audits.
---

# Casebuild Mesh Organization

## Purpose

Turn a scattered legal matter into a navigable, integrity-aware case mesh without flattening its repositories, cloud stores, review systems, or source records into one authority. This Skill owns the organization procedure and emits a `CASEBUILD_MESH_REGISTER.md`; it does not decide litigation strategy, draft persuasive filings, or alter original evidence.

## Governing rules

1. **Preserve plurality.** Treat repositories, cloud stores, task systems, databases, and review workspaces as peer nodes with distinct roles and provenance.
2. **Operational home is not architectural authority.** Select the strongest current navigation route, but link other nodes bidirectionally rather than replacing them.
3. **Source is not summary.** Preserve originals and immutable source pointers. OCR, transcripts, redactions, excerpts, Bates copies, and analyses are derivatives.
4. **Identity before interpretation.** Record stable case/evidence IDs, source-system IDs, locators, byte sizes, and SHA-256 hashes where applicable before relying on content.
5. **Contradictions create work.** Preserve conflicting assertions and open a discriminating-evidence target; never silently harmonize them.
6. **Safety at action edges.** Internal reading, indexing, hashing, mapping, and drafting may proceed autonomously. Filing, sending, deleting, merging, public release, privilege waiver, and irreversible mutations require the appropriate human authorization.
7. **Attorney boundary.** Support neutral evidence-to-element mapping, gaps, witnesses, discovery, exhibit infrastructure, and review packets. Attorneys own persuasive legal prose, filing choices, and litigation strategy.

## Inputs

- Matter identifier, caption, jurisdiction, and known deadlines
- Accessible repositories and cloud/system nodes
- Existing case homes, checkpoints, manifests, indexes, review queues, and source receipts
- Original or derivative evidence locators
- Sensitivity, privilege, access, and retention constraints

## Procedure

### 1. Establish the matter contract

Record the case ID, observable outcome, scope, exclusions, governing jurisdiction, stakeholders, decision owners, external-action approvals, and completion test. Unknown facts remain explicitly unknown.

### 2. Map the living node graph

For every accessible node, record:

- node ID, service, locator, and access state;
- role in the mesh;
- sensitivity and retention constraints;
- inbound/outbound links;
- last verification timestamp;
- stale, inaccessible, duplicate, or orphaned state.

Select a preferred operational route based on current case density, verified checkpoints, provenance coverage, navigation quality, and safe change workflow. Document that this is an operational preference only.

### 3. Build the evidence identity layer

Assign stable evidence IDs without renaming or modifying original media unless separately authorized. For each item record:

- case ID and evidence ID;
- title and neutral description;
- evidence type and original/derivative status;
- source system, source-system ID, exact locator, custodian, and acquisition time;
- SHA-256, byte size, and integrity state where applicable;
- parent evidence ID for every derivative;
- people/entities, event or docket relationship, sensitivity, and review status;
- last verified time and unresolved exception.

A matching filename is not proof of identity. Provider names and folders are locators, not authentication.

### 4. Separate source, derivative, and analysis lanes

Keep originals immutable. Store every transformation as a derivative with parent linkage, method, timestamp, operator/process, input hash, output hash, and validation result. Keep attorney work product and privileged materials in appropriately restricted nodes.

### 5. Construct navigation views

Build linked, source-cited views rather than new unsupported facts:

- master chronology;
- docket/filing index;
- people and entity index;
- evidence register;
- integrity/chain-of-custody ledger;
- issues and legal-element matrix;
- witness register;
- discovery and acquisition queue;
- exhibit/production register;
- attorney review and decision queue.

Every material chronology or matrix statement must point to evidence IDs and source locators. Mark allegation, observed fact, derived conclusion, assumption, contradiction, and open question distinctly.

### 6. Reconcile across systems

Detect and report:

- evidence present in one node but absent from the register;
- stale links, renamed paths, missing source-system IDs, and hash mismatches;
- derivatives without parents or transformation receipts;
- duplicate files with conflicting metadata;
- conflicting review states or deadlines;
- completed tasks whose artifacts are missing;
- source assertions omitted or altered by summaries;
- sensitive items exposed beyond their intended access boundary.

Repair non-destructive metadata and links when safe. Route content conflicts, access problems, integrity anomalies, and consequential legal decisions to named owners.

### 7. Rank the next frontier

Rank open work by consequence, deadline, evidentiary leverage, dependency unlock, integrity risk, and effort. Convert each actionable gap into an owned work packet with inputs, expected artifact, validation, approval boundary, and close condition.

### 8. Emit a recoverable checkpoint

Update `CASEBUILD_MESH_REGISTER.md` and a concise handoff containing:

- verified state and evidence citations;
- changes made;
- unresolved gaps and contradictions;
- blocked items and owners;
- exact next action;
- files/records needed to resume;
- last verification timestamp.

Do not declare completion merely because a pass found no new material.

## Output contract

Produce `CASEBUILD_MESH_REGISTER.md` with:

1. matter contract;
2. node graph and preferred operational route;
3. evidence identity/integrity status;
4. linked navigation views;
5. reconciliation findings;
6. ranked work packets;
7. approvals and attorney-review boundaries;
8. completion scorecard;
9. exact resume point.

Use CSV/YAML sidecars when volume makes Markdown unsafe or unwieldy, but link them from the register.

## Local validation

The Skill passes only when an independent reviewer can:

- navigate case → issue/event → evidence ID → exact source → integrity record;
- distinguish original sources from derivatives and analysis;
- identify contradictions, unknowns, access limits, and hash exceptions;
- see who owns each consequential next action;
- resume from the checkpoint without reopening the entire history;
- confirm no original evidence was altered and no legal filing or strategic decision was made autonomously.

## Non-goals

- No single-source-of-truth claims or forced repository consolidation
- No silent deletion, deduplication, renaming, or evidence rewriting
- No fabricated admissibility, authentication, corroboration, or completion claims
- No persuasive legal writing, autonomous legal strategy, or filing
- No exposure of secrets, privileged material, protected identities, or sensitive evidence
