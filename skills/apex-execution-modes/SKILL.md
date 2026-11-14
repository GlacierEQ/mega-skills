---
name: apex-execution-modes
description: "APEX execution modes adapt depth and resource use to the requested outcome, prioritizing strong, useful completion and task-appropriate verification."
---

# APEX Execution Modes (3 Modes in 1)

Use Lean, Throughput, or Exhaustive techniques as appropriate to the task. No mode sacrifices requested quality for speed, token counts, or test counts.

## Prime Execution Law — DOING, Not Watching

APEX execution exists to make the requested useful outcome real. Observation, reconciliation, monitoring and similar activities support a larger execution request; an explicitly requested audit, investigation or other read-only deliverable may itself be the outcome.

### Non-negotiable invariants

1. **SELECT REAL WORK → DO IT → VERIFY → KEEP DOING.**
2. **No final response while an authorized executable next action exists.**
3. **Never convert BUILD → PLAN, FIX → AUDIT, CONTINUE → REDISCOVER, EXECUTE → WATCH, or ADVANCE → RECONCILE.**
4. Observation serves a requested investigation or provides task-relevant input for action; a read-only outcome does not require a mutation.
5. Reconciliation can be the requested outcome or a technique supporting another outcome.
6. Do not mistake incidental monitoring, CI watching, diagnostics or status reporting for completion of a larger requested outcome. They can be a result when specifically requested.
7. Once the Operator has authenticated or provisioned a tool/capability, tool invocation, schema discovery, retries, alternate routes, troubleshooting, connector recovery, adapter repair, verification, and readback are **system work**, not Operator work.
8. Recoverable tool failures are internal implementation events. Repair or route around them and continue. Do not hand them back to the Operator as tasks.
9. Stop only for a genuine Operator-only decision/action, unavailable required information that cannot be acquired with existing capabilities, or a hard external boundary after safe execution paths are exhausted.
10. A successful execution cycle fulfills the requested outcome to the extent evidence supports. A read-only result need not mutate state.

### Anti-observer completion gate

Before finalizing, ask one machine question: **“Can any available authorized tool still make useful mission state more complete right now?”** If yes, execute it. Do not report it as a next step. Do not schedule it as future work. Do it now, verify it, then evaluate again.

### Substantive mission-work gate

“Real work” means work whose completed result directly advances the Operator’s substantive objective: a product capability, deployed/runtime capability, case/evidence state, application/job artifact, legal work product, organized evidence estate, external execution, or other requested mission deliverable.

The following are **support work**, not substantive mission completion, unless the Operator explicitly requested them as the mission: inspection, diagnostics, audit, inventory, reconciliation, health checks, CI watching, receipt consumption, branch freshness, meta-tool repair, skill-framework repair, scheduler repair, governance, registry maintenance, and reporting.

When support work serves a larger execution request, continue into the authorized requested work; do not substitute an inspection artifact, report, test or status for that outcome. When expressly requested, a completed, source-grounded audit, analysis or other deliverable is itself the outcome; do not manufacture a mutation.

### Scheduler/worker rule

Recurring workers are production executors unless the Operator explicitly requests a watch. Their default job is to perform substantive work each run. A worker must not spend a run on scanning, reconciliation, branch freshness, CI observation, cursor maintenance, health reporting, or queue inspection unless that directly enables and is immediately followed by concrete work in the same run.

---

## Mode Selection

The budgets below are illustrative, not quality ceilings. Choose the depth the requested outcome requires.

| Mode | When to Use | Token Budget | Depth |
|------|-------------|--------------|-------|
| **Lean** | Routine tasks, quick queries | ~1200 tokens | Surgical |
| **Throughput** | Complex analysis, parallel ops | Medium | Deep |
| **Exhaustive** | Federal filings, security audits | Unlimited | Maximum |

---

## 1. Lean Mode (Token Savings)

### Activation
```bash
export APEX_PROFILE=coremaximized
source ~/APEX_BOOTUP/apex-bootup.sh coremaximized
```

### Token Reduction Stack

The figures below are illustrative and unverified, not measured savings.
| Technique | Reduction |
|-----------|-----------|
| Pointer index vs. dir scan | ~85% |
| Exact grep vs. full file read | ~70% |
| Cache-hit on repeated state | ~42.5% |
| Parallel vs. sequential ops | ÷N |
| StartLine/EndLine constraints | ~60-90% |
| Diamond facet routing | ~89% |

### Cache Protocol
```python
query_hash = "stable_key_v1"
cached = optimizer.get_cached(query_hash)
if not cached:
    result = expensive_op()
    optimizer.set_cache(query_hash, result)
    # Savings depend on actual use and must be measured
```

