# 02 — Plan-and-Execute

**Status**: Gap. Not yet implemented in make-it-heavy.

## When it wins

- Multi-step tasks where the *order* matters more than the *next step*
- You need to show the user the plan before acting
- ReAct thrashes because the global structure isn't visible to the LLM
- Partial failure should trigger replanning, not a loop

## When it loses

- Tasks with only 1–3 steps (overhead exceeds value)
- Environments where the plan is invalidated by every observation
- Tool discovery must happen at runtime (plan can't enumerate unknowns)

## The Loop

```
plan = LLM_plan(task)                       # single planner call
state = {plan: plan, results: []}

loop up to max_replans:
  for step in plan:
    result = execute_step(step, state)
    state.results.append(result)
  if LLM_verify(state) == "ok": break
  plan = LLM_replan(state)                  # replan on failure

# Equivalent of mark_task_complete
return synthesize(state)
```

## Integration With `agent.py`

Use a `PlanAgent` wrapper:

```python
class PlanAgent:
    def __init__(self, planner_model, executor: Agent, max_replans=3):
        self.planner = planner_model
        self.executor = executor
        self.max_replans = max_replans

    def run(self, task):
        plan = self.planner.plan(task)              # returns list[Step]
        for _ in range(self.max_replans):
            state = self.executor.run_plan(plan)    # executes each step
            verdict = self.planner.verify(state)
            if verdict.ok:
                return state.synthesize()
            plan = self.planner.replan(state, verdict.feedback)
        raise PlanFailure(state, "max_replans exceeded")
```

Two model choices:
- **Same model for planner and executor** — simpler, cheaper, but planner
  has the same blind spots as the executor.
- **Stronger model as planner, faster as executor** — better plans, cheaper
  execution. Default recommended.

## Prompt Skeleton

```
PLANNER ROLE:
- Decompose the task into 3–7 ordered steps.
- Each step must name the tool it uses, the inputs, and the expected output.
- If a step can fail, add a "verify" step immediately after.
- Do not execute tools. Only plan.

EXECUTOR ROLE:
- Execute the step you are given.
- Surface the full tool output.
- Never skip a step or reorder.

VERIFIER ROLE:
- For each step's output, check: correct? complete? policy-compliant?
- Return: {ok: bool, feedback: str, replan_target: str|null}
```

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Plan is too vague ("look into it") | Planner lacks task knowledge | Feed planner the same context the executor will see |
| Replans every iteration | Verifier is too strict, or tools are flaky | Soften the verifier; stabilize the tool first |
| Planner enumerates tools executor doesn't have | Tool set wasn't shared with planner | Pass tool registry to the planner call |
| Execution drifts from plan | Executor improvises | Tell executor: "do exactly the named step, nothing more" |
