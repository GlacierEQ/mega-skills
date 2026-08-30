# 04 — Tree-of-Thoughts (ToT)

**Status**: Gap. Expensive. Use only when cheaper strategies fail measurably.

## When it wins

- Hard reasoning puzzles with multiple plausible approaches
- The problem space has clear intermediate states that can be *scored*
- You can afford N×L token cost for the quality gain
- Classic examples: 24-game, math olympiad, multi-step planning under constraints

## When it loses

- Tool-heavy tasks (use Plan-and-Execute instead)
- No good scoring function (ToT degrades to blind search)
- Cheap tasks where ReAct would solve it in 3 calls
- Real-time / latency-sensitive workloads

## The Loop

```
state = initial_state(task)
for depth in 0..max_depth:
  candidates = []
  for each leaf in active_branches:
    branches = LLM_expand(leaf, beam=b)            # b candidates per leaf
    scored  = [(score(branch), branch) for branch in branches]
    candidates.extend(scored)
  active_branches = top_k(candidates, k=beam)      # prune to beam width
  if any(branch.is_terminal() and score > threshold): return best
return best_branch
```

Parameters:
- `beam` (b) — how many candidates to expand per node (default 3)
- `max_depth` — how deep to search (default 4)
- `k` — how many top branches to keep at each level (default `beam`)
- `score_fn` — what evaluates a candidate (LLM, heuristic, or unit test)

## Integration With `agent.py`

```python
class TreeOfThoughtsAgent:
    def __init__(self, expand_model, score_model, executor: Agent, beam=3, max_depth=4):
        self.expand = expand_model
        self.score  = score_model
        self.executor = executor
        self.beam = beam
        self.max_depth = max_depth

    def run(self, task):
        leaves = [InitialState(task)]
        for depth in range(self.max_depth):
            expansions = []
            for leaf in leaves:
                expansions.extend(self.expand(leaf, n=self.beam))
            scored = [(self.score(b), b) for b in expansions]
            leaves = [b for _, b in sorted(scored, reverse=True)[:self.beam]]
            if self.has_terminal_solution(leaves):
                return self.executor.run(best(leaves))
        return self.executor.run(best(leaves))
```

The scoring function is the make-or-break. Options:
- **LLM-as-judge** — flexible, but biased; calibrate against ground truth
- **Heuristic** — fast, e.g. regex match, length penalty, keyword presence
- **External check** — unit test, schema validator, simulator. Best when available.

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| No good scoring function | critical | **Stop.** ToT without a score is random search. Use ReAct or Plan-and-Execute instead. |
| `beam × max_depth` exceeds budget silently | high | **Hard cap total calls**: `beam^max_depth ≤ 81` (3^4) is the safe upper bound. |
| Branches all converge to same answer | medium | Increase diversity in the expand prompt: "Consider approaches that differ in the first move." |
| Score model rewards verbosity | medium | Normalize: `score = quality - 0.1 * tokens`. |
| Tool execution per branch is expensive | high | **Score before executing.** Only run tools on the top-k final branches. |

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| All branches score the same | Scoring function has no signal | Replace LLM judge with a concrete metric |
| Best branch is a low-quality "obvious" answer | `beam=1` (no exploration) | Raise beam to 3–5 |
| Search never terminates | `max_depth` too high, no terminal check | Add terminal-state detection after each expansion |
| Cost is 10× the budget | Scoring per branch is too expensive | Score less often; prune early |
