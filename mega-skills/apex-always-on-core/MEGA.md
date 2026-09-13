# Apex Always-On Core

## Mission

Continuous always-on cognitive foundation fusing sequential thinking, context compaction, dialectic swarm consensus, multi-service connectors, estate watchdog health, and safe repository convergence.

## Compounding structure

- Required combos: `long-horizon-core`, `guarded-automation-loop`, `signal-to-decision-loop`
- Conditional combos: `capability-readiness`, `evidence-to-evolution-loop`, `frontier-orbit-synthesis`, `fleet-recon-and-harmonize`

## Execution protocol

1. Initialize `MISSION.md` through `HANDOFF.md` in the active execution workspace.
2. Execute required combos in deterministic dependency order.
3. Run the **Harmonious Merge Watch** during repository-state observation. It may inventory refs, compare branches to `main`, identify duplicate or security-sensitive history, and emit a disposition plan.
4. Route to `fleet-recon-and-harmonize` only when the watch finds branch sprawl, unresolved divergent work, overlapping implementations, or security-sensitive refs that require a deliberate convergence plan.
5. Validate all intermediate evidence hashes and record telemetry in `EVIDENCE.md`.
6. Synthesize final mission deliverable `ALWAYS_ON_CORE_MISSION_RESULT.md`.

## Harmonious Merge Watch

The watch is a standing read-only control, not an automatic cleanup mechanism.

- **Baseline:** Treat `main` as the living canonical line. Never replace, reset, delete, or demote it because another branch is larger, newer, or noisier.
- **Observe:** Maintain an evidence-backed inventory of branches and tags, their relationship to `main`, new divergence, check status, and any signs of credential-bearing paths or unsafe preservation refs.
- **Assess value:** Inspect actual behavior and tests—not names or commit counts—to identify unique beneficial changes, duplicated work, regressions, and blocked reviews.
- **Prepare:** Emit a `harmonious-merge-audit.json` or an escalation work packet with per-ref dispositions and the smartest coherent integration units.
- **Do not mutate:** The watch cannot merge, force-push, delete branches/tags, create archive refs, rotate credentials, or rewrite history.
- **Security escalation:** A known credential exposure triggers immediate rotation/revocation escalation and a separately authorized all-ref history-cleanup plan. Never create a new tag or backup ref that preserves contaminated history.

## Durable state files

- `MISSION.md`
- `ROADMAP.md`
- `EVIDENCE.md`
- `CONTEXT.md`
- `HANDOFF.md`
- `ALWAYS_ON_CORE_MISSION_RESULT.md`
- `harmonious-merge-watch.json` (when repository observation is in scope)

## Cognitive firewall

- Mode: `read_only`
- Fail closed: `true`
- Allowed actions: `read_repository`, `run_local_tests`, `write_run_artifacts`, `emit_receipt`
- Forbidden actions: `external_mutation`, `network_send`, `file_submission`, `deletion`, `deployment`, `merge`, `credential_access`, `legal_filing`, `autonomous_legal_decision`, `execute_unknown_program`

## Human control points

- `approve_production_release`
- `approve_harmonious_merge_plan`
- `approve_ref_retirement`
- `approve_history_rewrite`
- `escalate_critical_anomalies`

## Output contract

Produce `ALWAYS_ON_CORE_MISSION_RESULT.md` upon mission completion. When repository observation is in scope, include or reference the current `harmonious-merge-watch.json`, its evidence, and its next required human decision.

## Local validation

100% test assertions and receipts verify. The always-on layer passes its repository-convergence guard only when `main` remains the stated baseline, all discovered scoped refs have a recorded state or deliberate deferral, and no mutation occurred without the applicable approval.

## Non-goals

Unbounded external state mutations, autonomous branch cleanup, or automatic history rewriting.

## Always-On Source Integrity — 2026-08-31

The always-on core continuously enforces:
- **source ≠ summary**: context compaction may reference original material but cannot become a substitute source;
- **nonreview ≠ contradiction**: lack of reinspection in one run does not demote an existing source assertion;
- **journal continuity**: historical chats/exports used as a regularly kept journal remain verbatim source records;
- **alias expansion**: spelling/OCR variants expand retrieval rather than stopping it;
- **contradiction routing**: conflicts create evidence-acquisition work packets instead of silent fact deletion;
- **forward persistence**: every complex run should leave a durable delta and exact resume point;
- **no false completion**: close only when remaining gaps are explicitly blocked/assigned or mission criteria are satisfied.

## Epistemic contract & Notion bridge — 2026-09-07

Reference-only section (CONTRIBUTING: no skill-level instruction copying into a Mega Skill).

- Contract: `docs/EPISTEMIC_CONTRACT.md` · Mesh: `docs/SKILL_MESH_AND_TOOLS.md`
- Emits: PLAN (`MISSION.md`, `ROADMAP.md`), FACT with source grade (`EVIDENCE.md`), grade-D pointer set (`CONTEXT.md`), OBSERVATION (`HANDOFF.md`, `harmonious-merge-watch.json`).
- May promote to: COMPLETE only with quality-gate PASS + `HANDOFF.md` + every remaining gap explicitly blocked or assigned · Proof floor: L2 per artifact, L3 across stores
- Receipts: `HANDOFF.md` / ledger entry + `EVIDENCE.md` hashes; the watch emits receipts, never mutations.
- Contradiction routing: Harmonious Merge Watch → evidence-acquisition work packet with per-ref dispositions; the watch never resolves a contradiction itself (contract §8).
- PRESERVE (compaction exceptions): source ≠ summary, journal continuity, alias lineage, refs marked security-sensitive.
- Mesh edges: COMPOSES → `skills/casey-operator-execution-kernel`, `skills/max-token-saver`, `combo-skills/long-horizon-core`, the contract · VERIFIED_BY → `quality-gate` · MIRRORS → `GlacierEQ/apex-control-plane`
- Tools: read-only repository observation, local tests, run artifacts, receipts (cognitive firewall) · human control points listed above
- Notion projection: APEX Always-On Core — Long-Horizon Operating Loop · page `17811a298d2c4d328f293e63ad5a91ca` (route, don't copy — this file outranks the projection)
- Index: `integrations/notion-skill-bridge.json`
