# Oh My Pi — GlacierEQ End-to-End Runtime Mastery and Execution Contract

**Prepared:** 2026-10-14 HST. **Status:** upstream study plus tested, read-only preflight. Actual Intel Mac deployment, provider effects and cross-process mission acceptance are **UNVERIFIED**. This contract consumes existing APEX/Aspen/sigma-glue/computer-user state; it is **not** a new orchestrator.

## Recovered state and source discipline

The last direct audit on 2026-10-08 found a 2015 Intel MacBook Air, Core i5-5250U (2 cores/4 threads), 8 GiB, Sonoma 14.8.7 through OpenCore, OMP 18.8.4, Homebrew 7.0.9, Hindsight plus PostgreSQL, advisors, local Chrome testing, 27 OMP sessions/7,835 recorded events, Yolo approval, Mistral role settings, 22–23 GiB free, heavy CMake source compilation, ~3.5 GiB swap and extreme load. The extra ~27.6 GB macOS APFS volume was not cleared for removal. Git ignored several secret patterns but did **not** ignore the OMP auth db, config, sessions or local key-placeholder path. Firewall and FileVault were off. These facts are **historical**, not an October 14 host readback.

Subsequent other-device OMP and GlacierEQ control-plane improvements exist, including ARM OMP versions and APEX context admission and corrected-learning work. **Never roll the Mac back to the October 8 state or transfer other-device success claims onto it.** Desktop Commander currently reports the Intel Mac offline; no repair, upgrade or external mutation was attempted there during this research turn.

## Ownership boundaries

| Component | Actual owner role | Acceptance evidence |
| --- | --- | --- |
| OMP CLI, models, extensions, skills, session/RPC | Interactive cognition, coding, subagents and tool dispatch | live selected-model inference, process/state test, output review |
| GlacierEQ APEX/Spiral | exact active mission, authenticated history and source-matched applied correction/cursor | mission ID and ContextApplication bound before any effect |
| Aspen Grove memory | durable source/decision continuity | recall source proven and applied, not mere content retrieval |
| sigma-glue | workflow state, idempotency, reconciliation | native provider readback or explicit UNKNOWN freeze |
| computer-user | durable queue, authorized action, task/receipt replay | `computer-user doctor --pretty`, actual task and independent readback |
| mega-skills | reused atomic/compound/mega capabilities | source identity, tested Skill, second mission reuse |
| Oracle / Colab | remote compute *only after authorized and verified* | tenant, quota, cost, bounded job, output checkpoint, receipt |

## OMP upstream mastery notes

1. **MCP discovery**: project `.omp/mcp.json`, profile's `~/.omp/agent/mcp.json`, imported tool configs and root fallbacks have precedence and deduplication. Local stdio MCP can execute commands. Treat a third-party project's MCP definitions as trusted-input risk; inspect before launching a credentialed profile. Use `/mcp list` / `/mcp test <name>` / `/mcp reload`, not config appearance alone.
2. **Profiles**: `omp --profile name` isolates OMP-native config/auth/sessions/MCP, but project MCP and foreign CLI config may still apply. Not a sandbox.
3. **Approval modes**: `always-ask`, `write`, `yolo` have different read/write/exec permissions. Headless subagents and custom MCP tools require consequence-specific authorization; `yolo` is not proof of task authority. Do not silently rewrite active user's settings.
4. **Advisors**: the WATCHDOG reviewer is a challenge function, not independent provider verification or a second executor. A WATCHDOG roster may expand tools to mutating capabilities; keep independent reviews read-only by default.
5. **Memory**: Hindsight uses a reachable server and scoped banks; retain/recall can be asynchronous and do not prove history was applied to the correct mission. Source/correction/cursor must causally affect the next action.
6. **RPC**: OMP RPC is JSONL over stdio, not JSON-RPC. A prompt acknowledgment, `prompt_result`, `agent_end`, and `session_settled` are distinct; only settled accounts for pending background work. Correlate request IDs and use the preexisting durable job queue for cross-process effects.
7. **Model roles**: a catalog listing is not an inference receipt. Validate authenticated models with a real no-tools request, then verify fallback and advisor models; no surprise billed providers.
8. **Task/subagent discovery**: definitions are resolved and validated again at execution; use bounded concurrency and on-disk Git isolation where supported. This Intel Mac cannot sustain unbounded local builds or browsers.

