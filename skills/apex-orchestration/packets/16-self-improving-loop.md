# Packet 16 — SELF-IMPROVING-LOOP

**Owner:** apex-orchestration v1.1.0
**Maturity:** 9 / "Hebbian reinforcement with regression gates; learning is monotonic only when proven"
**Layer:** Skill
**Scope:** The closed loop that turns observations into permanent improvements. Lifts the L6 "Hebbian self-evolution" entry of Packet 05 from a line in a table to a working algorithm.

---

## Invariant (L5)

A learning update is valid iff:
1. It produces a `WEIGHTS_VERSION` bump (semver).
2. The new weights are accompanied by a regression test that proves the prior `lane_stats.json` produces equivalent or better scores than before.
3. The update is appended to `learning_log.jsonl` (immutable).
4. Reverting is one command: restore the prior `WEIGHTS_VERSION`.

The system never silently mutates weights. Every change is a checkpoint.

## The Hebbian Update (per mission)

After a delivered mission, the learning loop updates the per-lane weight vector and the routing weights:

```
For each dispatched lane L on subtask S:
  if outcome == success:
    w[L] += η * 1.0                     # Hebbian: fire together, wire together
  elif outcome == fail:
    w[L] -= η * 1.0                     # anti-Hebbian on failure
  w[L] = clamp(w[L], 0.0, 1.0)          # bounded weights
  decay: w[L] *= γ                       # retention decay (default 0.99)
```

Where `η` is the learning rate (default `0.05`) and `γ` is the retention decay (default `0.99`). Both are config in `~/.local/share/apex-orchestration/learning_config.json`.

For the 6 scoring weights in Packet 13 (w1..w6), the same update rule applies on a per-domain basis. A success in `CODE` lane on a `domain=finance` mission boosts `CODE`'s weight for `domain=finance` specifically.

## Versioning

```json
{
  "WEIGHTS_VERSION": "1.1.0",
  "ts": "2026-09-04T18:00:00Z",
  "weights": {
    "w1": 0.30, "w2": 0.20, "w3": 0.20,
    "w4": 0.10, "w5": 0.15, "w6": 0.05
  },
  "per_lane": {
    "REASON": {"w": 0.85, "n_observations": 42, "success_rate": 0.91},
    "CODE":   {"w": 0.92, "n_observations": 87, "success_rate": 0.95},
    "...": "..."
  },
  "per_domain": {
    "medical":  {"DOMAIN-MED": 0.98},
    "finance":  {"DOMAIN-FIN": 0.97},
    "code":     {"CODE": 0.95, "CODE-FAST": 0.88},
    "...": "..."
  },
  "parent_version": "1.0.0",
  "regression_test": "tests/test_routing_regression.py::test_v1_1_0_beats_v1_0_0"
}
```

Location: `~/.local/share/apex-orchestration/weights/<WEIGHTS_VERSION>.json`. The active version is symlinked from `weights/CURRENT.json`.

## The Learning Loop (5 stages)

```
DELIVERY  ->  EVALUATE  ->  REGRESS  ->  COMMIT  ->  ROLLBACK-WATCHDOG
   |            |            |            |              |
receipts    run miner    test against  bump version   monitor for
emitted     (Packet 14)  prior version WEIGHTS     regressions
                                     log commit   in next 10 missions
```

1. **DELIVERY** — receipts emitted (Packet 03).
2. **EVALUATE** — miner computes new weights from the latest 50 missions per lane (Packet 14).
3. **REGRESS** — replay the last 25 missions' routing decisions through the proposed weights; require ≥ 95% of those decisions to produce the same lane as before. Below 95% = reject the update (hold the prior version).
4. **COMMIT** — write `weights/<NEW_VERSION>.json`, symlink `CURRENT.json`, append to `learning_log.jsonl`, bump `WEIGHTS_VERSION`.
5. **ROLLBACK-WATCHDOG** — for the next 10 missions, compare actual `success_rate` to the prior version's. If it drops by > 10%, auto-revert to `parent_version` and emit an F-DEL-02 incident.

## Gates

- **G1 — Regression gate.** No weight update is committed unless the regression test passes (95% decision stability).
- **G2 — Monotonic-improvement gate.** A new version is committed only if its `lane_stats.json` projected scores are equal-or-better than the prior version on a frozen test set.
- **G3 — Rollback-safety gate.** Every commit records `parent_version`. The system can always restore.
- **G4 — Log-immutability gate.** `learning_log.jsonl` is append-only. Corrections create new entries with `supersedes`.
- **G5 — Watchdog gate.** The 10-mission post-commit monitor is mandatory. If auto-revert fires, an incident is recorded in `runs/incidents/`.

## Anti-Patterns

- Updating weights without a regression test (silent drift, no rollback).
- Allowing weights to drift outside [0, 1] without clamping (numerical instability).
- Skipping the watchdog (commits without verification of real-world impact).
- Correlating per-domain weights across unrelated domains (overfitting).
- Using a non-deterministic test set (regression results must be reproducible).

## L2 Evidence

- Determinism test: same 25-mission history, 2 learning runs, identical WEIGHTS_VERSION.
- Regression test: replay frozen 25 missions, 95% decision match required.
- Rollback test: simulate a drop in success_rate, watchdog fires, parent version restored.
- Clamp test: weight cannot go below 0 or above 1.
- Watchdog test: 10 missions with -11% success_rate → auto-revert recorded in incidents.

## Versioning

- **Major bump:** learning rate, decay, regression threshold change.
- **Minor bump:** new scoring component added (e.g. w7), per-domain schema change.
- **Patch:** bug fix with no formula change.

Current version: **1.0.0** (paired with apex-orchestration v1.1.0).
