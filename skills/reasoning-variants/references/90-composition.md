# 90 — Composing Strategies

Single strategies solve single problems. Real systems compose them. Below are
patterns that work.

## Common Compositions

### Plan + ReAct (most common in production)

Planner decomposes → ReAct executor runs each step.

```
plan = LLM_plan(task)
for step in plan:
    output = ReActAgent.run(step)   # one ReAct loop per step
    if evaluator(output).fail: plan = LLM_replan(state)
```

Used in: `make-it-heavy/genius_orchestration.py`-style systems.

### Plan + ReAct + Reflection

For high-quality multi-step output: plan, execute each step with ReAct,
reflect on the joined output.

```
plan = LLM_plan(task)
parts = [ReActAgent.run(step) for step in plan]
draft = join(parts)
final = reflect(draft, rubric)
```

### Tree-of-Thoughts + Debate

For hard strategic questions: explore paths (ToT), then defend the best
candidates against each other (Debate).

```
paths = ToT.explore(task, beam=3, depth=4)
candidates = [executor.run(p) for p in top_k(paths, k=2)]
verdict = debate(candidates, roles=["supporting", "critiquing"])
```

### Reflexion + Plan-and-Execute

When the plan can fail and the failure is informative.

```
for attempt in range(max):
    plan = LLM_plan(task, memory=reflections)
    output = ReActAgent.run(plan)
    if evaluator(output).ok: return output
    reflections.append(critique(output, evaluator))
```

### Debate + Reflection

For contested, high-quality output: argue it out, then reflect on the verdict.

```
verdict = debate(task, perspectives)
final = reflect(verdict, rubric="is this verdict well-grounded?")
```

## Anti-Compositions

These don't work. Don't try.

- **ToT + Reflexion** — two memory-heavy strategies; cost is multiplicative,
  signal is not.
- **Debate + Plan-and-Execute (on tool tasks)** — debate's strength is text
  reasoning, not tool orchestration. ReAct + Reflection wins.
- **Reflection + Reflection (nested)** — passes the same blind spot
  around; cap at one critic pass.
- **ToT with beam=1** — that's just beam search with extra steps. Use beam ≥ 3.

## Cost Discipline

Each composition multiplies token cost. Before composing, ask:

1. **What's the budget?** Per-task, per-day, per-user.
2. **What's the failure mode if I don't compose?** If the simple strategy's
   failure is recoverable downstream, don't compose.
3. **Can I measure the gain?** Run A/B: simple strategy vs composed. If
   composed doesn't measurably improve the rubric, revert.

Default: **start with ReAct + Reflection** (the cheapest composition that
adds quality). Add ToT, Debate, Reflexion only when the simpler composition
is observably failing on a specific failure class.
