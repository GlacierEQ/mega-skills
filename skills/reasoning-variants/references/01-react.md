# 01 — ReAct (Reason + Act)

**Status**: Baseline. The make-it-heavy `agent.py` IS this strategy.

## When it wins

- Tool-heavy, short-horizon tasks
- Clear stop condition (`mark_task_complete`)
- Steps are roughly sequential, each depending on the previous

## When it loses

- Task needs a global plan (ReAct reconsiders every step → thrashing)
- Output quality matters more than tool accuracy (no built-in critic)
- Many independent candidate paths exist (use ToT)

## The Loop

```
loop up to max_iterations:
  thought    = LLM("Given state, what next?")
  action     = parse(thought) -> tool_name + args
  observation = execute(action)
  state     += (thought, action, observation)
  if action == "mark_task_complete": break
```

## Integration With `agent.py`

Already implemented. The `Agent.run()` method is exactly this loop.
You tune it by:

- `system_prompt` — strategy-specific preamble
- `max_iterations` — default 10; raise to 20 for complex tool chains
- Tool allowlist — keep tight; ReAct picks worse when overloaded

## Minimal Prompt Variant

```
You will solve the task step by step using available tools.

For each step:
1. Reason briefly about what to do next.
2. Call exactly one tool.
3. Observe the result.
4. Continue until you can call mark_task_complete.

Never invent tool outputs. If a tool fails, surface the error and choose
a different tool or a smaller step.
```

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Loops forever on same tool | Tool returns same result regardless of args | Check tool determinism; vary the args explicitly |
| Picks wrong tool early | Tool descriptions are vague | Write complete tool specs (name, when-to-use, when-NOT-to-use, schema, example) |
| Skips steps and jumps to "done" | `max_iterations` is read as "soft target" | Treat as hard cap; check tool output count |
| Calls tools not in allowlist | Allowlist not enforced at prompt level | Add to system prompt: "Only call tools in: {list}" |
