# Packet 19 — DAG-SCHEDULER

**Owner:** apex-orchestration v1.2.0
**Maturity:** 9 / "Formal topological sort with cycle detection, parallel fan-out, ready-set maintenance"
**Layer:** Skill
**Scope:** When DECOMPOSE produces a DAG of subtasks, this packet governs how they are scheduled — not a simple list, but a properly-defined graph with edges, ready-set, and execution waves.

---

## Invariant (L5)

A DAG is schedulable iff:
1. It is a finite directed acyclic graph (verified by topological sort).
2. Every node names: (a) a lane, (b) a verification gate, (c) a receipt, (d) optional `depends_on: [node_id, ...]`.
3. A node becomes "ready" iff all of its `depends_on` nodes are PASSED.
4. Ready nodes are dispatched in parallel, capped at `MAX_PARALLEL` (default 4, configurable).

## The Scheduler

```
state = {nodes: {id: Node}, status: {id: PENDING|READY|RUNNING|PASSED|FAILED|BLOCKED}}
ready_set = {id for id in nodes if all(deps in status[PASSED])}

while not all_done(nodes):
    to_dispatch = take(ready_set, MAX_PARALLEL - running_count)
    if to_dispatch:
        for n in to_dispatch: dispatch(n); status[n] = RUNNING
    else:
        wait_for_any_running_to_finish()
    update_ready_set()

on_node_done(n, status):
    if status == FAILED: propagate_block_to_dependents(n)
    if status == PASSED: update_ready_set()
```

## Block Propagation

When a node Fails, all its descendants (transitive dependents) are marked `BLOCKED` with `cause: <upstream_failure>`. They are not dispatched. This is critical: do not waste tokens dispatching subtasks that depend on a failed subtask.

## Cycles

A cycle is a hard error (F-DEC-01 dag_cycle per Packet 09). The scheduler detects cycles by running Kahn's algorithm or Tarjan's strongly-connected-components; if any SCC has > 1 node or a self-loop, the DAG is rejected.

## Gates

- **G1 — Acyclicity gate.** Cycles are rejected with F-DEC-01; no node is dispatched from a cyclic DAG.
- **G2 — Dependency-resolution gate.** A node with an unresolvable `depends_on` (missing target) is rejected at DECOMPOSE, not at runtime.
- **G3 — Concurrency cap gate.** `MAX_PARALLEL` is never exceeded, even if more nodes are ready. Excess is queued.
- **G4 — Block-propagation gate.** Descendants of a FAILED node are marked BLOCKED before any new dispatch. The audit log records the propagation.
- **G5 — Wave-determinism gate.** Two runs of the same DAG produce the same execution order (topological + tiebreak by node_id).

## Anti-Patterns

- Treating the DAG as a flat list (loses dependency information; may dispatch a subtask before its inputs are ready).
- Ignoring block propagation (dispatching descendants of failed nodes).
- Capping MAX_PARALLEL at 1 (defeats parallel fan-out).
- Capping MAX_PARALLEL at infinity (rate-limit storm, no isolation).
- Auto-dispatching descendants of BLOCKED nodes (the gates say BLOCKED, not PENDING).

## L2 Evidence

- Acyclicity test: 5-node cycle → rejected with F-DEC-01.
- Topo-order test: A→B, A→C, B→D, C→D → execution order: A, then B||C, then D.
- Block propagation test: B fails → D marked BLOCKED, not dispatched.
- Concurrency cap test: 8 ready nodes, MAX_PARALLEL=3 → 3 dispatched, 5 queued.
- Wave-determinism test: same DAG, two runs, same execution order.

## Versioning

- **Major bump:** scheduling algorithm change, gate change.
- **Minor bump:** new state field added.
- **Patch:** bug fix.

Current version: **1.0.0** (paired with apex-orchestration v1.2.0).
