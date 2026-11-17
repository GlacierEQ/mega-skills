---
name: elite-kanban-team
description: "Operate a top-level team Kanban with zero bad habits: anti-pattern contract, two-phase dispatch, 6-stage lifecycle, merge/receipt gates, headroom gate, metrics. Use when building or running a kanban team, or when asked to 'create the best team.'"
version: 1.0.0
status: active
metadata:
  origin: glaciereq/apex-orchestration + team-agent-orchestration
  tags: [elite-kanban, team-construction, anti-bad-habits, merge-gate, headroom-gate, receipt-chain]
  related_skills: [team-builder, team-agent-orchestration, apex-orchestration, ws-verify, kanban-pipeline-v2]
---

# Elite Kanban Team — Zero-Bad-Habits Operating Contract

The elite kanban team is a *verified, merge-gated, headroom-closed* team. Its only purpose is to turn an intent into an artifact whose correctness can be checked without the team present. Any card, half-done, unmerged, or unverified work is treated as a block.

## 1. The anti-bad-habit contract

| Bad habit | Why it happens | Cure (what the team enforces) |
|---|---|---|
| Board theater (board exists, no acceptance) | No explicit done-criteria | Every card carries `acceptance: [...]`. `Done` requires `state=merged` AND `l2_proof:true`. |
| Agent soup (many agents, no owner) | No one owns convergence | Exactly one `owner` per card; a merge-integrator owns the gate. No overlap without a merge integrator. |
| Invisible work (output only in chat) | No handoff artifact | Every task writes a handoff artifact + receipt to `teamagent/<mission>/`. No delivery without artifact. |
| Overlapping writes | No worktree/branch boundary | One owner per branch/worktree; no two owners edit the same file. Merge-integrator resolves conflicts. |
| No product artifact | Scope not bounded | Every card is scoped to a `deliverable` (file, receipt, or report), not a chat thread. |
| Unverified merge | Trust instead of proof | Merge gate = `l2_proof:true` + `receipt_sha256` chain + reviewer signature. Draft ≠ deliverable. |
| Unbounded nodes | No timeout | Every node has `timeout_s` (60–300s). Long tails fail fast with `repair` path. |
| Headroom runaway | No gate | Max concurrency 1 if `SwapFree<50Mi or MemAvail<800Mi`, else 3 (RED/AMBER/GREEN). |
| Metric invisible | Plan-by-guess | `kanban-throughput.py` reports wall, sum_run, parallel_saved, bottlenecks after every run. |
| E0 claim without output | Confidence bias | No card completes on a self-report. The verifier (advisor, separate) re-runs the check. |

## 2. Operating model — two-phase dispatch

Borrowed from the Gemini `Orchestrator (Argon)` dual-phase model:

- **Phase 1 — Planning (read-only):** the team runs with plan tools only. Read the relevant source, establish contracts, list files and data. No writes.
- **Transition (`exit_plan_mode`):** emit plan + contract. The execution model then carries out the plan; if a step fails twice or a key assumption breaks, re-plan.
- **Phase 2 — Execution (write):** the team performs the write/edit/command actions. No re-planning unless a failure actually occurs.

This bans the bad habit of *re-planning on failure after already writing*, which is how 'best-practice' teams silently rot into messes.

## 3. Per-card contract (Every card is a first-class citizen)

Every card is a JSON object with:

```jsonc
{
  "id": "agent-card-001",
  "owner": "agent",
  "state": "backlog|ready|running|review|blocked|merged",
  "branch": "product/<card-id>",
  "deliverable": "path/to/artifact",
  "acceptance": ["...", "..."],
  "merge_gate": "lint, tests, receipt->l2_proof:true, sha256 chain",
  "handoff": "teamagent/<mission>/<card-id>.json"
}
```

- **Owner**: one accountable role/agent per card. No shared ownership.
- **Scope**: bounded file set, branch, tool surface, and no inter-card overlap.
- **State machine**: backlog → ready → running → review → blocked(marked with blocker) → merged.

## 4. The six-stage lifecycle (kanban flow)

```
INTAKE  ->  DECOMPOSE  ->  DISPATCH  ->  VERIFY  ->  FUSE  ->  DELIVER
```

