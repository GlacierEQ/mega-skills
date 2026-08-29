# 03 — Reflection / Self-Critique

**Status**: Gap. Implementable today by adding a second LLM call after `Agent.run()`.

## When it wins

- Quality-sensitive output: writing, code, analysis, legal-style text
- A second pass catches errors the first pass missed
- Cheap to add (one extra LLM call) and high upside

## When it loses

- Output is verified objectively (unit test, schema check) — use that instead
- Reflection is ungrounded (model just praises itself) — no rubric = no value
- Latency budget is tight (doubles time-to-answer)

## The Loop

```
draft = Agent.run(task)
for up to max_reflection_passes:
  verdict = critic(draft, rubric)
  if verdict.ok: break
  draft = Agent.run_revision(task, draft, verdict.feedback)
return draft
```

Two variants:

1. **Same-model self-reflection** — quick, cheap, but the model has the same
   blind spots on both passes.
2. **Critic model** — a separate LLM (often a smaller/faster one) scores the
   draft against a rubric. More reliable, more expensive.

Default: critic model with a concrete rubric. Never use bare "reflect on your
answer" prompts.

## Integration With `agent.py`

```python
def run_with_reflection(task, rubric, max_passes=3):
    draft = agent.run(task)
    for _ in range(max_passes):
        verdict = critic.score(draft, rubric)
        if verdict.ok:
            return draft
        draft = agent.run(f"Revise per critic. Task: {task}\nDraft: {draft}\nFeedback: {verdict.feedback}")
    return draft  # return best-effort; don't loop forever
```

## Rubric Template

```
Score the draft on:
1. Correctness   — are the claims true and supported?
2. Completeness  — does it answer every part of the task?
3. Format        — does it follow the required output shape?
4. Policy        — does it violate any rule (no secrets, no invented citations, …)?
5. Conciseness   — is it as short as it can be while still complete?

For each dimension: 0–3 (0=fails, 3=excellent).
Return: {ok: bool, scores: {...}, feedback: str, top_fix: str}
```

## Debugging

| Symptom | Cause | Fix |
|---------|-------|-----|
| Reflection passes but draft doesn't change | Critic feedback is non-actionable ("looks good") | Force feedback to start with a verb and name a specific change |
| Reflection makes it worse | Model overthinks simple answers | Limit to 1 pass for short outputs; only loop on outputs >500 tokens |
| Critic and drafter have same blind spot | Same model for both | Use a different model family for the critic |
| Reflection loops forever | No `ok` threshold on the rubric | Require ≥4/5 dimensions at score 3 to call it done |
