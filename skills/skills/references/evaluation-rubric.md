# Skill Evaluation Rubric

Score each dimension from 0 to 3. A score of 0 means absent or unsafe, 1 means weak, 2 means usable with caveats, and 3 means strong and evidenced.

| Dimension | What to examine |
|---|---|
| Trigger fit | Does the description identify what the skill does and when it should activate without broad keyword bait? |
| Method fit | Does the procedure actually solve the target task with clear steps and decision points? |
| Evidence | Are examples, tests, source links, receipts, or observed outcomes available? |
| Compatibility | Do tools, paths, formats, runtime assumptions, and permissions match the target environment? |
| Maintainability | Is ownership clear, is the body concise, are references separated, and is versioning meaningful? |
| Safety | Are data boundaries, destructive actions, secrets, external content, and approval points handled explicitly? |

Compute a raw score out of 18, but do not reduce safety to arithmetic. Reject a candidate with a safety score below 2 for mutation-capable work, or with any unresolved blocking manifest failure. Choose the strongest coherent skill or composition that covers the complete requested outcome, preserves complementary verified capability, and satisfies evidence, compatibility, and safety requirements. Narrow triggers and least privilege constrain activation and consequences, not the mission's ambition.

## Composition gate

Compose two or more skills only when every member has a distinct purpose, each handoff names its input and output artifact, the order is deterministic or its branch conditions are explicit, failure behavior is defined, and the combined workflow has an acceptance test. If a composition merely concatenates prompts, keep the skills separate.

## Evidence levels

| Level | Evidence |
|---|---|
| A | Reproducible tests and observed successful use in the target runtime |
| B | Reproducible local checks plus representative examples |
| C | Reviewed procedure with plausible examples but no execution evidence |
| D | Unreviewed prose, copied prompt, or registry-only claim |

Use A or B for production routing. Use C only with a review gate. Treat D as a candidate for inspection, never as proof of capability.