Each stage has entry/exit conditions and an **L2 evidence requirement**: a receipt, a test green, or a hash match. Skipping a stage is a FUSE rejection (not a recommendation).

| Stage | Exit evidence |
|---|---|
| INTAKE | `mission.md`, `CONTEXT.md`, `requirements.json` written |
| DECOMPOSE | `dag.json` (cards + deps + timeouts) written |
| DISPATCH | cards spawned, `teamagent/<card>.json` pre-run receipts written |
| VERIFY | `l2_proof: true` + `receipt_sha256` + independent verify re-run |
| FUSE | three-signatures (Producer→Auditor→Refiner), `teamagent/<card>.json` merged |
| DELIVER | `delivery.json` + `receipt_sha256` chain, `delivery_gate` = passed |

## 5. Merge gate + receipt chain

A card may leave `running`/`review` only after **three independent signatures** (E0):

| Order | Role | Produces |
|---|---|---|
| 1 | **Producer** | `{files, sha256, tests, l2_proof}` |
| 2 | **Auditor** | `{findings, severity_counts, approve|reject}` |
| 3 | **Refiner** | `{diff, complexity_before, complexity_after}` |

The **merge-gate token** is `l2_proof: true` + a SHA-256 chain entry. Missing signature = BLOCK. A card with a draft (non-`l2_proof`) receipt is **never** merged.

## 6. Headroom / context gate (do not run away the hardware)

| Tier | Condition | Max concurrency |
|---|---|---|
| RED | `MemAvailable < 1200 MiB` or `SwapFree < 500 MiB` | 1 |
| AMBER | `MemAvailable < 2000 MiB` or `SwapFree < 800 MiB` | 2 |
| GREEN | `MemAvailable >= 2000 MiB` and `SwapFree >= 800 MiB` | 3 |

Rule: one heavyweight agent per task. Never run parallel heavy builds locally. `pipeline-lint.py` enforces the gate at dispatch; `kanban-throughput.py` reports wall/sum_run/parallel_saved/bottlenecks after every run.

## 7. Metrics (so bottlenecks are visible, not guessed)

After each run, report:
- **wall** (real elapsed), **sum_run** (sum of node runtimes), **parallel_saved** = `sum_run - wall` (a positive number means parallelism worked), **top bottlenecks** (queue waits), **blocked count**, **merged count**.
- If `parallel_saved == 0` on a multi-card run, that is a finding: the team is serial and should be re-brokered.

## 8. Run procedure (end-to-end, zero bad habits)

1. **Lock objective** from the request; confirm goal and consequence. Ask only about genuinely unresolved material choices.
2. **Boot/search** for controlling state and prior receipts (memory mesh, receipts, art). Reuse context; continue independent work.
3. **Open** the relevant source; record the invention if any.
4. **Reconcile** material conflicts; carry settled corrections into dependent consumers.
5. **Adversarial test**: second-pass looking for what was missed (10–20% of defects confidence bias hides).
6. **Execute** (native tools) with the two-phase plan + headroom gate + timeouts.
7. **Verify** (tests green, hashes match) — an advisor re-runs the check; advisor is a separate agent.
8. **Persist**: receipts, indices, continuation state (append-only). No silent overwrite.
9. **Deliver**: the artifact + receipt chain into `delivery/`, with `receipt_sha256` and `l2_proof:true`.

## 9. Evidence and E0 rule

- A card is `done` only with an E0 artifact (command output, test run, hash) the advisor as an independent agent observed.
- No self-report is accepted as E0. Planner cannot promote `done` on its own report; the advisor re-runs and either passes or fails.
- Downgrade: plan says `done` → advisor re-runs → passes: E0. Fails: back to execute/fix/re-verify (repair ≤ 2 cycles, then escalate). Vendor claims stay E4 until reproduced.

## 10. Do-not-do list (the elite team never)

- Never claim `verified` without a receipt chain hash.
- Never write `TODO`, `pass`, `NotImplementedError`, or `return True` in production code.
- Never feed a persona the full conversation transcript; keep prompts focused.
- Never run `rm -rf` outside temp without confirmation; never put secrets in files/logs.
- Never run parallel heavy local builds (one heavyweight agent at a time).
- Never prune skills or downgrade versions without a reversible backup-first snapshot.
