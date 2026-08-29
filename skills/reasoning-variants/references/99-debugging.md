# 99 — Debugging Reasoning Failures

When an agent fails, the failure usually has a *specific* shape. Use this
guide to diagnose it before reaching for a different strategy.

## Diagnostic Questions (Answer in Order)

1. **Did the agent finish, or hit `max_iterations`?**
   - Hit limit → strategy can't converge. See "Looping" below.
   - Finished → output is just wrong. See "Wrong answer" below.

2. **What does the tool-call trace look like?**
   - Same tool called repeatedly with the same args → tool or arg bug.
   - Tool calls are valid but results don't match expectations → tool contract drift.
   - No tool calls at all on a tool-heavy task → tool allowlist or description issue.

3. **What does the prompt actually say?**
   - Read the *full* prompt the model saw, including context. Often the bug
     is in context, not the system prompt.

## Failure Modes

### Looping (agent never finishes)

| Strategy | Likely cause | Fix |
|----------|--------------|-----|
| ReAct | Tool returns same result regardless of args; agent's `thought` is identical each step | Vary the args explicitly; add a "you have called this tool N times" warning |
| Plan-and-Execute | Replan keeps producing the same plan | Verifier feedback is too vague; require replan to change at least one step |
| Reflection | Critic never says "ok" | Rubric has no passing threshold; require N dimensions at score 3 |
| ToT | Beam converges, all branches score the same | Scoring function has no signal; replace with a concrete metric |
| Reflexion | Same critique on every attempt | Feedback isn't reaching the prompt; check `build_context` output |
| Debate | Positions keep oscillating | No shared success criteria; add explicit rubric before round 1 |

### Wrong answer (agent finishes but output is wrong)

| Strategy | Likely cause | Fix |
|----------|--------------|-----|
| ReAct | Model lacks knowledge; tool retrieved wrong data | Add memory retrieval; verify tool output quality |
| Plan-and-Execute | Plan steps are correct in isolation but wrong in sequence | Add a verifier that checks the *joined* output, not per-step |
| Reflection | Critic has the same blind spot as drafter | Use a different model family for the critic |
| ToT | Searched the wrong part of the space | Tighten the expand prompt to focus on the relevant dimension |
| Reflexion | Stored reflections are wrong | Validate evaluator against ground truth before wiring it in |
| Debate | All perspectives have the same blind spot | Force distinct evidence bases per perspective |

### Drifting (agent goes off-task)

| Strategy | Likely cause | Fix |
|----------|--------------|-----|
| ReAct | No anchor to the original task in the prompt | Re-include the task in every iteration's context |
| Plan-and-Execute | Executor improvises beyond the step | Tell executor: "do exactly this step, nothing more" |
| Reflection | Revision introduces new errors | Require the revision to *only* address the critique, not rewrite |
| ToT | Branches diverge into unrelated territory | Bound expansion: "stay within these entities/concepts" |
| Reflexion | Old reflections pull the agent toward a previous (wrong) attempt | Filter reflections: only include ones from attempts that improved the score |
| Debate | One perspective derails the others | Cap cross-critique length; require it to *quote* the original position |

## Before Switching Strategy

The most common mistake is to **switch strategy when the bug is in the
prompt, tool, or context**. Before escalating:

- [ ] Read the full prompt the model saw (including context)
- [ ] Run the agent on a known-good input — does it work there?
- [ ] Check tool outputs by hand — are they what you expected?
- [ ] Confirm the tool allowlist includes everything needed
- [ ] Confirm the system prompt and rubric are present and correct
- [ ] Run 3 attempts — is the failure consistent or flaky?

If all 6 pass and the strategy still fails, *then* escalate. If any fail,
fix that first.

## Receipts

Every failure investigation should produce a record:

- The strategy used
- The exact prompt that failed
- The output (good or bad)
- The fix that worked
- The cost (tokens, time)

Store this in your receipt/audit log. Patterns will emerge.
