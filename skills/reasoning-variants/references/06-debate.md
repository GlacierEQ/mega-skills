# 06 — Debate / Multi-Perspective

**Status**: Partial. `make-it-heavy/orchestrator.py` already runs parallel workers
(this is the *infrastructure*). Debate is the *protocol* on top.

## When it wins

- Contested questions (legal, ethical, strategic)
- Where the answer depends on which evidence you weight
- When a single model's blind spot is the failure mode
- Calibration: you want a *defended* answer, not just any answer

## When it loses

- The question has a single right answer (debate wastes tokens)
- The perspectives would all be identical (no diversity, no debate)
- Latency budget can't afford N parallel agents
- Tool execution is the bottleneck (debate is mostly text)

## The Loop

```
perspectives = define_perspectives(task)        # 2–4 distinct roles
positions = parallel([
    Agent(role=role, task=task).run()
    for role in perspectives
])
critiques = parallel([
    cross_critique(role=role, positions=positions)
    for role in perspectives
])
rebuttals = parallel([
    Agent(role=role, task=task, context=critiques).run()
    for role in perspectives
])
verdict = judge(rebuttals, criteria)             # final adjudication
```

Variants:
- **Single-round** (above) — one initial, one critique, one rebuttal
- **Multi-round** — loop rebuttals up to N times until convergence
- **Adversarial** — one "prosecutor", one "defender", one "judge"

## Integration With `make-it-heavy`

```python
from orchestrator import TaskOrchestrator
from agent import Agent

def run_debate(task, perspectives, max_rounds=2):
    orchestrator = TaskOrchestrator()
    positions = orchestrator.fan_out([
        {"role": role, "task": task, "agent_id": f"debate-{role}-pos"}
        for role in perspectives
    ])
    for _ in range(max_rounds):
        critiques = orchestrator.fan_out([
            {"role": role, "task": f"Critique these positions: {positions}",
             "agent_id": f"debate-{role}-crit"}
            for role in perspectives
        ])
        positions = orchestrator.fan_out([
            {"role": role, "task": f"Rebut these critiques: {critiques}",
             "agent_id": f"debate-{role}-rebut"}
            for role in perspectives
        ])
    return judge(positions, criteria=CRITERIA)
```

The orchestrator's existing parallel-fan-out does the heavy lifting. Debate
just adds the cross-critique and rebuttal passes.

## Perspective Design (Make-or-Break)

Perspectives must be **substantively different**, not cosmetic. Good
perspectives disagree on *evidence weighting*, not just tone.

| Domain | Three good perspectives |
|--------|-------------------------|
| Legal motion | "statute-textualist" / "policy-pragmatist" / "precedent-historian" |
| Code review | "correctness" / "performance" / "maintainability" |
| Product decision | "user-advocate" / "engineering-feasibility" / "business-impact" |
| Bug investigation | "first-cause" / "load-induced" / "configuration-error" |

Bad: "optimist" / "pessimist" / "neutral" — these are moods, not viewpoints.

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| All perspectives converge to the same answer | Perspectives are not differentiated | Use concrete evidence bases or success criteria per role |
| Judge just averages the positions | Judge has no criteria | Require ranked criteria (e.g. "correctness > cost > style") |
| Debate takes 6× the time of a single agent | 4 perspectives × 2 rounds + judge | Reduce to 2 perspectives or 1 round for latency-sensitive paths |
| One perspective is wrong and dominates | Judge weighs positions unevenly | Use blind judging (judge doesn't know which role wrote which position) |
| Critics attack strawmen | Cross-critique prompt is lazy | Require: "Quote the position you are critiquing, then identify its weakest claim." |

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Outputs are near-identical | Same model + same prompt | Use different model families OR very different system prompts |
| Debate never converges | No shared success criteria | Add explicit shared rubric before the debate starts |
| Judge picks the longest answer | Verbosity bias | Normalize: judge sees truncated/anonymized positions |
| One perspective is always overruled | Role is poorly defined | Strengthen its evidence base; don't fight the judge |