### Session Discipline
- [ ] Resolve paths via `APEX_POINTER_INDEX.json` first
- [ ] Set `StartLine`/`EndLine` on every file view
- [ ] Use `grep_search` with exact patterns
- [ ] Launch independent tasks in parallel
- [ ] Maintain single living artifact
- [ ] Apply cache-hit before recomputation

---

## 2. Throughput Mode (Hyper-Efficiency)

### Juggernaut Pipeline
```mermaid
graph LR
    A[Surgical Context] -->|High SNR| B[Max Attention]
    B -->|Clear Paths| C[Accurate Logic]
    C -->|Zero Noise| D[Fast Execution]
    D -->|Cache Write| E[Token Store]
    E -->|Cache Hit| B
```

### 4-Phase Execution
1. **Phase 1** — Run relevant independent diagnostics in parallel when useful
2. **Phase 2** — ForensicStrikeEngine + Memory sync launched concurrently
3. **Phase 3** — State written to single manifest (not scattered logs)
4. **Phase 4** — Verify material results appropriately without blocking unrelated progress

### Parallel Execution Pattern
```python
async def run_all():
    await asyncio.gather(
        run_diagnostics(),
        load_constellation(),
        check_connectors()
    )
    # Parallel calls may reduce elapsed time; token savings are not assumed
```

### Helix Orchestrator
- Use specialist builder or reviewer roles when materially useful and explicitly authorized.
- Independent review can find issues; it does not guarantee a self-correcting result.

### Efficiency Multiplier Stack

The following is illustrative, not a measured result or guarantee.
```
CoreMaximized Profile  →  +baseline efficiency
+ Pointer Index First  →  ×0.15 token cost (85% reduction)
+ Parallel Execution   →  ÷N sequential overhead
+ Cache-Hit Protocol   →  -42.5% on repeats
+ Diamond Facet Route  →  ÷9 context injection cost
+ StartLine/EndLine    →  ×0.1–0.4 file read cost
= Illustrative estimate only; actual savings unmeasured
```

---

## 3. Exhaustive Mode (Make-It-Heavy)

### When to Invoke
- **Federal Litigation Filings:** Complaints, responses, motions
- **Security & Audits:** Vault audits, credential checks, file integrity
- **Core Refactoring:** Structural rewrites of base engines

### Rules
1. **No Simplifications:** Never use placeholders, "todo" comments, or summarized code blocks. Every function, variable, and class must be fully written, typed, and docstringed.
2. **Multi-Dimensional Verification:** Test not only the success path, but every edge case, error state, and exceptional environment branch.
3. **Legal Standard Integration:** Trace arguments to applicable controlling law, the chosen court, and the actual filing route. Do not use an unrelated federal rule as a substitute for state-court requirements.
4. **Comprehensive Evidence Mapping:** Preserve original exhibits, source IDs, timing and provenance. Generate full SHA-256/Blake2b manifests and file-tree inventories when they advance authentication or an ordered proof issue; NEVER delay a live filing, appeal, preservation notice, or other irreversible deadline to compute hashes, reconcile duplicate bytes, or perfect a nonrequired exhibit index.
5. **Deadline-first preemption (overrides all three modes):** When a live court/agency deadline could expire before the next work phase, first establish the current forum/time/cutoff, identify the shortest authorized filing-ready route, produce required initiating papers, and move to actual submission/official acceptance receipt if tools and authorization permit. If only the human or an attorney can file, immediately surface that exact action while completing all preparatory work in parallel. Nonmandatory forensic reviews, citation expansion, record migrations, and internal governance are POST-SUBMISSION tasks.
6. **Do not relabel preparation as filing:** A draft, ZIP, hash match, perfect test suite, or upload to Box does not constitute judicial filing. Record FILED only against a native acceptance timestamp/case number; retain PREPARED/UNFILED otherwise.
7. **Scope protection:** An emergency filing pass preserves the complete alleged facts, counts, remedies, and amendment/discovery routes as a separate protected case graph. Omission from a time-critical pleading must be recorded explicitly with reason and revival action, never silently treated as waiver or irrelevance.

---

## Workspace Resources

| Resource | Path |
|----------|------|
| CoreMaximized Profile | `APEX_BOOTUP/profiles/coremaximized.sh` |
| LightMax Profile | `APEX_BOOTUP/profiles/lightmax.sh` |
| Token Cache Optimizer | `gemini-unified-ops/scripts/activate_memory_savings.py` |
| Dynamic Sentinel | `gemini-unified-ops/services/apex_optimizer.py` |
| Stats Registry | `~/.apex_cache/optimizer_stats.json` |

---

## Usage Triggers
- "Token savings", "token optimization"
- "Hyper-efficiency", "maximum throughput"
- "Make it heavy", "exhaustive rigor"
- "CoreMaximized", "lean mode"
- "Parallel execution", "cache-hit"
- "Juggernaut pipeline", "Diamond topology"
