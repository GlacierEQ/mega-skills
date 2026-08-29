# 05 — Reflexion (Verbal Reinforcement Learning)

**Status**: Gap. Requires persistent memory (`memory_tiered.py` is built for this).

## When it wins

- Long-horizon tasks where the agent retries after failure
- Failures are *informative* (the next attempt can do better)
- You have a way to detect failure (assertion, schema, critic, user signal)

## When it loses

- Failures are non-actionable ("the model just doesn't know")
- Memory persists across *unrelated* tasks (you want short-term learning, not global)
- One-shot tasks (use Reflection instead — no retry needed)

## The Loop

```
memory = []  # list of (attempt, critique, next_strategy)
for attempt in 0..max_attempts:
  output = Agent.run(task, memory=memory)
  feedback = evaluator(output)                    # can be assertion, critic, or user
  if feedback.ok: return output
  memory.append(Reflection(attempt, output, feedback, "what to do differently"))
  if not progress(memory): raise StuckError(memory)
return best(outputs)  # return best of failed attempts
```

Key distinction from Reflection:
- **Reflection** = critic on the *same* draft, producing a revision
- **Reflexion** = critic across *multiple* attempts, building a verbal memory of what didn't work

Reflexion *requires* the memory to actually be fed back into the next attempt.
Without that, it's just "try again" — which models are bad at.

## Integration With `agent.py` + `memory_tiered.py`

```python
class ReflexionAgent:
    def __init__(self, agent: Agent, evaluator, memory: TieredMemory, max_attempts=5):
        self.agent = agent
        self.evaluator = evaluator
        self.memory = memory
        self.max_attempts = max_attempts

    def run(self, user_id, task):
        for attempt in range(self.max_attempts):
            reflections = self.memory.retrieve(user_id, f"reflexion {task}", tiers=("ltm", "entity"))
            context = self.memory.build_context(user_id, task, token_budget=800)
            output = self.agent.run(task, context=context)
            feedback = self.evaluator(output)
            if feedback.ok:
                self.memory.store_long_term(user_id, f"reflexion success: {task[:80]}")
                return output
            self.memory.upsert_entity(user_id, "reflexion", f"task:{task[:40]}", feedback.summary, confidence=0.7)
        return output  # return best-effort last attempt
```

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Memory grows unbounded across attempts | high | Cap the LTM reflections per `task`; decay after 7 days. |
| Same failure repeated each attempt | high | **Detect non-progress** — if last 2 critiques are near-identical, raise `StuckError` instead of looping. |
| Memory from one task contaminates another | critical | **Scope by `user_id` and by `task` slug.** Never share reflections across users or unrelated tasks. |
| Evaluator itself is wrong | critical | **Validate the evaluator first** on a held-out set before wiring it into the loop. |
| Self-critique spirals into self-doubt | medium | Cap attempts; require monotonically improving evaluator scores. |

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Each attempt repeats the same mistake | Reflections not reaching the model | Check that `build_context` actually includes them; log the prompt. |
| Memory fills with low-quality critiques | No curation on storage | Store only critiques that change behavior; rate-limit writes. |
| Success on attempt 5 but the early attempts should have worked | Evaluator is noisy | Stabilize the evaluator or require N consecutive passes. |
| Cross-task contamination | Reflections keyed on user_id only | Add a `task_slug` to the entity key. |
