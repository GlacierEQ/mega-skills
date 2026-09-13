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
- Tool allowlist — keep it task-relevant and complete; remove only irrelevant or unauthorized tools, not mission-relevant capability

## Compact Transport Prompt Variant

This is a transport-efficient prompt, not a capability ceiling. Expand the prompt with task-specific constraints, evidence requirements, and verification whenever the mission needs them.

```
You will solve the task step by step using available tools.

For each step:
1. Reason about what to do next and preserve material rationale.
2. Call the tool that advances the mission with the strongest available evidence.
3. Observe and record the result.
4. Continue until the requested capability is complete and verified.

Never invent tool outputs. If a tool fails, surface the error, preserve the evidence,
and choose the strongest justified recovery path. Use a narrower diagnostic step only
when it improves fault isolation; do not turn local narrowing into mission reduction.
```

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Loops forever on same tool | Tool returns same result regardless of args | Check tool determinism; vary the args explicitly |
| Picks wrong tool early | Tool descriptions are vague | Write complete tool specs (name, when-to-use, when-NOT-to-use, schema, example) |
| Skips steps and jumps to "done" | `max_iterations` is read as "soft target" | Treat as hard cap; check tool output count |
| Calls tools not in allowlist | Allowlist not enforced at prompt level | Add to system prompt: "Only call tools in: {list}" |
