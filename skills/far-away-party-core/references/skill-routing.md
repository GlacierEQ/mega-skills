# Skill Routing and Handoff Guide

Far Away Party is an orchestration framework. Use it to choose, sequence, and integrate specialist skills; do not use it as a substitute for the detailed method owned by a domain skill.

## Routing sequence

1. Identify the **dominant deliverable**: research report, financial analysis, software product, data workbook, slide deck, document, media asset, automation, transaction, or operational change.
2. Select the **primary skill** that has the most specific required procedure for that deliverable.
3. Add a complementary skill only when it contributes a distinct required capability, constraint, or validation method.
4. Convert each cross-skill boundary into an artifact contract: required input, format, owner, validation, and destination.
5. Place the primary skill’s mandatory sequence inside the applicable Far Away Party phase. Retain its required gates.

## Composition patterns

| Mission shape | Primary responsibility | Typical complementary responsibility | Integration artifact |
|---|---|---|---|
| Research-backed report | Research and technical writing | Data analysis, citation management, visual evidence | Evidence register and final claims trace |
| Financial or company analysis | Finance workflow | Data extraction, spreadsheet production, report writing | Period-consistent model and source register |
| Website or application | Web or mobile development | Product framing, design assets, testing, deployment | Requirements matrix, implementation plan, tested release |
| Automation or agent workflow | Automation and scheduling | API or connector configuration, persistent computing, data validation | Trigger map, idempotency plan, monitoring evidence |
| Presentation | Slide content planning and generation | Research, visual assets, data visualization | Slide outline, source list, exported deck QA |
| Visual or media deliverable | Image, video, audio, or music generation | Brand or content planning, rendered-output review | Prompt/source ledger and inspected final asset |
| High-complexity operational task | Domain-specific operational procedure | Compliance, stakeholder communication, verification | Approval record, action log, post-condition evidence |

This table illustrates capability boundaries rather than automatic skill requirements. Route only what is relevant to the mission.

## Handoff contract

Every transition between skills must specify the following in the roadmap or work packet:

| Element | Required question |
|---|---|
| Input contract | Which canonical artifact, source IDs, decisions, and constraints must the receiving skill use? |
| Output contract | What exact artifact, format, fields, location, and quality bar will it produce? |
| Ownership | Who resolves defects, missing inputs, and ambiguous requirements? |
| Validation | How will the integrator verify that the output is fit for the next skill? |
| State update | Which decision, evidence, risk, or completion status must be written before the handoff closes? |

Do not hand off implicit knowledge, raw conversational history, or an unexplained conclusion. Encode the required information in the relevant durable-state file or work packet.

## Conflict resolution

Apply this order when instructions compete:

1. Mandatory platform, safety, legal, privacy, or user-approval requirements.
2. Explicit user instructions relevant to the current mission.
3. The specialist skill whose domain directly governs the action or output.
4. Another directly relevant specialist skill, limited to its own domain.
5. Far Away Party’s coordination and state-management guidance.
6. General stylistic preferences.

When two domain procedures materially conflict, pause the affected work, explain the conflict in `CONTEXT.md`, seek the narrowest clarifying decision, and revise the mission or roadmap before proceeding.

## Token-efficient composition

Keep the active context lean by loading the primary skill, the current context capsule, and only the one complementary reference needed for the active chunk. Preserve outcomes as evidence pointers and decision summaries rather than reproducing lengthy source material. Use specialization to reduce search or implementation uncertainty, not to create multiple redundant treatments of the same task.

## Quality ownership

The primary skill owns **local quality** within its domain. Far Away Party owns **system quality**: complete requirements traceability, cross-artifact consistency, recovery readiness, decision visibility, and final integration. No deliverable is final until both local and system quality have passed their stated checks.
