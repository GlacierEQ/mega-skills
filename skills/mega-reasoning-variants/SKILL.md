---
name: mega-reasoning-variants
description: "Reasoning Variants"
---



# MEGA-REASONING-VARIANTS

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Reasoning Variants

The same task can be solved by very different reasoning loops. Picking the wrong
one causes loops, drift, hallucination cascades, or wasted tokens. This skill is
a catalog + selector.

**Load `ai-agents-architect` first** for the broader agent-design context.

## Selector (Decision Tree)

Walk top-to-bottom. Stop at the first match.

```
Is the task well-defined with a clear right answer?
  └─ Yes, and tools are central → ReAct                          (strategy 1)
  └─ Yes, but the path is long (5+ steps) → Plan-and-Execute    (strategy 2)
  └─ No, output quality is paramount → Reflection               (strategy 3)

Are there multiple plausible approaches and the cost of being wrong is high?
  └─ Yes, and you can score candidates → Tree-of-Thoughts        (strategy 4)
  └─ Yes, and past attempts inform future ones → Reflexion       (strategy 5)

Is the answer contested or does it require weighing evidence?
  └─ Yes → Debate / Multi-Perspective                            (strategy 6)

Don't know?
  └─ Start with ReAct. If it loops or diverges, escalate to Plan-and-Execute
     or Reflection. Add the others only when the simpler one is observably failing.
```

## The Six Strategies

| # | Strategy | When to use | Cost |
|---|----------|-------------|------|
| 1 | **ReAct** | Tool-heavy, short horizon, clear stop condition | Low (1 LLM call per step) |
| 2 | **Plan-and-Execute** | Multi-step tasks, replanning on partial failure | Medium (planner + executor) |
| 3 | **Reflection** | Quality-sensitive output (writing, code, analysis) | Medium (1 critic pass) |
| 4 | **Tree-of-Thoughts** | Hard reasoning, multiple candidate paths | High (N parallel branches) |
| 5 | **Reflexion** | Long-horizon tasks that benefit from verbal memory | High (LLM-judged retry) |
| 6 | **Debate** | Contested/evidence-heavy questions | High (M parallel agents) |

## Per-Strategy References

Each strategy has a file in `references/`:

- `references/01-react.md` — the baseline (matches `agent.py` exactly)
- `references/02-plan-and-execute.md`
- `references/03-reflection.md`
- `references/04-tree-of-thoughts.md`
- `references/05-reflexion.md`
- `references/06-debate.md`
- `references/90-composition.md` — how to combine strategies
- `references/99-debugging.md` — when each one fails and how to fix it

## Integration With `make-it-heavy`

All six strategies are designed to plug into the existing `agent.py` shape:

- The `Agent` class accepts a `system_prompt`; the strategy-specific prompt is
  prepended/appended there.
- Tool calls still go through the existing tool registry (no tool changes).
- `mark_task_complete` remains the only "I'm done" signal; strategies route
  through it.
- `max_iterations` still applies, but its meaning changes per strategy
  (see per-strategy references for the new semantics).
- `agent_id` should encode the strategy: `react-…`, `plan-…`, `reflect-…`.

The pattern:

```python
from agent import Agent
from strategies import build_strategy_prompt, build_strategy_runner

prompt = build_strategy_prompt("plan-and-execute", task)
runner = build_strategy_runner("plan-and-execute")
agent = Agent(system_prompt=prompt, tool_policy=tools, agent_id="plan-001")
runner(agent, task)
```

## Hard Rules (Apply to Every Strategy)

1. **`max_iterations` is mandatory.** Different defaults per strategy:
   - ReAct: 10
   - Plan-and-Execute: outer 3 replans × inner 10 steps = 30 effective
   - Reflection: 3 (one per critic pass)
   - Tree-of-Thoughts: depth 4 × breadth 3 = 12 leaf evaluations
   - Reflexion: 5 (one per memory-augmented attempt)
   - Debate: 2 (one round, one rebuttal)

2. **No strategy without a stop signal.** Every loop must end on either
   `mark_task_complete`, a hard error, or `max_iterations`. Never spin on
   "almost done" heuristics.

3. **All tool calls are policy-bound.** Strategies don't bypass the tool
   allowlist; they route *through* it.

4. **Receipts/audit for every state change.** Plan steps, critic verdicts,
   branch evaluations — append to the audit log, don't just print.

5. **The simpler strategy is the right one until proven otherwise.**
   Don't reach for Tree-of-Thoughts when ReAct works. Strategy escalation
   requires evidence of failure, not intuition.

## Anti-Patterns

### ❌ Strategy shopping
"ReAct didn't work, let me try Reflexion." → Diagnose the failure first
(see `references/99-debugging.md`). Most ReAct failures are bad tool
descriptions or missing context, not the wrong loop.

### ❌ Tree-of-Thoughts on cheap tasks
ToT costs N×L tokens. Use it only when the per-call savings outweigh the
fan-out cost. For "what's 2+2", ReAct wins.

### ❌ Reflection without a critic rubric
"Reflect on your answer" produces vague self-praise. Use a concrete rubric
(correctness, completeness, format, policy) and score against it.

### ❌ Reflexion without memory persistence
Reflexion only works if the verbal self-critique is stored and fed back on
the next attempt. One-shot reflection is just Reflection.

### ❌ Debate without role differentiation
Two identical agents arguing is wasted tokens. Give them distinct roles,
evidence bases, or success criteria.

## When to Update This File

- New strategy emerges with strong empirical results → add to catalog.
- A strategy's loop template changes materially → update its reference.
- A new debugging case is documented → add to `references/99-debugging.md`.