Primary official docs (2026-10-14 verification):
- https://github.com/can1357/oh-my-pi/blob/main/docs/config-usage.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/mcp-config.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/approval-mode.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/memory.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/task-agent-discovery.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/advisor-watchdog.md
- https://github.com/can1357/oh-my-pi/blob/main/docs/rpc.md

## Execution gates

**A. Recover host without mutations:** Desktop Commander `list_devices` and ping, correct device/account identity, machine version and latest effective OMP profile. Run `python3 scripts/omp_runtime_audit.py --home "$HOME"` on the Mac when reachable. Its `READ_ONLY_AUDIT` JSON classifies approval, Git-index risk, disk pressure and abnormal load; it never attests mission completion. Save receipt only to controlled storage. Do not print raw auth config or transcripts.

**B. Stabilize host:** identify foreground OMP/compile jobs, swap and memory pressure; on Tier 3 Intel Homebrew, avoid repeating source-heavy builds during large ongoing work. Protect local auth/state files against accidental Git staging *and check tracked index/history*. Review OpenCore boot volume group and snapshots before any disk reclamation. Design firewall/FileVault adjustments with boot recovery and remote access preservation.

**C. Apply mission authority:** resolve the actual user-requested mission, `expected_mission_id`, authenticated source snapshots, exact historic correction and durable cursor. Verify source-matched application changes execution decisions. Keep each workstream on the canonical `shared/SCALE_FDE_MISSION.yaml`.

**D. Compose and execute:** discover existing Skill/connector/worker capabilities; use OMP for governed planning and coding, APEX admission for authority, computer-user for durable tasks, sigma-glue for idempotency and ambiguity. Oracle/Colab may be compute workers, never independent state authorities. Perform only authorized actions on non-sensitive test targets first.

**E. Verify provider reality:** capture exact applied revision and provider-native state after an effect. On ambiguous provider response freeze/reconcile; never blindly retry a potentially applied mutation. Bind independent verification to original source and action receipt.

**F. Prove durability:** intentionally interrupt the controlling process. Spawn a genuinely new process, hydrate correct mission/cursor, prevent duplicate effects, continue to target state, produce execution/verification/mission receipts.

**G. Prove compounding:** register a new reusable capability only after successful verification; run Mission 2 and show it discovers and uses that capability with measurable improvement versus Mission 1 or baseline. Registry presence alone does not prove reuse.

### Acceptance ledger — all UNVERIFIED until independent live proof

| Gate | Evidence | False-positive to reject |
| --- | --- | --- |
| Identity | host-derived mission ID matches recovered one | last session title guessed |
| Applied context | source/correction/cursor-matched readback changes chosen action | context merely retrieved |
| Capability | existing owner reused with tests | new duplicate framework |
| Execution | authorized external mutation and reservation | simulated request or shell output |
| Reconciliation | exact provider readback and ambiguity protocol | HTTP ack presumed applied |
| Resurrection | new process survives orchestrator death | same session resume |
| Evidence | original sources/revisions/independent verifier receipts | agent self-report |
| Compounding | Mission 2 actually uses registered improvement | Skill file written |

Do not collapse missing remote Mac access into global project paralysis: **LOCAL_BLOCK != GLOBAL_BLOCK**. Continue independent repository work without claiming it deployed to the offline Mac.

## Local tests

```bash
python3 -m unittest discover -s tests -p test_omp_runtime_audit.py -v
python3 -m py_compile scripts/omp_runtime_audit.py
python3 scripts/omp_runtime_audit.py --home /missing-home
# Expected nonzero=2 and NEEDS_ATTENTION; this is correct fail-closed behavior.
```

On actual Mac: verify OMP version and selected provider no-tools response; `omp config get tools.approvalMode`; `omp config get memory.backend`; safe host preflight; `computer-user doctor --pretty` once its installed runtime is confirmed. The real end-to-end acceptance requires an authorized provider effect, independent readback, process-death continuation and second-run reuse.

**Current checkpoint:** off-device audit implementation/test suite exists and passes in isolation; branch receipt and tested artifact are source-linked. **Remaining:** host deployment, host-run evidence, native execution/reconciliation and durable multi-run capability proof.
