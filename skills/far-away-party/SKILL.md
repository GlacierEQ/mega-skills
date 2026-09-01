---
name: far-away-party
description: "Governing long-horizon autonomous missions from high ambiguity to evidence-backed delivery without context drift. Coordinates Long-Horizon Core with conditional specialist loops (capability-readiness, signal-to-decision, guarded-automation, evidence-to-evolution, recon-and-map, skill-forge, automation-control)."
---



# 🚀 Far Away Party Mega-Skill

The mission-governance layer for complex, long-horizon work that runs across multiple turns, subagents, and sessions without context drift.

## When to Activate
- Tasks requiring multi-phase planning, research, implementation, and verification.
- Work with high initial ambiguity where requirements evolve from discovery.
- Autonomous long-running missions (overnight / multi-session / large estate passes).
- Complex workflows where loss of context or state amnesia would cause failure.

---

## The 5 Immutable Durable State Files

Far Away Party maintains five durable files as the absolute mission source of truth:

| State File | Purpose | Rule |
| :--- | :--- | :--- |
| `MISSION.md` | Bounded intent, non-negotiable criteria, and exclusions | Sole input to planning; never silently expanded |
| `ROADMAP.md` | Phase gates, dependency order, and chunk boundaries | Explicit validation criteria per chunk |
| `CONTEXT.md` | Lean operational capsule of current realities | Enables execution without loading full chat history |
| `EVIDENCE.md` | Physical test results, compiler receipts, and proof hashes | Zero claims without verified file-backed evidence |
| `HANDOFF.md` | Exact state, last verified gate, and next actionable step | Guarantees lossless resumption across turns |

---

## The Compounding Route Matrix

| Mandatory Core | Conditional Route | When Activated | Added Value |
| :--- | :--- | :--- | :--- |
| `long-horizon-core` | `capability-readiness` | Tools, access, or claims unverified | Admits/blocks route via preflight proof |
| `long-horizon-core` | `signal-to-decision-loop`| Inbound signal requires pivot | Converts observation to reviewed route |
| `long-horizon-core` | `guarded-automation`   | Recurring/event-triggered action | Enforces approvals & idempotency |
| `long-horizon-core` | `evidence-to-evolution`| Repeated evidence shows need | Submits governed skill upgrade proposal |
| `long-horizon-core` | `recon-and-map`        | Repository scope is uncertain | Maps actual disk state before writing |
| `long-horizon-core` | `skill-forge`          | Recurring task spotted | Compiles new atomic skill into registry |
| `long-horizon-core` | `automation-control`   | External triggers or cron | Enforces phase gates & audit trace |

---

## The 8-Step Mission Execution Algorithm

1. **Initialize State**: Generate `MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md`.
2. **Preflight Readiness**: If any tool, dependency, or access is uncertain, execute `capability-readiness` before proceeding.
3. **Execute in Chunks**: Work on exactly one chunk at a time as declared in `ROADMAP.md`.
4. **Enforce Compound Handoffs**: Accept only named, structured artifacts from subagents; ignore raw conversational transcripts.
5. **Phase Gating**: After every chunk, run the local validation test harness and update `EVIDENCE.md`.
6. **Update Context Capsule**: Refresh `CONTEXT.md` with the new reality; discard obsolete intermediate steps.
7. **Write Handoff Record**: Update `HANDOFF.md` with exact next steps so any crash or turn boundary can resume instantly.
8. **Final Mission Verification**: Close only when all `MISSION.md` criteria map to verified evidence and zero open assumptions remain.

## Source Fidelity / Case Mission Upgrade — 2026-08-31

For evidence-heavy, legal, investigative, journal-based, or life-history missions, Far Away Party must preserve two separate layers:

### Source layer — immutable meaning
- Preserve original evidence, historical wording, regularly kept journal/chat-export language, timestamps, speaker sequence, paths, hashes, and prior source assertions.
- A later summary, verification pass, context capsule, or model interpretation may annotate the source layer but must not silently replace it.
- "Not reopened in this pass" is a retrieval state, not contrary evidence.
- Existing material assertions remain in the mission graph unless stronger evidence establishes a specific reason to supersede them. Preserve superseded provenance.

### Analysis layer — additive structure
Add fact IDs, allegation IDs, confidence/evidence state, authority mapping, contradiction records, defenses, rebuttals, damages, discovery targets, and lifecycle work product around preserved sources.

### Retrieval expansion law
A spelling/OCR/name variation is normally a reason to widen retrieval, not terminate it. Use event fingerprints, relationships, dates, addresses, contact data, and source continuity to resolve identity. Conversely, do not merge distinct people or matters merely because names resemble each other.

### Contradiction law
Contradiction → preserve both propositions → identify discriminating evidence → resolve when evidence permits.
Never: contradiction → silently delete/downgrade the operator/source account.

### Full-lifecycle legal mission rule
When the mission explicitly requests full casebuilding, do not stop at research or an outline while materially executable lanes remain. Drive through source recovery, fact/event architecture, current-law verification, allegations/elements, opposition modeling, damages/remedies, discovery, motions/petitions/declarations/exhibits, hearing strategy, enforcement, post-ruling preservation, and exact handoff state. External filing/service still requires its own authority and receipt.

### Completion semantics
"Complete" means the mission criteria are materially exhausted or every remaining item is a named blocked dependency with owner, acquisition route, and next executable action. It never means "first useful answer produced."

## Hidden Caveat Gate

For legal, investigative, evidence-heavy, journal-based, and source-sensitive missions, activate `hidden-caveat-detector` at three checkpoints:

1. **Before source-bearing durable mutation** — detect whether a proposed rewrite, status label, qualifier, or compaction changes source meaning.
2. **Before phase/final quality gate** — detect hidden scope reduction, burden shifting, remedy suppression, caveat propagation, or premature completion.
3. **Before mission closure** — verify no executable lane is being concealed behind caution or "not verified" language.

A failed hidden-caveat audit returns the artifact to the work owner. It does not silently advance.
