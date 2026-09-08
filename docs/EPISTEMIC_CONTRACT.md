# Epistemic Contract — Proof-Bound Claims

**Status:** ACTIVE reference · **Added:** 2026-09-07 via the Notion skill bridge · **Index:** `integrations/notion-skill-bridge.json` · **Notion projection:** page `f86b7bc950e84c5b9f8b7272883dd18d` (route, don't copy — this file outranks the projection).

This is a **crosswalk, not a new layer**. It unifies truth vocabularies that already exist in this repository so every skill, combo, mega-skill, and pipeline can hook into one contract. Nothing here changes a registry entry, an ID, a layer, or a dependency.

| Vocabulary | Executable owner |
| --- | --- |
| Six-layer epistemic loop; five-level authority stack; execution-state ladder | `skills/casey-operator-execution-kernel/SKILL.md` |
| Evidence states; outcome statuses | `integrations/genius-mastery-bridge.json` |
| L0–L6 verification tiers; `epistemic-verification-receipt.json` | `skills/epistemic-gate/SKILL.md` |
| gate → register → quality-gate chain; `epistemic-verification-record.md` | `combo-skills/epistemic-verification-chain/COMBO.md` |
| Proposition record; typed edges; anti-collapse rules | `skills/holographic-case-mesh/SKILL.md` |

## 0. Why one contract

Four overlapping vocabularies kept producing the same five failures: **state inflation** (GENERATED reported as VERIFIED), **recency capture**, **authority laundering** (a persisted assistant claim treated as operator authority), **summary-as-progress**, and **false completion**. One contract; every skill hooks into it (§12). Improving this document improves every skill that references it — that is the compounding mechanism.

## 1. Process layers (six-layer loop)

| Layer | Question | Emits |
| --- | --- | --- |
| PERCEPTION / ACQUISITION | What did I actually read or receive? | source pointer + retrieval state (§3) |
| PROVENANCE / AUTHORITY | Who says so, with what standing? | source grade + authority level (§6) |
| TRUTH STATE | What is its status right now? | claim type (§2) + truth state |
| INFERENCE / MODEL | What follows, and how confidently? | typed inference + confidence band |
| ADVERSARIAL FALSIFICATION | What test would break it? | test run + result (§10) |
| OPERATIONAL VERIFICATION | Did the world change as claimed? | receipt + readback (§5) |

## 2. Claim typing — label every material assertion

`FACT` (source-bound, grade A/B) · `OBSERVATION` (firsthand: operator or tool result) · `INFERENCE` (derived; premises cited) · `HYPOTHESIS` (testable, untested) · `PROPOSAL` / `PLAN` · `QUESTION` · `UNKNOWN`.

- `UNKNOWN ≠ FALSE`. Not searched ≠ not found ≠ false.
- The operator's firsthand knowledge is primary for the operator's own experiences, intentions, architecture, corrections, history, and project direction.
- External search / provider output never silently outranks operator authority over direction; it does outrank assistant memory for externally verifiable facts.

## 3. Retrieval states (verbatim from `integrations/genius-mastery-bridge.json`)

`known_from_context` · `operator_reported` · `retrieval_pending` · `not_searched` · `searched_found` · `searched_not_found` · `unavailable` · `contradicted`

**Invariant:** `retrieval_pending`, `not_searched`, `searched_not_found`, and `unavailable` are not proof of falsity. Record the state; do not collapse it into a verdict.

## 4. Proof tiers for artifacts and actions (`epistemic-gate` L0–L6)

| Tier | Name | Repo meaning | Notion meaning |
| --- | --- | --- | --- |
| L0 | Presence | file / route exists | a page or row exists — proves nothing about behavior |
| L1 | Structure | AST / signatures / schema verified | schema loaded; frontmatter / table shape confirmed |
| L2 | Behavior | tests pass, SHA-256 verified, compilers green | **readback matches intent** after every write; blob SHA + content readback for repo. **Baseline for any mutation claim.** |
| L3 | Backend | live DB / RPC / multi-store sync verified | Notion + GitHub + backing store agree on the same object |
| L4 | Telemetry | runtime health over time; self-healing | connector-health receipts across runs |
| L5 | Swarm consensus | 4-phase dialectic multi-agent agreement | parallel passes agree; second-source confirmation for court / enterprise deliverables |
| L6 | Sovereign autonomy | upstream tracking, zero drift | bridge-manifest SHAs equal live SHAs (mesh drift check) |

**Law of action:** nothing below L2 authorizes a mutation claim. Enterprise or court-facing deliverables require L5.

## 5. Execution-state ladder and the receipt each state requires

| State | Meaning | Required receipt |
| --- | --- | --- |
| `OBSERVED` | seen in a tool result | tool output reference |
| `INFERRED` | derived from observations | premises listed |
| `HYPOTHESIZED` | proposed explanation | falsification test named |
| `PROPOSED` | plan exists | plan text |
| `ATTEMPTED` | call fired (may have failed) | call record |
| `EXECUTED` | call accepted | tool success response |
| `VERIFIED` | readback matches intent | loaded content / blob SHA / query result |
| `COMMITTED` | durable in source control | commit SHA |
| `DEPLOYED` | live | deployment id / URL responding |
| `OBSERVED_IN_OPERATION` | behaves in production over time | telemetry receipt |

Shorthand: `GENERATED ≠ EXECUTED ≠ VERIFIED` · `PARTIAL ≠ COMPLETE`. Crosswalk to genius-mastery `outcome_statuses`: `pending` → PROPOSED / ATTEMPTED · `observed` → EXECUTED · `verified` → VERIFIED · `contradicted` → a CONTRADICTS edge (never a deletion).

**Provider-state rule:** no `SENT` / `FILED` / `CALLED` / `ACKNOWLEDGED` / `MERGED` without a provider-native receipt (filing stamp, message id, merge SHA).

## 6. Source grades and the authority stack

**Authority stack** (kernel, highest first): 1 platform / safety / legal · 2 the operator's explicit current command and durable architecture · 3 provider-native / source-grounded evidence · 4 verification receipts · 5 assistant heuristics.

| Grade | Class | Examples |
| --- | --- | --- |
| A | primary / provider-native | court-issued record, commit SHA, signed declaration, provider receipt, original bytes |
| B | controlled mirror with hash + provenance pointer | custody-logged working copy, mirrored file with SHA-256, hash-chained manifest |
| C | secondary / index | registry entry, README, summary page, search snippet |
| D | assistant-generated representation | matrix, report, ledger prose, this document |
| X | unknown provenance | anything without a locator |

Laws: a grade never rises by copying · C never overrides A or B (README counts 709/33/29 vs registry 714/36/32 → registry wins) · D is a pointer to A/B or it is nothing · X is quarantined until graded · the humanizer boundary (§9) protects A/B verbatim.

## 7. Storage record — the proposition and its eight-field projection

**Proposition record** (`holographic-case-mesh`):
`PROPOSITION_ID | NODE_ID | CLAIM | SOURCE_ID | SOURCE_CLASS | OBSERVER/ACTOR | TIME | TRUTH_STATE | CONFIDENCE | CONTRADICTS | CONFIRMS | NARROWS | SUPERSEDES | NOTES`

**Eight-field source-control row** (Notion legs 1–4): source · date · actor · exact quote / record pin · verification status · blocker · lane use · output.

| Row field | Proposition field |
| --- | --- |
| source | SOURCE_ID + SOURCE_CLASS (grade A–X) |
| date | TIME |
| actor | OBSERVER/ACTOR |
| exact quote / record pin | CLAIM (verbatim, never polished) |
| verification status | TRUTH_STATE + CONFIDENCE |
| blocker | NOTES / NARROWS |
| lane use | NODE_ID |
| output | typed edge → production artifact |

## 8. Contradiction and precedence law

- Contradiction is evidence, never corruption: keep both propositions, add CONTRADICTS edges, route to the owner as an open issue or an evidence-acquisition work packet.
- Supersession creates an edge; it never deletes. Mistaken states stay source-bearing.
- Anti-recency: newest ≠ truest. Owner precedence ladder: explicit ownership > source authority > identity correctness > provenance strength > verification state > relation completeness > schema fitness > freshness. Never "newest / best-name wins".
- Identity protection: a shared person, institution, date, evidence object, or report number never merges nodes. Cross-node facts travel only on provenance-bearing edges.
- A higher-authority source may supersede one proposition for one question without becoming global authority over the mesh.

## 9. Compaction and humanizer boundary

- Compaction never drops locators: SHA, docket / record number, timestamp, hash, deadline, URL, page id.
- Source ≠ summary. The compaction record is the receipt; the original stays (append-only).
- Evidence, quotes, citations, JSON, and code are never style-polished. Journal / chat sources keep original wording, labeled `REGULARLY KEPT JOURNAL — ORIGINAL WORDING PRESERVED`.
- Anything the operator marks PRESERVE is exempt from compaction.

## 10. Adversarial falsification — run before any VERIFIED

Ask: *what test would fail if this were wrong?* Then run it: readback, query, script, second source, parallel agent, hash recompute. The kernel's ten-question pre-response test gains three questions: **11** Is every material claim typed? **12** Does every promoted state carry its receipt? **13** Is every UNKNOWN written as UNKNOWN rather than silently dropped?

## 11. Named failure modes — detect, then repair

| Failure | Signature | Repair |
| --- | --- | --- |
| State inflation | "done / verified" without receipt | demote to EXECUTED or ATTEMPTED; obtain the receipt |
| Recency capture | latest chat topic becomes the mission | rerun the kernel mission-selection gate |
| Authority laundering | persisted assistant claim treated as operator authority | re-grade as D; recover the operator source |
| Summary-as-progress | new matrix / report counted as gain | mission-delta gate: which objective state changed? |
| False completion | PARTIAL reported as COMPLETE | list remaining gaps with typed state |
| Silent normalization | divergent records merged | restore both; add CONTRADICTS edge |
| Source → summary substitution | citing the summary | re-cite the source; summary becomes a pointer |
| Locator loss | SHA / record number / deadline missing after compaction | recover from source; tag PRESERVE |
| Secret-as-evidence | credential text copied as "proof" | redact; metadata only; rotate if exposed |

## 12. Hook contract — the block every skill declares

Append one reference-style section to the skill file (and its Notion page). Reference the contract; never copy lower-level instructions into a higher-level body (`governance/CONTRIBUTING.md`).

```markdown
## Epistemic contract & Notion bridge — YYYY-MM-DD

- Contract: `docs/EPISTEMIC_CONTRACT.md` · Mesh: `docs/SKILL_MESH_AND_TOOLS.md`
- Emits: <claim types this skill produces>
- May promote to: <states> · Proof floor: L<n>
- Receipts: <what must be attached before a state is claimed>
- Contradiction routing: <owner / edge>
- PRESERVE (compaction exceptions): <locators>
- Mesh edges: <TYPE → target> …
- Tools: <runtime tools> · <repo / CLI tools>
- Notion projection: <title> · page `<id>` (route, don't copy — this file outranks the projection)
- Index: `integrations/notion-skill-bridge.json`
```

## 13. Output contract

End every material response with a typed state block:

```json
{"state":"VERIFIED|EXECUTED|PARTIAL|BLOCKED|UNKNOWN","tier":"L0-L6","claims":{"fact":0,"inference":0,"unknown":0},"receipts":["url|sha|path"],"contradictions":0,"next":"single next action"}
```

## Hooked on this branch (2026-09-07)

`skills/max-token-saver/SKILL.md` · `skills/token-saver/SKILL.md` · `mega-skills/apex-always-on-core/MEGA.md` · `combo-skills/long-horizon-core/COMBO.md` · `skills/casey-operator-execution-kernel/SKILL.md` · `skills/power-skill/SKILL.md` · `skills/make-it-heavy/SKILL.md` · `skills/apex-meta-ignition/SKILL.md`. Queued peers are listed in the manifest under `queued_peers`.
